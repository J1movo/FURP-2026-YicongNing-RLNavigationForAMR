# Real Robot Deployment Guide

## Hardware

| Component | Model |
|-----------|-------|
| Robot | WHEELTEC S100 differential-drive |
| Computer | NVIDIA Jetson Orin Nano (6-core ARM, 7.3GB RAM) |
| Camera | Orbbec Astra S (RGB 640×480, Depth 640×480 16UC1 mm) |
| OS | Ubuntu 20.04 + ROS1 Noetic |
| Odom | Wheel odometry + IMU EKF (`robot_pose_ekf`) |

## Software Stack

| Layer | Technology |
|-------|-----------|
| Inference | conda `wheeltec` (Python 3.8, PyTorch 1.14 NVIDIA Jetson build) |
| ROS | ROS1 Noetic, `rospy`, custom catkin workspace `ppo_ws` |
| Model | `PointNavResNetPolicy` (ResNet18 + GRU) from habitat-baselines |

## Files

| File | Purpose |
|------|---------|
| `habitat_stub.py` | Stub to bypass habitat-sim import on Jetson |
| `load_and_infer.py` | M1: offline model loading & inference test |
| `camera_preprocessor.py` | M2: RGB (640→256) + Depth (mm→m→norm→256) |
| `goal_computer.py` | M2: odom → polar goal coordinates |
| `m2_verify.py` | M2: end-to-end verification of observation pipeline |
| `s100_inference_node.py` | M3: main ROS node (subscribe → infer → publish cmd_vel) |
| `policy_wrappers.py` | M3: unified interface for habitat/JIT models |
| `preprocess.py` | M3: RGB/Depth preprocessing (same as M2, in-node) |
| `action_controller.py` | M3: discrete action → cmd_vel (step/continuous modes) |
| `s100_deploy.launch` | M3: ROS launch file |
| `STARTUP.md` | Quick-start commands reference |

## Quick Start

See `STARTUP.md` for the complete 7-terminal launch sequence.

## Key Design Decisions

1. **Step mode**: Execute one discrete action at a time (FORWARD 0.25m / TURN 10°), stop, then re-infer. Matches Habitat's step semantics.
2. **Depth safety**: Virtual bumper — stop if center-region min depth < safety threshold.
3. **RNN reset**: Hidden state reset on every new goal.
4. **Hole-filling**: Structured-light depth holes filled with local median before inference.

## Known Sim-to-Real Gaps

| Gap | Training | Real | Impact |
|-----|----------|------|--------|
| FOV | 90° | ~57.6° | Weaker edge obstacle detection |
| RGB | True color | IR grayscale | Texture-dependent models degrade in featureless rooms |
| Depth noise | Perfect | Structured-light holes (~60% center valid) | Mitigated by hole-filling |
| Frame rate | Variable | 30Hz RGBD | M2 sync ensures consistent timing |

## Model Checkpoints

Checkpoints are NOT stored in this repo due to size (~90MB each). They are located at:

- Training server (AutoDL): `/root/autodl-tmp/exp/`
- Jetson: `~/M3/`
- Local backup: `D:\AMR-Navigation-Project\autodl\exp\`

Available models for deployment:
- `ckpt.49.pth` — baseline_seed300 (SR 0.895)
- `stop_aware_seed300.pth` — stop_aware 1e7 (SR 0.900)
- `stop_aware_5e7_seed300.pth` — stop_aware 5e7 (SR 0.945)
- `policy_depth_jit.pt` — JIT depth-only (texture-robust)
