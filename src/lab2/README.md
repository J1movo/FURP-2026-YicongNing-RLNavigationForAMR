# PointNav PPO Baseline

## Model Summary

| Item | Value |
|------|-------|
| Architecture | ResNet18 + GRU (Policy) |
| Parameters | 5,821,797 |
| Algorithm | PPO (Proximal Policy Optimization) |
| Sensors | RGB (256×256) + Depth (256×256) + GPS+Compass (2D) |
| Actions | 4 discrete: stop, forward, left, right |
| Base config | `ppo_pointnav.yaml` (Habitat ICCV 2019 hyperparams) |

## Final Checkpoint

| File | Step | Size |
|------|------|------|
| `ckpt.43.pth` (latest) | ~32.4M | 23 MB |
| `latest.pth` | ~32.4M | 23 MB |
| Full checkpoint dir | 45 checkpoints | 1.1 GB |

**Path:** `habitat-lab/data/checkpoints/baseline_pointnav_gibson/`

## Final Metrics

Reported as **average of last 10 checkpoints** (stable plateau, low variance):

| # | Step | Success | SPL | Reward | Dist to Goal |
|---|------|:------:|:----:|:------:|:------------:|
| 1 | 32,412,672 | 96.1% | 84.8% | 6.48 | 0.18 m |
| 2 | 32,406,528 | 96.1% | 85.1% | 6.50 | 0.20 m |
| 3 | 32,402,688 | 96.3% | 85.5% | 6.42 | 0.19 m |
| 4 | 32,399,616 | 97.1% | 86.3% | 6.59 | 0.15 m |
| 5 | 32,397,312 | 97.2% | 86.7% | 6.55 | 0.14 m |
| 6 | 32,395,008 | 97.5% | 86.7% | 6.55 | 0.15 m |
| 7 | 32,389,632 | 97.4% | 86.9% | 6.68 | 0.12 m |
| 8 | 32,388,096 | 97.2% | 87.0% | 6.68 | 0.12 m |
| 9 | 32,387,328 | 97.2% | 87.1% | 6.66 | 0.14 m |
| 10 | 32,385,024 | 97.2% | 87.6% | 6.71 | 0.16 m |
| **Avg ± Std** | | **96.9% ± 0.5%** | **86.4% ± 0.9%** | **6.58 ± 0.09** | **0.15 ± 0.03 m** |

| Summary | Value |
|--------|-------|
| Training steps | 32,412,672 / 75,000,000 (43%) |
| Peak Success | 99.0% |
| Peak SPL | 91.5% |
| Std < 1% → converged | ✅ Stable plateau |

## Evaluation Videos

- **134 videos** across 43 checkpoints (3 episodes/checkpoint)
- **121 success / 13 fail** (90.3% eval success rate)
- Saved at: `habitat-lab/data/video/baseline_pointnav_gibson/`

## Environment

| Item | Value |
|------|-------|
| Habitat-Sim | 0.3.3 (conda pre-built) |
| Habitat-Lab | 0.3.3 (editable pip) |
| PyTorch | 2.8.0+cu128 |
| GPU | RTX 3060 (12 GB) |
| Python | 3.9.25 |
| Seed | 42 |

## Reproducibility

```bash
conda activate habitat
cd /home/jimovo/Desktop/FURP/habitat-lab
python -u -m habitat_baselines.run \
    --config-name=pointnav/ppo_pointnav \
    habitat.seed=42 \
    habitat.simulator.scene_dataset=data/scene_datasets/gibson/gibson.scene_dataset_config.json \
    habitat_baselines.checkpoint_folder=data/checkpoints/baseline_pointnav_gibson \
    habitat_baselines.eval_ckpt_path_dir=data/checkpoints/baseline_pointnav_gibson \
    habitat_baselines.evaluate=True \
    habitat_baselines.test_episode_count=-1 \
    habitat_baselines.num_updates=-1
```

## Patches Applied

- `habitat-baselines/habitat_baselines/rl/ddppo/ddp_utils.py:224` — `weights_only=False`
- `habitat-baselines/habitat_baselines/rl/ppo/ppo_trainer.py:341` — `weights_only=False`
