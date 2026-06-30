#!/bin/bash
# =============================================================================
# PointNav PPO Baseline Training — Gibson Dataset
# =============================================================================
# Reproduces: Habitat 1.0 paper (ICCV 2019) PointNav baseline
# Config:     ppo_pointnav.yaml (ResNet18, 75M steps)
# Dataset:    Gibson scenes + PointNav Gibson v1 episodes
# =============================================================================

set -e

# --- Paths ---
HABITAT_LAB="/home/jimovo/Desktop/FURP/habitat-lab"
CONDA_PYTHON="/home/jimovo/miniconda3/envs/habitat/bin/python3"

# --- Experiment settings ---
EXPERIMENT_NAME="baseline_pointnav_gibson"
CONFIG_NAME="pointnav/ppo_pointnav"          # Full Gibson training config
SEED=42

# --- Overrides ---
# These override the defaults from ppo_pointnav.yaml:
#   - checkpoint/output dirs go under habitat-lab (large files, gitignored)
#   - seed for reproducibility
#   - evaluate=False → training mode
HABITAT_OVERRIDES="
    habitat.seed=${SEED}
    habitat.simulator.scene_dataset=data/scene_datasets/gibson/gibson.scene_dataset_config.json
    habitat_baselines.checkpoint_folder=data/checkpoints/${EXPERIMENT_NAME}
    habitat_baselines.tensorboard_dir=data/tb/${EXPERIMENT_NAME}
    habitat_baselines.video_dir=data/video/${EXPERIMENT_NAME}
    habitat_baselines.eval_ckpt_path_dir=data/checkpoints/${EXPERIMENT_NAME}
    habitat_baselines.evaluate=False
    habitat_baselines.num_environments=5
    habitat_baselines.num_updates=-1
    habitat_baselines.test_episode_count=1
    habitat_baselines.eval.video_option=[\"disk\"]
"

echo "============================================"
echo "  PointNav PPO Baseline Training"
echo "  Experiment: ${EXPERIMENT_NAME}"
echo "  Config:     ${CONFIG_NAME}"
echo "  Seed:       ${SEED}"
echo "  GPU:        $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'check nvidia-smi')"
echo "============================================"

# --- Stability env vars (avoid EGL/Mesa conflicts during multi-env init) ---
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
export OMP_NUM_THREADS=1

cd "${HABITAT_LAB}"
exec ${CONDA_PYTHON} -u -m habitat_baselines.run \
    --config-name="${CONFIG_NAME}" \
    ${HABITAT_OVERRIDES}
