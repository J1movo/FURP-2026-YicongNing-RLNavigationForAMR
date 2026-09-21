# End-to-End Navigation for an AMR with Reinforcement Learning

> FURP 2026 · Research Track · University of Nottingham Ningbo China

## Project Info

| Field | Entry |
|---|---|
| Student | Yicong Ning |
| Project title | End-to-End Navigation for an AMR with Reinforcement Learning |
| Project tag | RLNavigationForAMR |
| Track | Research |
| Supervising faculty | FoSE |
| Project lead | Tianxiang Cui |
| Team or individual | Team |
| Cited papers | **DD-PPO: Learning Near-Perfect PointGoal Navigators from 2.5 Billion Frames** (Wijmans et al., ICLR 2020) — method and network architecture; **Habitat: A Platform for Embodied AI Research** (Savva et al., ICCV 2019) — simulator and PointNav task definition |

**One-line summary:** This project builds an end-to-end navigation policy for an Autonomous Mobile Robot (AMR) using reinforcement learning. Instead of hand-designed planning modules, the robot learns to go from sensor inputs (e.g., lidar/depth) and a goal position directly to control commands.

## Overview

Replicated the PointGoal PPO navigation baseline in Habitat on the Gibson dataset, and trained two models differing only in observation modality. The deployment pipeline to a WHEELTEC S100 differential-drive robot was then designed and its on-board inference verified.

| | RGBD | Depth-only |
|---|---|---|
| Input | RGB + depth (4 ch) | depth (1 ch) |
| Parameters | 5,821,797 | 5,817,093 |
| Success / SPL | 96.9% ± 0.5% / 86.4% ± 0.9% | **97.8% ± 0.3% / 89.9% ± 0.3%** |
| Dataset | Gibson (88 scenes) | Gibson (88 scenes) |
| Random seed | 42 | 42 |

**Key finding.** The TorchScript export pipeline was silently inconsistent with the trained model: the exported visual backbone never received its trained weights, gained an untrained downsampling branch, and was rebuilt with a different normalisation type and an extra recurrent layer. The defect raises no error, so the reported simulation metrics describe the original checkpoint rather than the artefact that was deployed. Full evidence chain and a reproducible verification script are in [`REPORT.md`](REPORT.md) §VII.A.

## Deliverables

| Item | Location |
|---|---|
| Final report | [`REPORT.md`](REPORT.md) |
| Environment & dependencies (training / deployment / simulation) | [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md) |
| Weekly logs, Weeks 1–8 (indexed) | [`docs/00_weekly.md`](docs/00_weekly.md) |
| ROS 1 deployment package (buildable with `catkin_make`) | [`src/deploy/s100_deploy/`](src/deploy/s100_deploy/) |
| Platform specification and robot media | [`src/deploy/wheeltec_s100/`](src/deploy/wheeltec_s100/) |
| Joint-phase materials (with provenance notice) | [`src/joint_phase/`](src/joint_phase/) |

## Repository structure

```
/docs                       weekly logs, meeting notes, environment notes
  ├── 00_weekly.md          index of all weekly logs
  ├── 01–06_weekly.md       Weeks 1–6 (per-week entries)
  ├── 07–08_weekly.md       Week 7 (deployment), Week 8 (write-up)
  ├── ENVIRONMENT.md        environment and dependencies
  └── meeting_notes/        one file per meeting
/src                        code, experiments, materials
  ├── lab1/ … lab6/         per-week experiment code
  ├── deploy/               deployment code
  │   ├── s100_deploy/      ROS 1 package (S100 / Jetson)
  │   ├── turtlebot3/       TB3 / D455 deployment line
  │   └── wheeltec_s100/    platform specification and robot media
  └── joint_phase/          joint-phase materials (see PROVENANCE.md)
REPORT.md                   final report
```

## Requirements

To earn the FURP certificate, all three must be satisfied:

1. Attend > 50% of programme activities.
2. Submit a poster as `FURP_Showcase.pdf` in the repo root.
3. Present at the Poster Showcase.

**Research Track minimum:** replicate a cited paper with at least 10% innovation. The three
innovations here are (i) systematic localisation of the TorchScript export defect with a
tensor-level evidence chain, (ii) a controlled dual-modality comparison under identical dataset,
hyperparameters and seed, and (iii) a two-process TCP-bridge simulation harness. See
[`REPORT.md`](REPORT.md) §I.C.

## Checklist

- [x] Forked the template and renamed the repo
- [x] Made the repo public **or** shared it with the research group
- [x] Filled in the *Project Info* table
- [x] Started `docs/00_weekly.md`
- [x] Created meeting notes in `docs/meeting_notes/`
- [ ] (By Showcase) Added `FURP_Showcase.pdf` to the repo root

> This project is delivered as a **written report** ([`REPORT.md`](REPORT.md)); no demo video or
> poster was produced. `FURP_Showcase_PLACEHOLDER.md` is the template placeholder and is kept
> until a poster is submitted.

---

*Bridging the gap between classroom knowledge and cutting-edge research.*
