# PointNav PPO Depth-Only Baseline

## Model Summary

| Item | Value |
|------|-------|
| Architecture | ResNet18 + GRU (Policy) |
| Parameters | 5,817,093 |
| Algorithm | PPO (Proximal Policy Optimization) |
| Sensors | Depth (256×256) + GPS+Compass (2D) |
| Actions | 4 discrete: stop, forward, left, right |
| Base config | `ppo_pointnav_depth_only.yaml` (Habitat ICCV 2019 hyperparams) |

## Final Checkpoint

| File | Step | Size |
|------|------|------|
| `ckpt.99.pth` (latest) | ~75M | 23 MB |
| Full checkpoint dir | 100 checkpoints | ~2.3 GB |

**Path:** `habitat-lab/data/checkpoints/depth_only_pointnav_gibson/`

## Final Metrics

Reported as **average of last 10 checkpoints** (stable plateau, low variance):

| # | Step | Success | SPL | Reward |
|---|------|:------:|:----:|:------:|
| 1 | 74,996,736 | 98.1% | 90.4% | 7.57 |
| 2 | 74,996,224 | 98.1% | 90.2% | 7.57 |
| 3 | 74,995,712 | 98.1% | 90.3% | 7.56 |
| 4 | 74,995,200 | 97.9% | 90.1% | 7.54 |
| 5 | 74,994,688 | 97.9% | 89.7% | 7.51 |
| 6 | 74,994,176 | 97.6% | 89.7% | 7.45 |
| 7 | 74,993,664 | 97.4% | 89.5% | 7.46 |
| 8 | 74,993,152 | 97.4% | 89.6% | 7.46 |
| 9 | 74,992,640 | 97.5% | 89.6% | 7.48 |
| 10 | 74,992,128 | 97.7% | 89.6% | 7.49 |
| **Avg ± Std** | | **97.8% ± 0.3%** | **89.9% ± 0.3%** | **7.51 ± 0.05** |

| Summary | Value |
|--------|-------|
| Training steps | 74,992,128 / 75,000,000 (100%) |
| Peak Success | 100.0% |
| Peak SPL | 95.6% |
| Std < 0.4% → converged | ✅ Stable plateau |

## Comparison with RGBD Baseline

| | RGBD | Depth-Only | Δ |
|------|:------:|:--:|:--:|
| Success | 96.9% ± 0.5% | **97.8% ± 0.3%** | +0.9% |
| SPL | 86.4% ± 0.9% | **89.9% ± 0.3%** | +3.5% |
| Input | RGB + Depth | Depth only | — |
| Training steps | 32.4M | 75M | — |

## Environment

| Item | Value |
|------|-------|
| Habitat-Sim | 0.3.3 (conda pre-built) |
| Habitat-Lab | 0.3.3 (editable pip) |
| PyTorch | 2.8.0+cu128 |
| GPU | RTX 3060 (12 GB) |
| Python | 3.9.25 |
| Seed | 42 |
| Sensor config | `depth_agent` (1-channel input) |

## Reproducibility

```bash
conda activate habitat
cd /home/jimovo/Desktop/FURP/habitat-lab
python -u -m habitat_baselines.run \
    --config-name=pointnav/ppo_pointnav_depth_only \
    habitat.seed=42 \
    habitat.simulator.scene_dataset=data/scene_datasets/gibson/gibson.scene_dataset_config.json \
    habitat_baselines.checkpoint_folder=data/checkpoints/depth_only_pointnav_gibson \
    habitat_baselines.eval_ckpt_path_dir=data/checkpoints/depth_only_pointnav_gibson \
    habitat_baselines.evaluate=True \
    habitat_baselines.test_episode_count=-1 \
    habitat_baselines.num_updates=-1
```

## Patches Applied

- `habitat-baselines/habitat_baselines/rl/ddppo/ddp_utils.py:224` — `weights_only=False`
- `habitat-baselines/habitat_baselines/rl/ppo/ppo_trainer.py:341` — `weights_only=False`
