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