### Week 6 — 2026-07-31

**Attended this week's meeting:** Yes

**Progress this week**

- **Real robot deployment pipeline established:**
  - Intel RealSense D455 connected to Orange Pi 5 Pro (USB 3.0), mounted on TB3 Burger top plate (~0.22 m height).
  - D455 firmware 5.17.3.10 verified; depth quality confirmed in usable range.
  - End-to-end pipeline: D455 → depth preprocessing → TorchScript PointNav → `/cmd_vel`.
  - Robot observed alternating FORWARD / TURN_LEFT / TURN_RIGHT behavior — model is reactive to environment.

- **Model export to TorchScript:**
  - Both trained models exported via `torch.jit.script` (not trace — GRU recurrency requires scripting).
  - `policy_depth_jit.pt` (35 MB, depth-only ckpt.99, 1-channel input).
  - `policy_rgbd_jit.pt` (35 MB, RGBD ckpt.43, 4-channel input).
  - Pure PyTorch architecture (no torchvision / Habitat dependency) — loads with `torch.jit.load()` on Orange Pi.
  - Key fix: `inplace=False` on all ReLU layers for TorchScript compatibility.

- **Critical architecture fixes (compared to Week 5 standalone model):**
  - **MaxPool added** to ResNet18 backbone after conv1 — matches Habitat training architecture (previously missing, causing the model to always output STOP).
  - **Goal format corrected** from Cartesian `[dist/5, sin(θ), cos(θ)]` to Habitat POLAR `[rho (m), -phi (rad), compass_yaw (rad)]` — matches `PointGoalWithGPSCompassSensor` training format.
  - **BatchNorm momentum = 0** confirmed — Habitat sets this during training, so BN running stats stay at defaults (mean=0, var=1) throughout. Missing BN stats in checkpoint are expected and benign.
  - **Prev_action feedback** — now properly tracked and passed to the model each step.

- **TB3 camera height domain adaptation:**
  - Habitat training: depth sensor at 1.25 m.
  - Real TB3 Burger: D455 at 0.22 m → floor visible at ~0.36 m in bottom portion of FOV.
  - Mitigations applied in `d455_preprocess.py`:
    - `CROP_BOTTOM_PX = 180` — discards bottom 180 rows (ground region) from 480-row raw image.
    - `MIN_DEPTH = 0.5` — clips floor reflections and robot-body proximity.

- **Gazebo simulation environment:**
  - Nav2 (AMCL + global planner + DWB) verified working in `turtlebot3_world` with saved map `tb3_map.yaml`.
  - LiDAR-to-depth projection (`scan_to_depth`) enables depth-only model testing in Gazebo.
  - TB3 Burger lacks RGB camera in Gazebo → RGBD model requires LiDAR-to-depth + simulated RGB (waffle_pi model has RGB, depth camera can be added via URDF).
  - Investigated adding depth camera to waffle_pi model via `realsense_gazebo_plugin`.

- **Nav2 integration plan for PointNav:**
  - Explored Nav2 controller plugin approach (C++ `pluginlib` interface) — not practical for Python-only codebase.
  - Designed external Python node integration: subscribe to Nav2 `/plan` (global path) + `/odom` + D455 → PointNav → `/cmd_vel`.
  - Nav2 DWB controller can be disabled or run in parallel for comparison.
  - This approach replaces Nav2's local planner with a learned policy while retaining AMCL + global planner.

**Deployment architecture**

```
┌─ Nav2 (optional) ────┐
│  Global Planner (A*)  │
│  AMCL (localization)  │
│  /plan (global path)  │
└──────────┬────────────┘
           │
┌──────────▼────────────┐
│  PointNav Node (Python)│
│  TorchScript model     │
│  D455 depth input      │
│  odom → goal vector    │
│  → /cmd_vel            │
└───────────────────────┘
```

**Key files created/updated in `src/deploy/`**

| File | Purpose |
|------|---------|
| `policy_depth_jit.pt` | TorchScript depth-only model (35 MB) |
| `policy_rgbd_jit.pt` | TorchScript RGBD model (35 MB) |
| `jit_policy.py` | Model architecture definition (script-compatible) |
| `d455_preprocess.py` | D455 depth → Habitat input (crop + clip + resize) |
| `d455_deploy.py` | ROS 2 / standalone deployment node |
| `inference_rgbd.py` | RGBD model class (PyTorch, Gazebo-sourced) |
| `pointnav_inference.py` | Standalone model + agent (pre-TorchScript fallback) |

**Challenges & blockers**

- **Inference latency causes stuttering:** The robot moves with noticeable jerkiness at each step — likely due to TorchScript model inference time on the Orange Pi 5 Pro CPU. The control loop runs at 10 Hz but inference may not complete within the 100 ms window, causing delayed or skipped control updates. Profiling and potential ONNX conversion / model pruning should be investigated.
- **Oscillatory "head-shaking" behavior:** The robot frequently gets stuck alternating between TURN_LEFT and TURN_RIGHT without making forward progress toward the goal. This suggests the model's depth input + goal vector combination is ambiguous — the model sees alternating obstacle patterns or the goal angle keeps crossing the decision boundary, causing indecisive back-and-forth turning.
- Model struggles to maintain goal-directed behavior over longer distances. The discrete action space (4 actions: STOP / FORWARD / TURN_LEFT / TURN_RIGHT) limits fine-grained control compared to continuous velocity outputs.
- D455-to-Habitat depth domain gap still significant — LiDAR-like D455 patterns differ from Gibson rendered depth. Real-world domain randomization may be needed.
- Camera height mismatch (0.22 m vs 1.25 m) changes the entire perspective; bottom-crop mitigates but doesn't fully resolve.
- Gazebo TB3 Burger has no depth camera — RGBD model can only be tested with LiDAR-to-depth proxy or with modified URDF.

**Next steps**

- Profile TorchScript inference latency; consider ONNX Runtime conversion or model pruning to reduce stuttering. Add action smoothing.
- Write Nav2-integrated PointNav node subscribing to `/plan` for automatic sub-goal extraction.

**Hours spent (optional):** 18h

**Links (optional):**
- Deploy directory: `FURP-2026-YicongNing-RLNavigationForAMR/src/deploy/`
- TorchScript models: `src/deploy/policy_depth_jit.pt`, `src/deploy/policy_rgbd_jit.pt`
- Lab 5 (deploy code): `src/lab5/`
- Gazebo workspace: `tb3_pointnav_ws/`
- Nav2 launch: `ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=$HOME/tb3_map.yaml`
- SLAM map: `~/tb3_map.pgm`, `~/tb3_map.yaml`
