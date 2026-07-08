#!/bin/bash
# =============================================================================
# PointNav PPO Depth-Only Training — Gibson Dataset
# =============================================================================
# Same as RGBD baseline but uses depth_agent (no RGB sensor, 1 input channel)
# =============================================================================

set -e

HABITAT_LAB="/home/jimovo/Desktop/FURP/habitat-lab"
CONDA_PYTHON="/home/jimovo/miniconda3/envs/habitat/bin/python3"
EXPERIMENT_NAME="depth_only_pointnav_gibson"
SEED=42

# Stability env vars
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
export OMP_NUM_THREADS=1

HABITAT_OVERRIDES="
    habitat.seed=${SEED}
    habitat.simulator.scene_dataset=data/scene_datasets/gibson/gibson.scene_dataset_config.json
    habitat_baselines.checkpoint_folder=data/checkpoints/${EXPERIMENT_NAME}
    habitat_baselines.tensorboard_dir=data/tb/${EXPERIMENT_NAME}
    habitat_baselines.video_dir=data/video/${EXPERIMENT_NAME}
    habitat_baselines.eval_ckpt_path_dir=data/checkpoints/${EXPERIMENT_NAME}
    habitat_baselines.evaluate=False
    habitat_baselines.num_environments=4
    habitat_baselines.num_updates=-1
    habitat_baselines.test_episode_count=3
    habitat_baselines.eval.video_option=[\"disk\"]
"

echo "============================================"
echo "  PointNav PPO Depth-Only Training"
echo "  Experiment: ${EXPERIMENT_NAME}"
echo "  GPU:        $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null)"
echo "============================================"

cd "${HABITAT_LAB}"
exec ${CONDA_PYTHON} -u -m habitat_baselines.run \
    --config-name="pointnav/ppo_pointnav_depth_only" \
    ${HABITAT_OVERRIDES}
