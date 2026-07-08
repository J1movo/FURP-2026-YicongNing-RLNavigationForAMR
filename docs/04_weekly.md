### Week 4 — 2026-07-04

**Attended this week's meeting:** Yes

**Progress this week**
- **Depth-only PointNav PPO training completed** on Gibson dataset:
  - Same architecture (ResNet18 + GRU, 5.82M params), `depth_agent` config (1 input channel).
  - Trained to **74.99M / 75M steps (100%)**, 100 checkpoints saved.
  - **Final: Success 97.8% ± 0.3%, SPL 89.9% ± 0.3%** (avg of last 10 checkpoints).
  - Peak: Success 100.0%, SPL 95.6%.

| # | Step | Success | SPL | Reward |
|---|------|:------:|:----:|:------:|
| 1 | 74,996,736 | 98.1% | 90.4% | 7.57 |
| 2 | 74,996,224 | 98.1% | 90.2% | 7.57 |
| 3 | 74,995,712 | 98.1% | 90.3% | 7.56 |
| 4 | 74,995,200 | 97.9% | 90.1% | 7.54 |
| 5 | 74,994,688 | 97.9% | 89.7% | 7.51 |
| 6 | 74,994,176 | 97.6% | 89.7% | 7.45 |
| 7 | 74,993,664 | 97.4% | 89.5% | 7.46 |
| 8 | 74,993,152 | 97.4% | 89.6% | 7.46 |
| 9 | 74,992,640 | 97.5% | 89.6% | 7.48 |
| 10 | 74,992,128 | 97.7% | 89.6% | 7.49 |
| **Avg ± Std** | | **97.8% ± 0.3%** | **89.9% ± 0.3%** | **7.51 ± 0.05** |

- **ROS 2 + Gazebo simulation environment set up:**
  - Installed ROS 2 Humble + TurtleBot3 + Gazebo 11.
  - Verified TurtleBot3 LiDAR, RGB camera, and odometry sensors.
  - Wrote PointNav inference ROS 2 node supporting both RGBD and Depth-only models.
  - LiDAR-to-depth projection + collision safety. End-to-end `sensor → model → cmd_vel` pipeline verified.

- **Isaac Sim installation:**
  - Installed NVIDIA Isaac Sim 6.0.1 (Workstation) for high-fidelity sensor simulation.
  - Imported TurtleBot3 URDF + scanned 3D scene into Isaac Sim.
  - Investigating Isaac Sim ROS 2 Bridge for policy testing with realistic depth input.

- **Model deployment preparation:**
  - Exported standalone inference code for both models (`inference_depth_only.py`, `inference_rgbd.py`), fully independent of Habitat.
  - Wrote deployment guide `DEPLOY.md`.
  - Created ROS 2 deployment node `pointnav_deploy.py` for depth camera input.

**Model comparison**

| | RGBD | Depth-Only |
|------|:------:|:--:|
| Success | 96.9% ± 0.5% | **97.8% ± 0.3%** |
| SPL | 86.4% ± 0.9% | **89.9% ± 0.3%** |
| Input channels | 4 (RGB+Depth) | 1 (Depth) |
| Training steps | 32.4M (43%) | 75M (100%) |
| FPS | ~160 | ~380 |

**Challenges & blockers**
- LiDAR-projected depth images differ significantly from Habitat training data; model navigation performance is limited in Gazebo.
- TurtleBot3 Burger lacks a depth camera — external camera required for deployment.
- `ros2 run` entry point registration failed; worked around by running Python scripts directly.
- System pip missing numpy/torch on ARM — resolved via apt or system Python pip.

**Next steps**
- Set up Isaac Sim ROS 2 Bridge and run end-to-end model inference.
- Deploy and test the model on real hardware (depth camera installation needed first).

**Hours spent (optional):** 14h

**Links (optional):**
- Depth-only training script: `src/lab2/training/train_depth_only.sh`
- Deployment code: `src/deploy/`
- ROS 2 node: `tb3_pointnav_ws/`
- Depth-only checkpoints: `habitat-lab/data/checkpoints/depth_only_pointnav_gibson/`
