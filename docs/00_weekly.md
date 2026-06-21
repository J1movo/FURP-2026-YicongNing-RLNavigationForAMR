# Weekly Progress Log

> Update this file **every week**. Add a new entry at the top for each week.
> This is the first thing we check during review. Keep it honest and specific — it also feeds your attendance record (Rule 1).

**How to use:** copy the *Week template* block below for each new week. Newest week goes at the top.

---

<!-- =================  YOUR ENTRIES BELOW  ================= -->

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

---

### Week 1 — 2026-06-15

**Attended this week's meeting:** Yes

**Progress this week**
- Set up repository from the FURP template.
- Installed ROS2 and its dependencies.
- Set up ROS2 workspace and environments.
- Successfully ran ROS2 turtlesim demo — ROS2 installation verified.
- Chose starter path: **Habitat RL navigation path** for end-to-end navigation and reward design.
- Environment Record:
  - OS: Windows 11 (WSL2: Ubuntu 24.04 LTS)
  - Python: 3.13.9 (Windows) / 3.9 (WSL2 conda env)
  - Package manager: Pixi (Windows) / Conda + pip (WSL2)
  - Repository: [GitHub](https://github.com/J1movo/FURP-2026-YicongNing-RLNavigationForAMR/)
- WSL2 environment setup:
  - Installed Ubuntu 24.04 LTS via Microsoft Store
  - Installed Miniconda, created `habitat` conda env (Python 3.9)
- Habitat toolchain installed:
  - `conda install habitat-sim -c conda-forge -c aihabitat` (v0.3.3)
  - `pip install habitat-lab`
- CUDA verified:
  - Installed PyTorch with CUDA support (`pytorch-cuda=12.1`)
  - `torch.cuda.is_available()` - True on NVIDIA GPU
- Test scene data:
  - Installed git-lfs, manually cloned `habitat_test_scenes`
  - Successfully downloaded `apartment_1.glb` (50MB)
- Install commands:
    ```
    **Pixi + ROS2 (Windows)**
    > pixi install
    pixi run python preinstall_setup_windows.py
    > pixi shell
    call D:\ROS2\lyrical\local_setup.bat\

    **Conda (WSL2)**
    $ conda activate habitat
    ```

**Challenges & blockers**
- ROS2 commands differ across PowerShell, CMD, and Git Bash.
- **WSL2 CUDA-EGL interop failure**: scene rendering fails with `unable to find CUDA device 0 among 1 EGL devices`. D3D12 EGL layer in WSL2 and CUDA device enumeration are mismatched.

**Next steps**
- Resolve WSL2 EGL rendering issue (consider using a USB stick to install the Linux operating system)
- Complete visual smoke test with RGB, depth, and top-down trajectory evidence

**Hours spent (optional):**

**Links (optional):**

