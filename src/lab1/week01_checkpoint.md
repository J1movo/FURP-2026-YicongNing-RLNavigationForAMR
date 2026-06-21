# Week 1 Checkpoint

## Student / Team

- Name(s): Yicong Ning
- Student ID(s): 20720098
- Date: 2026-06-21

## Environment

- [x] Python environment created
- [x] Dependencies installed without conflicts
- [x] Project folder structure understood

## Smoke test

- [x] Smoke test command executed
- [x] No runtime crash
- [x] Output evidence attached
<img src=".\results\week1_smoke_test_terminal_output.png" width = 500>
<img src=".\results\week1_pointnav_interactive_terminal_output.png" width = 500>

## Reflection

1. What was the hardest setup issue?
   - **WSL2 CUDA-EGL interop failure**: scene rendering failed with `unable to find CUDA device 0 among 1 EGL devices`. The D3D12 EGL layer in WSL2 and CUDA device enumeration are mismatched, blocking all visual rendering in Habitat.

2. How did you solve it?
   - Migrated from Windows 11/WSL2 to **Ubuntu 22.04.5 LTS** native installation on a machine with an NVIDIA GPU, eliminating the WSL2 EGL translation layer entirely.
   - Cleaned up leftover partial NVIDIA driver packages from the previous hardware before installing `nvidia-driver-595` fresh.

3. What still needs support?
   - Choosing suitable papers for further reading.