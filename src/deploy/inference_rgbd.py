"""
Standalone RGBD PointNav inference (4-channel input: RGB + Depth).
No Habitat dependency.  Matches Week 4 Gazebo architecture.
"""
import numpy as np
import torch
import torch.nn as nn


class RunningMeanAndVar(nn.Module):
    """Per-channel input normalisation (from Habitat training)."""
    def __init__(self, n_channels):
        super().__init__()
        self.register_buffer("_mean", torch.zeros(1, n_channels, 1, 1))
        self.register_buffer("_var", torch.zeros(1, n_channels, 1, 1))
        self.register_buffer("_count", torch.zeros(()))

    def forward(self, x):
        inv_stdev = torch.rsqrt(torch.max(self._var,
                                          torch.full_like(self._var, 1e-2)))
        return torch.addcmul(-self._mean * inv_stdev, x, inv_stdev)


class ResNet18EncoderRGBD(nn.Module):
    """ResNet18 for 4-channel RGBD input (matches RGBD training)."""
    def __init__(self):
        super().__init__()
        from torchvision.models.resnet import BasicBlock
        self._norm_layer = nn.BatchNorm2d
        self.conv1 = nn.Conv2d(4, 32, 7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(32)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(BasicBlock, 32, 32, 2, stride=1)
        self.layer2 = self._make_layer(BasicBlock, 32, 64, 2, stride=2)
        self.layer3 = self._make_layer(BasicBlock, 64, 128, 2, stride=2)
        self.layer4 = self._make_layer(BasicBlock, 128, 256, 2, stride=2)
        self.compression = nn.Sequential(
            nn.Conv2d(256, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
        )
        self.avgpool = nn.AdaptiveAvgPool2d((4, 4))
        self.running_mean_and_var = RunningMeanAndVar(4)

    def _make_layer(self, block, inplanes, planes, blocks, stride):
        layers = [block(inplanes, planes, stride, downsample=nn.Sequential(
            nn.Conv2d(inplanes, planes * block.expansion, 1, stride, bias=False),
            nn.BatchNorm2d(planes * block.expansion)))]
        for _ in range(1, blocks):
            layers.append(block(planes, planes))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.running_mean_and_var(x)
        x = self.conv1(x); x = self.bn1(x); x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x); x = self.layer2(x)
        x = self.layer3(x); x = self.layer4(x)
        if x.shape[-1] > 4:
            x = self.compression(x)
        x = self.avgpool(x)
        return torch.flatten(x, 1)


class PointNavRGBDModel(nn.Module):
    """RGBD PointNav policy (single-step GRUCell inference)."""
    def __init__(self, weights_path=None):
        super().__init__()
        self.visual_encoder = ResNet18EncoderRGBD()
        self.visual_fc = nn.Sequential(nn.Linear(2048, 512), nn.ReLU(inplace=True))
        self.tgt_embeding = nn.Linear(3, 32)
        self.prev_action_embedding = nn.Embedding(5, 32)
        self.state_encoder = nn.GRUCell(576, 512)
        self.action_distribution = nn.Linear(512, 4)
        self.critic = nn.Linear(512, 1)
        self.hx = torch.zeros(1, 512)
        if weights_path:
            self._load_weights(weights_path)

    def _load_weights(self, path):
        import re
        state = torch.load(path, map_location='cpu')
        if 'state_dict' in state:
            state = state['state_dict']
        model_dict = self.state_dict()
        for ck, cv in state.items():
            nk = ck
            nk = nk.replace('net.visual_encoder.backbone.', 'visual_encoder.')
            nk = re.sub(r'visual_encoder\.conv1\.0\.', 'visual_encoder.conv1.', nk)
            if re.search(r'visual_encoder\.conv1\.1\.', nk):
                nk = re.sub(r'conv1\.1\.weight', 'bn1.weight', nk)
                nk = re.sub(r'conv1\.1\.bias', 'bn1.bias', nk)
            nk = re.sub(r'\.convs\.0\.', '.conv1.', nk)
            nk = re.sub(r'\.convs\.1\.bias', '.bn1.bias', nk)
            nk = re.sub(r'\.convs\.1\.weight', '.bn1.weight', nk)
            nk = re.sub(r'\.convs\.3\.', '.conv2.', nk)
            nk = re.sub(r'\.convs\.4\.bias', '.bn2.bias', nk)
            nk = re.sub(r'\.convs\.4\.weight', '.bn2.weight', nk)
            nk = nk.replace('net.visual_fc.1.', 'visual_fc.0.')
            nk = nk.replace('net.tgt_embeding.', 'tgt_embeding.')
            nk = nk.replace('net.prev_action_embedding.', 'prev_action_embedding.')
            nk = nk.replace('net.state_encoder.rnn.', 'state_encoder.')
            nk = re.sub(r'state_encoder\.(.*)_l0', r'state_encoder.\1', nk)
            nk = nk.replace('action_distribution.linear.', 'action_distribution.')
            nk = nk.replace('critic.fc.', 'critic.')
            nk = nk.replace('net.visual_encoder.running_mean_and_var.', 'visual_encoder.running_mean_and_var.')
            nk = nk.replace('net.visual_encoder.compression.', 'visual_encoder.compression.')
            if nk in model_dict and model_dict[nk].shape == cv.shape:
                model_dict[nk] = cv
        self.load_state_dict(model_dict, strict=False)

    def forward(self, rgb, depth, goal_vector, prev_action=0):
        """
        Args:
            rgb:   (1, 3, 256, 256) float32 [0,1]
            depth: (1, 1, 256, 256) float32
            goal_vector: (1, 3) [dist/5, sin(θ), cos(θ)]
            prev_action: int 0-4
        Returns:
            action: int 0=STOP, 1=FORWARD, 2=LEFT, 3=RIGHT
        """
        rgbd = torch.cat([rgb, depth], dim=1)          # (1, 4, 256, 256)
        x = self.visual_encoder(rgbd)                   # (1, 2048)
        x = self.visual_fc(x)                            # (1, 512)
        g = self.tgt_embeding(goal_vector)               # (1, 32)
        a = self.prev_action_embedding(
            torch.tensor([prev_action], dtype=torch.long))
        combined = torch.cat([x, g, a], dim=-1)          # (1, 576)
        self.hx = self.state_encoder(combined, self.hx)
        logits = self.action_distribution(self.hx)
        return torch.argmax(logits, dim=-1).item()

    def reset(self):
        self.hx = torch.zeros(1, 512)
