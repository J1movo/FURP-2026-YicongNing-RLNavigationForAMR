#!/usr/bin/env python3
"""
PointNav PPO inference server — loads a habitat-baselines checkpoint and
serves action predictions over TCP (localhost:9876).

Designed to run in the conda ``habitat`` environment (Python 3.9), where
habitat-baselines is installed.  ROS 2 (system Python 3.10) talks to this
server to avoid the Python 3.9 / 3.10 C-extension mismatch.

Protocol (JSON-line, one JSON object per line over TCP):
    Request  → {"rgb": [[[r,g,b],...],...], "depth": [[d,...],...],
                 "goal": [distance, angle_rad], "reset": false}
    Response ← {"action": 0-3, "error": null}

Usage:
    conda activate habitat
    python inference_server.py --ckpt /path/to/latest.pth [--port 9876]
"""

import argparse
import json
import math
import socketserver
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import torch
from gym import spaces

# --- habitat_sim / magnum stub (blocks dead-code import chains) ---
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import habitat_stub_full

habitat_stub_full.install()

from habitat_baselines.rl.ddppo.policy.resnet_policy import PointNavResNetPolicy

# ---------------------------------------------------------------------------
# Observation / action spaces (must match training)
# ---------------------------------------------------------------------------

OBSERVATION_SPACE = spaces.Dict(
    {
        "rgb": spaces.Box(low=0, high=255, shape=(256, 256, 3), dtype=np.uint8),
        "depth": spaces.Box(
            low=0.0, high=1.0, shape=(256, 256, 1), dtype=np.float32
        ),
        "pointgoal_with_gps_compass": spaces.Box(
            low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32
        ),
    }
)

ACTION_SPACE = spaces.Discrete(4)
ACTION_NAMES = {0: "STOP", 1: "FORWARD", 2: "TURN_LEFT", 3: "TURN_RIGHT"}


# ---------------------------------------------------------------------------
# Model loader
# ---------------------------------------------------------------------------


def load_policy(ckpt_path: str, device: torch.device):
    """Load a PointNavResNetPolicy from a habitat-baselines checkpoint."""
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    config = ckpt["config"]
    hb = config.habitat_baselines
    agent_name = config.habitat.simulator.agents_order[0]
    policy_config = hb.rl.policy[agent_name]

    policy = PointNavResNetPolicy(
        observation_space=OBSERVATION_SPACE,
        action_space=ACTION_SPACE,
        hidden_size=hb.rl.ppo.hidden_size,
        num_recurrent_layers=hb.rl.ddppo.num_recurrent_layers,
        rnn_type=hb.rl.ddppo.rnn_type,
        backbone=hb.rl.ddppo.backbone,
        normalize_visual_inputs="rgb" in OBSERVATION_SPACE.spaces,
        policy_config=policy_config,
        aux_loss_config=hb.rl.auxiliary_losses,
        fuse_keys=None,
    )
    policy.load_state_dict(ckpt["state_dict"])
    policy.to(device)
    policy.eval()

    return policy, hb


# ---------------------------------------------------------------------------
# TCP handler
# ---------------------------------------------------------------------------


class InferenceHandler(socketserver.StreamRequestHandler):
    """Handle one TCP connection (the server keeps the model loaded across
    sessions.  In practice the ROS node connects once and keeps the socket
    open for the entire episode.)"""

    def handle(self):
        peer = self.client_address
        print(f"[server] connected: {peer}", flush=True)

        # Per-connection RNN state
        rnn_hidden = torch.zeros(
            1,
            self.server.num_recurrent_layers,
            self.server.hidden_size,
            device=self.server.device,
        )
        prev_actions = torch.zeros(1, 1, dtype=torch.long, device=self.server.device)
        masks = torch.zeros(1, 1, dtype=torch.bool, device=self.server.device)
        total_requests = 0
        total_time_s = 0.0

        try:
            for line in self.rfile:
                line = line.strip()
                if not line:
                    continue

                try:
                    req = json.loads(line)
                except json.JSONDecodeError as e:
                    self._respond({"action": 0, "error": f"JSON parse: {e}"})
                    continue

                # --- Reset flag ---
                if req.get("reset", False):
                    rnn_hidden.zero_()
                    prev_actions.zero_()
                    masks.zero_()
                    print("[server] RNN reset", flush=True)
                    self._respond({"action": 0, "error": None, "reset_ack": True})
                    continue

                # --- Build observation tensors ---
                try:
                    rgb_np = np.array(req["rgb"], dtype=np.uint8)  # (256,256,3)
                    depth_np = np.array(req["depth"], dtype=np.float32)  # (256,256)
                    goal = req["goal"]  # [distance, angle]
                except (KeyError, ValueError) as e:
                    self._respond({"action": 0, "error": f"Bad request: {e}"})
                    continue

                rgb_t = (
                    torch.from_numpy(rgb_np).unsqueeze(0).to(self.server.device)
                )  # (1,256,256,3)
                depth_t = (
                    torch.from_numpy(depth_np)
                    .unsqueeze(0)
                    .unsqueeze(-1)
                    .to(self.server.device)
                )  # (1,256,256,1)
                goal_t = torch.tensor(
                    [[goal[0], goal[1]]],
                    dtype=torch.float32,
                    device=self.server.device,
                )

                observations = {
                    "rgb": rgb_t,
                    "depth": depth_t,
                    "pointgoal_with_gps_compass": goal_t,
                }

                # --- Diagnostic: log obs stats every 20 requests ---
                total_requests += 1
                if total_requests == 1 or total_requests % 20 == 0:
                    print(
                        f"[diag] req#{total_requests}: "
                        f"rgb={rgb_np.shape} [{rgb_np.min()},{rgb_np.max()}] "
                        f"depth={depth_np.shape} [{depth_np.min():.3f},{depth_np.max():.3f}] "
                        f"goal=[{goal[0]:.2f}m, {math.degrees(goal[1]):.0f}°]",
                        flush=True,
                    )

                # --- Inference ---
                t0 = time.perf_counter()
                with torch.no_grad():
                    action_data = self.server.policy.act(
                        observations,
                        rnn_hidden,
                        prev_actions,
                        masks,
                        deterministic=True,
                    )
                if self.server.device.type == "cuda":
                    torch.cuda.synchronize()
                elapsed_ms = (time.perf_counter() - t0) * 1000

                # --- Update RNN state ---
                rnn_hidden = action_data.rnn_hidden_states
                prev_actions = action_data.actions
                masks = torch.ones(1, 1, dtype=torch.bool, device=self.server.device)

                action_idx = int(action_data.actions.item())

                total_time_s += elapsed_ms / 1000

                self._respond(
                    {
                        "action": action_idx,
                        "error": None,
                        "latency_ms": round(elapsed_ms, 1),
                    }
                )

        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            avg_lat = (
                total_time_s / total_requests * 1000 if total_requests > 0 else 0
            )
            print(
                f"[server] disconnected: {peer}  "
                f"(requests={total_requests}, avg_lat={avg_lat:.0f}ms)",
                flush=True,
            )

    def _respond(self, data: dict):
        try:
            self.wfile.write((json.dumps(data) + "\n").encode())
            self.wfile.flush()
        except (ConnectionResetError, BrokenPipeError):
            pass


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------


class InferenceServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, policy, hidden_size, num_recurrent_layers, device):
        self.policy = policy
        self.hidden_size = hidden_size
        self.num_recurrent_layers = num_recurrent_layers
        self.device = device
        super().__init__(server_address, InferenceHandler)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="PointNav PPO Inference Server")
    parser.add_argument(
        "--ckpt", required=True, help="Path to .pth checkpoint"
    )
    parser.add_argument(
        "--port", type=int, default=9876, help="TCP port (default: 9876)"
    )
    parser.add_argument(
        "--device", default="cuda", help="Device: cuda or cpu (default: cuda)"
    )
    args = parser.parse_args()

    # Device
    if args.device == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    print(f"[server] device: {device}", flush=True)

    # Load model
    print(f"[server] loading checkpoint: {args.ckpt}", flush=True)
    policy, hb = load_policy(args.ckpt, device)
    print(
        f"[server] model ready  "
        f"backbone={hb.rl.ddppo.backbone}  "
        f"hidden={hb.rl.ppo.hidden_size}  "
        f"rnn={hb.rl.ddppo.rnn_type}(layers={hb.rl.ddppo.num_recurrent_layers})",
        flush=True,
    )

    # Start server
    server = InferenceServer(
        ("127.0.0.1", args.port),
        policy,
        hb.rl.ppo.hidden_size,
        hb.rl.ddppo.num_recurrent_layers,
        device,
    )
    print(f"[server] listening on 127.0.0.1:{args.port}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] shutting down.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
