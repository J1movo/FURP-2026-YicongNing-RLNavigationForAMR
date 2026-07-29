# Lab 5 — Real Robot Deployment & TorchScript Export

Deploy PointNav models on TurtleBot3 Burger + Intel RealSense D455.

## Quick Start (Orange Pi)

```bash
# Standalone test (no robot movement)
python3 d455_deploy.py --model policy_depth_jit.pt --dry-run

# ROS 2 deployment
python3 d455_deploy.py --model policy_depth_jit.pt --ros
```

## Files

| File | Purpose |
|------|---------|
| `d455_deploy.py` | ROS 2 / standalone deployment node |
| `d455_preprocess.py` | D455 depth → Habitat input (crop bottom, clip, resize 256×256) |
| `pointnav_inference.py` | Standalone PointNav model + agent (PyTorch, pre-TorchScript) |
| `inference_rgbd.py` | RGBD model class (PyTorch, used in Gazebo node) |
| `jit_policy.py` | TorchScript-compatible model architecture definition |
| `diag.py` | Depth model diagnostic (prints depth stats + action per frame) |

Large model files (NOT in repo — reference only):

| File | Size | Source |
|------|------|--------|
| `src/deploy/policy_depth_jit.pt` | 35 MB | Depth-only TorchScript (ckpt.99) |
| `src/deploy/policy_rgbd_jit.pt` | 35 MB | RGBD TorchScript (ckpt.43) |

## Architecture

```
D455 (pyrealsense2)          /odom              /goal_pose or /plan
      │                         │                      │
      ▼                         ▼                      ▼
d455_preprocess.py         pose (x, y, yaw)      goal (gx, gy)
      │                         │                      │
      ▼                         └──────────┬───────────┘
(1, 256, 256) float32                    ▼
      │                          goal vector
      │                    [rho, -phi, compass]
      │                         │
      └─────────┬───────────────┘
                ▼
      TorchScript model (policy_depth_jit.pt)
                │
                ▼
      action logits → discrete action → /cmd_vel
```

## ROS Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/cmd_vel` | Twist | Out (published) |
| `/odom` | Odometry | In (subscribed) |
| `/move_base_simple/goal` | PoseStamped | In (from RViz) |
| `/goal_pose` | PoseStamped | In (from Nav2 / RViz) |

## Key Parameters

| Parameter | Value | Reason |
|-----------|-------|--------|
| `MIN_DEPTH` | 0.5 m | Clip floor reflections (camera at 0.22 m) |
| `CROP_BOTTOM_PX` | 180 px | Discard ground region from 480-row image |
| `H`, `W` | 256, 256 | Habitat training resolution |
| `MAX_DEPTH` | 10.0 m | Habitat default max depth |
| FORWARD speed | 0.22 m/s | TB3 Burger max speed |
| TURN speed | ±1.0 rad/s | Angular velocity |

## Dependencies (Orange Pi)

```bash
pip install pyrealsense2 numpy opencv-python torch
```
