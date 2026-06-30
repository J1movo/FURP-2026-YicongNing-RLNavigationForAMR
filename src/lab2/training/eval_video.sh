#!/bin/bash
# =============================================================================
# PointNav PPO — Evaluate checkpoint with video recording
# =============================================================================

set -e

HABITAT_LAB="/home/jimovo/Desktop/FURP/habitat-lab"
CONDA_PYTHON="/home/jimovo/miniconda3/envs/habitat/bin/python3"
EXPERIMENT_NAME="baseline_pointnav_gibson"

echo "============================================"
echo "  Evaluate Checkpoint (with video)"
echo "  Experiment: ${EXPERIMENT_NAME}"
echo "============================================"

cd "${HABITAT_LAB}"
exec ${CONDA_PYTHON} -u -m habitat_baselines.run \
    --config-name="pointnav/ppo_pointnav" \
    habitat.seed=42 \
    habitat.simulator.scene_dataset=data/scene_datasets/gibson/gibson.scene_dataset_config.json \
    habitat_baselines.evaluate=True \
    habitat_baselines.eval_ckpt_path_dir=data/checkpoints/${EXPERIMENT_NAME} \
    habitat_baselines.checkpoint_folder=data/checkpoints/${EXPERIMENT_NAME} \
    habitat_baselines.tensorboard_dir=data/tb/${EXPERIMENT_NAME} \
    habitat_baselines.video_dir=data/video/${EXPERIMENT_NAME} \
    habitat_baselines.num_updates=-1 \
    habitat_baselines.test_episode_count=3 \
    habitat_baselines.eval.video_option='["disk"]' \
    habitat_baselines.num_environments=3
