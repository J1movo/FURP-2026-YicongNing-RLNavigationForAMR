### Week 2 — 2026-06-21

**Attended this week's meeting:** Yes

**Progress this week**
- Migrated from Windows 11 / WSL2 to **Ubuntu 22.04.5 LTS** (native installation).
  - Reason: WSL2 CUDA-EGL interop failure blocked scene rendering in Week 1.
  - GPU: NVIDIA GeForce RTX 3060, 12 GB VRAM.
- Installed NVIDIA driver 595.71.05 with CUDA 13.2 support.
  - `nvidia-smi` working, kernel module loaded (`nvidia`, `nvidia_uvm`, `nvidia_modeset`).
- System dependencies installed: cmake 3.22.1, git-lfs 3.0.2, libegl1-mesa-dev, libgl1-mesa-glx, libglm-dev, mesa-utils, freeglut3-dev, xorg-dev, libjpeg-dev.
- Installed Miniconda 26.3.2.
- Created `habitat` conda environment: Python 3.9.25, cmake 3.14.0.
- Installed Habitat toolchain (official recommended method):
  - `conda install habitat-sim withbullet -c conda-forge -c aihabitat` (v0.3.3, pre-built binary).
  - `pip install -e habitat-lab` (v0.3.3, from locally cloned repo).
  - `pip install -e habitat-baselines` (v0.3.3).
  - Fixed pillow version conflict (habitat-sim requires 10.4.0, installed 11.3.0 initially).
- Downloaded test data via official download utility:
  - `habitat_test_scenes` (105 MB, `data/scene_datasets/habitat-test-scenes/`).
  - `habitat_test_pointnav_dataset` (0.9 MB, `data/datasets/pointnav/habitat-test-scenes/`).
- Verified PyTorch 2.8.0+cu128 with CUDA: True on RTX 3060.

**Smoke tests**
| Test | Script | Result |
|---|---|---|
| Interactive WASD rendering | `src/lab1/pointnav_interactive.py` | RGB window rendered correctly |
| Shortest-path follower | `src/lab1/shortest_path_smoke_test.py` | 2/3 episodes reached goal, trajectory videos saved |

**Challenges & blockers**
- `habitat-sim 0.3.3` requires `pillow==10.4.0`, conflicts with `habitat-lab` pulling `pillow 11.3.0` (resolved by pinning).

**Next steps**
- Reproduce PointNav PPO baseline training.
- Begin Week 3 literature review (e.g.: Habitat 1.0 paper: *"Habitat: A Platform for Embodied AI Research"*, ICCV 2019).

**Hours spent (optional):** 8h

**Links (optional):**
- Smoke test scripts: `src/lab1/pointnav_interactive.py`, `src/lab1/shortest_path_smoke_test.py`
- Sceenshot of terminal output: `src/results/`
- Trajectory videos: `src/lab1/results/shortest_path/`