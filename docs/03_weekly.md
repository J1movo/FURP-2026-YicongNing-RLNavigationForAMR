### Week 3 — 2026-06-28

**Attended this week's meeting:** Yes

**Progress this week**
- Downloaded **Gibson scene dataset** (88 scenes, 1.5 GB) and **PointNav Gibson v1 episode dataset** (385 MB).
- Set up data symlinks and scene dataset config (`gibson.scene_dataset_config.json`) per official Habitat DATASETS.md.
- Created experiment directory at `src/experiments/baseline_pointnav/`:
  - `train.sh` — full PPO training (75M steps, ResNet18, Gibson)
  - `eval_video.sh` — checkpoint evaluation with video recording
  - `quick_test.sh` — 1000-step smoke test
  - `configs/` — config backup for reproducibility
- **PointNav PPO baseline training completed** on Gibson dataset:
  - Model: ResNet18 + GRU (5.82M params), GPU: RTX 3060 (12 GB)
  - Config: `ppo_pointnav.yaml` (Habitat ICCV 2019 hyperparameters), 5 parallel envs
  - Trained to 32.4M steps, **converged at 96.1% Success, 84.8% SPL**
  - Peak: Success 99.0%, SPL 91.5%. 45 checkpoints saved.

| Metric | Start | Final |
|--------|-------|-------|
| Reward | -0.04 | 6.48 |
| Success | 0% | 96.1% |
| SPL | 0% | 84.8% |
| Distance to goal | 7.08 m | 0.18 m |

- Fixed **PyTorch 2.8 compatibility** — `weights_only=True` breaks Habitat checkpoint loading. Patched `ddp_utils.py:224`, `ppo_trainer.py:341`.
- Resolved **EGL multi-env instability**: forced NVIDIA EGL (`__EGL_VENDOR_LIBRARY_FILENAMES`), env count tuned 6→3→5 (stable).
- Set up **cron watchdog** for auto-restart on process crash (without auto-start on reboot).

**Challenges & blockers**
- 6-env EGL initialization crashes GPU driver — resolved by forcing NVIDIA EGL vendor.
- PyTorch 2.8 incompatible with Habitat 0.3.3 checkpoints — manually patched.
- Terminal instability — solved with `nohup` + cron watchdog.

**Next steps**
- Attempt model deployment to real robot (Orange Pi): export standalone model + inference code, integrate with ROS 2.
- Consider retraining a Depth-only model (drop RGB, use `depth_agent` config) for radar-based deployment.

**Hours spent (optional):** 12h

**Links (optional):**
- Experiment scripts: `src/experiments/baseline_pointnav/`
- Config backup: `src/experiments/baseline_pointnav/configs/`
- Checkpoints: `habitat-lab/data/checkpoints/baseline_pointnav_gibson/` (45 saved)
- Videos: `habitat-lab/data/video/baseline_pointnav_gibson/`
- TensorBoard: `habitat-lab/data/tb/baseline_pointnav_gibson/`