### Week 5 — 2026-07-15

**Attended this week's meeting:** Yes

**Progress this week**

- **Isaac Lab installation and configuration completed:**
  - Installed Isaac Lab v3.0.0-beta2.patch1 (the only release compatible with Isaac Sim 6.0) on top of the existing Isaac Sim 6.0.1 binary installation.
  - Created conda environment `env_isaaclab` (Python 3.12) and installed all 16 extensions: `isaaclab`, `isaaclab_tasks`, `isaaclab_rl`, `isaaclab_assets`, `isaaclab_physx`, `isaaclab_newton`, `isaaclab_ov`, `isaaclab_ovphysx`, `isaaclab_ppisp`, `isaaclab_visualizers`, `isaaclab_mimic`, `isaaclab_teleop`, `isaaclab_contrib`, `isaaclab_experimental`, `isaaclab_tasks_experimental`.
  - RL frameworks ready: `rl_games`, `rsl_rl`, `skrl`, `sb3`, `robomimic`.

- **Compatibility issues resolved (Isaac Sim 6.0.1 + Isaac Lab v3.0.0-beta2):**
  - Missing `setup_conda_env.sh` → Created runtime environment script that correctly sets Kit Python stdlib paths.
  - Missing `EXP_PATH` / `ISAAC_PATH` env vars → Configured in conda activation hooks.
  - Kit Python 3.12 `platform.py` fails to parse conda-forge version string → Patched to strip `| packaged by conda-forge |` prefix.
  - `_isaac_sim` symlink management → Recreated and documented for persistence.
  - conda base Python 3.13 vs. Kit Python 3.12 stdlib conflict → Separated path loading: conda hooks load only extension paths; stdlib loaded at runtime by `isaaclab.sh`.

- **Installation verification:**
  - `create_empty.py` — Empty scene launched successfully ✅
  - `run_articulation.py` — Cart-pole robot simulation running with visible GUI window ✅
  - `./isaaclab.sh --help` — CLI functional ✅
  - All core Python imports pass ✅

**Environment setup summary**

| Component | Version | Location |
|-----------|---------|----------|
| Isaac Sim | 6.0.1 (Workstation) | `~/isaacsim/` |
| Isaac Lab | v3.0.0-beta2.patch1 | `~/Desktop/FURP/IsaacLab/` |
| Python | 3.12.13 (conda-forge) | `env_isaaclab` |
| PyTorch | 2.13.0+cu130 | conda env |
| Gymnasium | 1.2.1 | conda env |

**Isaac Lab overview for this project**

Isaac Lab is NVIDIA's open-source robot learning framework built on Isaac Sim (Omniverse). For this AMR navigation project, it provides:

| Capability | Benefit over Habitat |
|------------|---------------------|
| High-fidelity physics (PhysX) | More realistic dynamics for sim-to-real transfer |
| RTX ray-traced sensors | RGB-D, LiDAR, IMU with realistic noise |
| URDF/MJCF robot import | Direct TurtleBot3 / custom AMR model support |
| ROS 2 bridge | Seamless sim-to-real deployment pipeline |
| Domain randomization | Improved policy generalization |
| Multi-RL-framework support | rl_games, rsl_rl, skrl, SB3, robomimic |
| Parallel simulation | Thousands of concurrent envs for faster training |

**Challenges & blockers**

- Isaac Sim 6.0.1 binary install has limited compatibility with Isaac Lab — the official documentation primarily targets the pip-based flow (Isaac Sim 5.1.0). The binary path required manual resolution of several environment configuration issues.
- Kit Python stdlib and conda Python stdlib path conflict required precise PYTHONPATH ordering control.
- Isaac Lab defaults to headless mode; GUI window requires explicit `--viz kit` flag.
- For cleaner long-term maintenance, switching to the pip-based installation (Isaac Sim 5.1.0 + Isaac Lab main) remains an option.

**Next steps**

- Import the AMR model (TurtleBot3 URDF or custom chassis) into Isaac Lab.
- Build a PointNav training environment using Isaac Lab's sensor simulation (RGB-D camera, LiDAR).
- Explore Isaac Lab's Domain Randomization features to improve sim-to-real generalization.
- Investigate the Isaac Lab → ROS 2 deployment pipeline.

**Hours spent (optional):** 10h

**Repo files:**
- `src/lab4/README.md` — overview + full installation guide
- `src/lab4/conda_hook_setenv.sh` — conda activation hook
- `src/lab4/conda_hook_unsetenv.sh` — conda deactivation hook
- `src/lab4/setup_conda_env.sh` — runtime environment script
- `src/lab4/patch_platform_py.py` — Kit Python compatibility patch
- `src/lab4/verify_install.py` — installation verification script
