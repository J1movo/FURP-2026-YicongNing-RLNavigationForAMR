# Lab 4 — Isaac Lab Setup

Isaac Lab v3.0.0-beta2.patch1 installed alongside Isaac Sim 6.0.1 (binary).

## Quick Start

```bash
conda activate env_isaaclab
cd ~/Desktop/FURP/IsaacLab
./isaaclab.sh -p scripts/tutorials/01_assets/run_articulation.py --viz kit
```

## Files

| File | Description |
|------|-------------|
| `conda_hook_setenv.sh` | Conda activation hook — sets `ISAAC_PATH`, `EXP_PATH`, `LD_LIBRARY_PATH`, etc. |
| `conda_hook_unsetenv.sh` | Conda deactivation hook — restores original env state |
| `setup_conda_env.sh` | Runtime env script — sourced by `isaaclab.sh` to load Kit Python stdlib |
| `patch_platform_py.py` | Applies conda-forge compatibility fix to Kit `platform.py` |
| `verify_install.py` | Quick verification: imports, env vars, SimulationApp |

## Installation Steps

### 1. Clone & link

```bash
cd ~/Desktop/FURP
git clone https://github.com/isaac-sim/IsaacLab.git --branch v3.0.0-beta2.patch1 --depth 1
cd IsaacLab
ln -s ~/isaacsim _isaac_sim
```

### 2. Create conda env & install hooks

```bash
conda env create -y --file environment.yml -n env_isaaclab
mkdir -p ~/miniconda3/envs/env_isaaclab/etc/conda/activate.d
mkdir -p ~/miniconda3/envs/env_isaaclab/etc/conda/deactivate.d
cp conda_hook_setenv.sh ~/miniconda3/envs/env_isaaclab/etc/conda/activate.d/setenv.sh
cp conda_hook_unsetenv.sh ~/miniconda3/envs/env_isaaclab/etc/conda/deactivate.d/unsetenv.sh
```

### 3. Runtime env script & platform patch

```bash
cp setup_conda_env.sh ~/isaacsim/
python patch_platform_py.py
```

### 4. Install extensions

```bash
conda activate env_isaaclab
for pkg in isaaclab isaaclab_ppisp isaaclab_assets isaaclab_contrib \
           isaaclab_experimental isaaclab_newton isaaclab_ov isaaclab_ovphysx \
           isaaclab_physx isaaclab_rl isaaclab_tasks isaaclab_tasks_experimental \
           isaaclab_visualizers isaaclab_teleop isaaclab_mimic; do
    pip install --editable source/$pkg
done
```

### 5. Verify

```bash
python verify_install.py
./isaaclab.sh -p scripts/tutorials/01_assets/run_articulation.py --viz kit
```

## Key Paths (local machine)

| Resource | Path |
|----------|------|
| Isaac Lab repo | `~/Desktop/FURP/IsaacLab/` |
| Isaac Sim | `~/isaacsim/` |
| Conda env | `env_isaaclab` (Python 3.12.13) |
| Activation hook | `~/miniconda3/envs/env_isaaclab/etc/conda/activate.d/setenv.sh` |
| Deactivation hook | `~/miniconda3/envs/env_isaaclab/etc/conda/deactivate.d/unsetenv.sh` |
| Runtime env script | `~/isaacsim/setup_conda_env.sh` |
| Kit platform.py | `~/isaacsim/kit/python/lib/python3.12/platform.py` (patched) |

## Compatibility Fixes Applied

| # | Issue | Root Cause | Fix |
|---|-------|-----------|-----|
| 1 | `setup_conda_env.sh` missing | Isaac Sim 6.0.1 has `setup_python_env.sh` instead | Created custom script |
| 2 | `EXP_PATH` / `ISAAC_PATH` unset | Not in any startup script | Added to conda hook |
| 3 | `_isaac_sim` symlink lost | Not persisted | `ln -s ~/isaacsim _isaac_sim` |
| 4 | `SRE module mismatch` | Kit Python 3.12 stdlib conflicts with conda base Python 3.13 | Extensions in hook, stdlib at runtime |
| 5 | `ValueError: failed to parse CPython sys.version` | Kit `platform.py` can't parse `\| packaged by conda-forge \|` | Strip conda packaging prefix before regex |
| 6 | No GUI window | Isaac Lab defaults to headless without visualizer | Use `--viz kit` flag |
