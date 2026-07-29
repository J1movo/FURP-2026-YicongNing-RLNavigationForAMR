# D455 + PointNav — Real-Robot Deployment

End-to-end pipeline: D455 depth camera → PointNav inference → TurtleBot3 control.

## Files

| File | Purpose |
|------|---------|
| `model_depth_only.pt` | Exported depth-only PointNav checkpoint (ckpt.99, ~22 MB) |
| `pointnav_inference.py` | Standalone model + agent (no Habitat dependency) |
| `d455_preprocess.py` | D455 depth → Habitat input format |
| `d455_deploy.py` | Main inference node (standalone or ROS 2) |

## Setup (Orange Pi)

```bash
# 1. Install dependencies
pip install pyrealsense2 numpy opencv-python torch

# 2. Verify D455
realsense-viewer   # or: python -c "import pyrealsense2 as rs; print(rs.context().devices)"

# 3. Copy files to Orange Pi
scp model_depth_only.pt pointnav_inference.py d455_preprocess.py d455_deploy.py orangepi@<ip>:~/d455_nav/
```

## Test Pipeline (Dry-Run)

```bash
# Step 1 – test model loading only (no D455 needed)
python3 -c "
from pointnav_inference import PointNavAgent
import numpy as np
agent = PointNavAgent('model_depth_only.pt')
agent.reset()
action = agent.act(np.random.rand(1,256,256).astype(np.float32), (1.0, 0, 0))
print(f'Action: {action} ({agent.ACTION_NAMES[action]})')
print('Model OK')
"

# Step 2 – test D455 + preprocessing + model (no robot)
python3 d455_deploy.py --model model_depth_only.pt --dry-run
# Press Ctrl+C to stop.  Check that actions change as you move the camera.
```

## ROS 2 Deployment

```bash
# Terminal 1: bring up robot
ros2 launch turtlebot3_bringup robot.launch.py

# Terminal 2: start D455 + PointNav inference
python3 d455_deploy.py --model model_depth_only.pt --ros

# Terminal 3: RViz
rviz2
# → Click "2D Nav Goal" to set target
```

## Pipeline

```
D455 (pyrealsense2)
    │
    ▼
d455_preprocess.py          /odom ──→ TargetTracker ←── /goal_pose (RViz)
    │                                    │
    ▼                                    ▼
(1, 256, 256) float32          (dx, dy, dθ)
    │                                    │
    └──────────┬─────────────────────────┘
               ▼
        PointNavAgent.act()
               │
               ▼
        action → linear.x, angular.z
               │
               ▼
           /cmd_vel → TurtleBot3
```

## Model Specs

| Parameter | Value |
|-----------|-------|
| Architecture | ResNet18 + GRU (3-layer, 512) |
| Input | Depth (1×256×256) + goal (dx, dy, dθ) + prev action |
| Output | 4 discrete actions: STOP, FORWARD, TURN_LEFT, TURN_RIGHT |
| Depth range | [0, 10] m, normalised by /10.0 |
| Weights | ckpt.99, Seq = 98.1% Success, 90.2% SPL (Gibson eval) |

## Action Semantics

| Index | Action | linear.x | angular.z |
|:-----:|--------|:--------:|:---------:|
| 0 | STOP | 0.00 | 0.00 |
| 1 | FORWARD | 0.25 | 0.00 |
| 2 | TURN_LEFT | 0.00 | 0.50 |
| 3 | TURN_RIGHT | 0.00 | -0.50 |

## Safety

- **Always test with `--dry-run` first** — verify actions before connecting to robot.
- Keep a gamepad connected as emergency stop.
- Start with low speed: reduce `linear.x` from 0.25 to 0.10 for initial tests.
- The model has **no collision detection** — add a LiDAR safety layer (stop if < 0.3 m).
