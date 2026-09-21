"""
Lightweight PointNav inference — no Habitat dependency.

Loads a Habitat checkpoint and runs discrete-action PointNav inference
(depth + target → action).  Verified against depth-only model (ckpt.99).

Usage:
    agent = PointNavAgent("model_depth_only.pt")
    agent.reset()
    action = agent.act(depth_array, (dx, dy, dtheta))
    lin_x, ang_z = agent.action_to_twist(action)
"""

from __future__ import annotations
from collections import OrderedDict
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ── ResNet18 backbone (matched to Habitat-Baselines) ──────────────────────

class _BasicBlock(nn.Module):
    """ResNet BasicBlock (BatchNorm variant, no expansion)."""

    def __init__(self, in_c: int, out_c: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_c, out_c, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_c)
        self.conv2 = nn.Conv2d(out_c, out_c, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_c)
        self.downsample: "nn.Module | None" = None
        if stride != 1 or in_c != out_c:
            self.downsample = nn.Sequential(OrderedDict([
                ("0", nn.Conv2d(in_c, out_c, 1, stride=stride, bias=False)),
                ("1", nn.BatchNorm2d(out_c)),
            ]))
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        return self.relu(out)


class _ResNet18Backbone(nn.Module):
    """ResNet-18, single-channel input, no initial max-pool."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Sequential(OrderedDict([
            ("0", nn.Conv2d(1, 32, 7, stride=2, padding=3, bias=False)),
            ("1", nn.BatchNorm2d(32)),
        ]))
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = nn.Sequential(_BasicBlock(32, 32), _BasicBlock(32, 32))
        self.layer2 = nn.Sequential(_BasicBlock(32, 64, stride=2), _BasicBlock(64, 64))
        self.layer3 = nn.Sequential(_BasicBlock(64, 128, stride=2), _BasicBlock(128, 128))
        self.layer4 = nn.Sequential(_BasicBlock(128, 256, stride=2), _BasicBlock(256, 256))

    def forward(self, x):
        x = self.relu(self.conv1(x))     # 256→128 (stride 2)
        x = self.maxpool(x)              # 128→64  (stride 2)
        x = self.layer1(x)               # 64→64
        x = self.layer2(x)               # 64→32 (stride 2)
        x = self.layer3(x)               # 32→16 (stride 2)
        x = self.layer4(x)               # 16→8  (stride 2)
        return x                          # (B, 256, 8, 8)


# ── Full policy ───────────────────────────────────────────────────────────

class PointNavPolicy(nn.Module):
    """
    PointNav policy: ResNet18(1-ch) + GRU(3-layer, 512).

    Input:
        depth       (B, C, 256, 256)  float32  [0, 1] (C=1 depth-only, C=4 RGBD)
        target      (B, 3)            float32  (dx, dy, dtheta)
        prev_action (B,)              int64    [0, 4)
        rnn_hidden  (3, B, 512)       float32
        masks       (B, 1)            float32  0=reset, 1=continue

    Output:
        action_logits  (B, 4)
        rnn_hidden     (3, B, 512)
    """

    def __init__(self, in_channels: int = 1):
        super().__init__()
        self.in_channels = in_channels
        self.backbone = _ResNet18Backbone()                      # → (B, 256, 16, 16)
        # Override conv1 for correct input channels
        if in_channels != 1:
            self.backbone.conv1[0] = nn.Conv2d(
                in_channels, 32, 7, stride=2, padding=3, bias=False)

        self.compression = nn.Sequential(OrderedDict([
            ("0", nn.Conv2d(256, 128, 3, stride=1, padding=1, bias=False)),
            ("1", nn.BatchNorm2d(128)),
        ]))                                                       # → (B, 128, 16, 16)

        # visual_fc: AdaptiveAvgPool2d + Flatten → Linear(2048→512)
        # Habitat wraps pool+flatten in a nested Sequential at index 0
        self.visual_fc = nn.Sequential(OrderedDict([
            ("0", nn.Sequential(
                nn.AdaptiveAvgPool2d((4, 4)),                      # → (B, 128, 4, 4)
                nn.Flatten(),                                       # → (B, 2048)
            )),
            ("1", nn.Linear(2048, 512)),                           # → (B, 512)
        ]))

        self.tgt_embedding = nn.Linear(3, 32)
        self.prev_action_embedding = nn.Embedding(5, 32)

        # GRU: 512 (visual) + 32 (tgt) + 32 (prev_action) = 576
        self.rnn = nn.GRU(576, 512, num_layers=3)

        # Action head: 512 → 4
        self.action_head = nn.Linear(512, 4)

    @property
    def num_recurrent_layers(self):
        return 3

    def forward(self, depth, target, prev_action, rnn_hidden, masks):
        x = self.backbone(depth)                           # (B, 256, 16, 16)
        x = F.relu(self.compression(x))                    # (B, 128, 16, 16)
        x = self.visual_fc(x)                              # (B, 512)

        g = F.relu(self.tgt_embedding(target))             # (B, 32)
        a = self.prev_action_embedding(prev_action)        # (B, 32)

        x = torch.cat([x, g, a], dim=1)                    # (B, 576)
        x, h = self.rnn(x.unsqueeze(0), rnn_hidden * masks.unsqueeze(0))
        return self.action_head(x.squeeze(0)), h


# ── Key remapping ────────────────────────────────────────────────────────

# Habitat BasicBlock uses a Sequential named "convs":
#   [0] conv1, [1] bn1, [2] ReLU, [3] conv2, [4] bn2
_CONVS_MAP = {
    "convs.0": "conv1",
    "convs.1": "bn1",
    "convs.3": "conv2",
    "convs.4": "bn2",
}

_SKIP_KEYS = {
    "net.critic.fc.weight", "net.critic.fc.bias",
}


def _remap_key(key: str) -> str | None:
    """Convert a Habitat checkpoint key to our module key.

    Returns None for keys that should be skipped (e.g. critic).
    """
    if key in _SKIP_KEYS:
        return None

    k = key

    # Strip leading namespace
    k = k.removeprefix("net.")

    # Fix Habitat typo
    k = k.replace("tgt_embeding.", "tgt_embedding.")

    # Flatten visual_encoder (which wraps backbone + compression)
    k = k.replace("visual_encoder.", "")

    # Rename other sub-modules
    k = k.replace("state_encoder.rnn.", "rnn.")
    k = k.replace("action_distribution.linear.", "action_head.")

    # Remap backbone BasicBlock convs numbering
    for old, new in _CONVS_MAP.items():
        k = k.replace(old, new)

    return k


# ── High-level agent wrapper ──────────────────────────────────────────────

class PointNavAgent:
    """Stateful agent for interactive deployment."""

    ACTION_NAMES = ["STOP", "FORWARD", "TURN_LEFT", "TURN_RIGHT"]

    def __init__(self, model_path: str, device: str = "cpu"):
        self.device = torch.device(device)
        ckpt = torch.load(model_path, map_location=self.device,
                          weights_only=False)
        sd = ckpt["state_dict"]

        # Remap Habitat keys to our module keys
        renamed = OrderedDict()
        for key, value in sd.items():
            new_key = _remap_key(key)
            if new_key is not None:
                renamed[new_key] = value

        in_ch = ckpt.get('in_channels', 1)
        self.model = PointNavPolicy(in_channels=in_ch).to(self.device)
        missing, unexpected = self.model.load_state_dict(renamed, strict=False)
        if missing:
            print(f"[WARN] Missing keys: {len(missing)}", flush=True)
        if unexpected:
            print(f"[WARN] Unexpected keys: {len(unexpected)}", flush=True)
        self.model.eval()

        self.hidden_size = 512
        self.num_recurrent_layers = ckpt.get("num_recurrent_layers", 3)
        self.depth_shape = tuple(ckpt.get("depth_shape", [256, 256]))
        self.depth_max = ckpt.get("depth_max", 10.0)
        self._hidden: torch.Tensor | None = None
        self._prev_action: int = 0

    def reset(self):
        """Reset hidden state for a new episode."""
        self._hidden = torch.zeros(
            self.num_recurrent_layers, 1, self.hidden_size,
            device=self.device)
        self._prev_action = 0

    def act(self, depth_np: np.ndarray,
            target: tuple[float, float, float]) -> int:
        """
        Run one inference step.

        Args:
            depth_np: (1, H, W) float32 [0, 1], normalised depth.
            target: (dx, dy, dtheta) relative to agent frame.

        Returns:
            action index: 0=stop, 1=forward, 2=turn_left, 3=turn_right.
        """
        if self._hidden is None:
            self.reset()

        depth = torch.from_numpy(depth_np).unsqueeze(0).to(self.device)
        tgt = torch.tensor([target], dtype=torch.float32, device=self.device)
        prev = torch.tensor([self._prev_action], dtype=torch.long,
                            device=self.device)
        mask = torch.ones(1, 1, device=self.device)

        with torch.no_grad():
            logits, self._hidden = self.model(
                depth, tgt, prev, self._hidden, mask)

        action = int(logits.argmax(dim=1).item())
        self._prev_action = action
        return action

    @staticmethod
    def action_to_twist(action: int) -> tuple[float, float]:
        """Discrete action → (linear_x, angular_z)."""
        return {
            0: (0.0, 0.0),      # STOP
            1: (0.22, 0.0),     # FORWARD (TB3 Burger max: 0.22 m/s)
            2: (0.0, 0.5),      # TURN_LEFT
            3: (0.0, -0.5),     # TURN_RIGHT
        }.get(action, (0.0, 0.0))
