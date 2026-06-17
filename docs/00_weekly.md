# Weekly Progress Log

> Update this file **every week**. Add a new entry at the top for each week.
> This is the first thing we check during review. Keep it honest and specific — it also feeds your attendance record (Rule 1).

**How to use:** copy the *Week template* block below for each new week. Newest week goes at the top.

---

## Week template — copy me

### Week N — YYYY-MM-DD

**Attended this week's meeting:** Yes / No (if No, did you email leave? Yes / No)

**Progress this week**
- _What did you actually do / finish?_

**Challenges & blockers**
- _What got in the way? What are you stuck on?_

**Next steps**
- _What will you do next week?_

**Hours spent (optional):** _e.g. 6h_

**Links (optional):** _commits, notebooks, docs, datasets..._

---

<!-- =================  YOUR ENTRIES BELOW  ================= -->

### Week 1 — 2026-06-17

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
- Smoke test (no-scene) passed:
  - All imports OK (habitat, habitat_sim, torch, numpy, cv2)
  - Config system and simulator API functional
  - Script: `src/lab1_smoke_test.py`
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
- **WSL2 CUDA-EGL interop failure**: scene rendering fails with `unable to find CUDA device 0 among 1 EGL devices`. D3D12 EGL layer in WSL2 and CUDA device enumeration are mismatched. Visual smoke test (`lab1_visual_smoke_test.py`) cannot complete.

**Next steps**
- Resolve WSL2 EGL rendering issue (consider using a USB stick to install the Linux operating system)
- Complete visual smoke test with RGB, depth, and top-down trajectory evidence

**Hours spent (optional):**

**Links (optional):**
- Smoke test script: `src/lab1_smoke_test.py`
