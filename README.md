# FURP Project Repository

> **Faculty Undergraduate Research Practice (FURP)**
> Undergraduate Research Group · Faculty of Science and Engineering · University of Nottingham Ningbo China

End-to-end navigation for an Autonomous Mobile Robot (AMR) with reinforcement learning.
FURP 2026 · Research Track.

---

## Project Info

| Field | Your entry |
|---|---|
| Student name(s) | Yicong Ning |
| Project title | End-to-End Navigation for an AMR with Reinforcement Learning |
| Project tag | RLNavigationForAMR |
| Track | Research |
| Supervising faculty | FoSE |
| Project lead | Tianxiang Cui |
| Team or individual | Team |
| Cited paper being replicated | **DD-PPO: Learning Near-Perfect PointGoal Navigators from 2.5 Billion Frames** (Wijmans et al., ICLR 2020, [arXiv:1911.00357](https://arxiv.org/abs/1911.00357)) — 复现其方法与网络结构；**Habitat: A Platform for Embodied AI Research** (Savva et al., ICCV 2019, [arXiv:1904.01201](https://arxiv.org/abs/1904.01201)) — 复现其仿真平台与 PointNav 任务定义 |

**One-line summary:** This project builds an end-to-end navigation policy for an Autonomous Mobile Robot (AMR) using reinforcement learning. Instead of hand-designed planning modules, the robot learns to go from sensor inputs (e.g., lidar/depth) and a goal position directly to control commands.

---

## 项目概览

在 Habitat 仿真环境中复现 PointGoal PPO 导航基线，训练两个仅观测模态不同的对照模型，
并完成向 WHEELTEC S100 真机平台的部署链路设计。

| | RGBD 模型 | Depth-only 模型 |
|---|---|---|
| 输入 | RGB + 深度（4 通道） | 深度（1 通道） |
| 参数量 | 5,821,797 | 5,817,093 |
| 成功率 / SPL | 96.9% ± 0.5% / 86.4% ± 0.9% | **97.8% ± 0.3% / 89.9% ± 0.3%** |
| 数据集 | Gibson（88 场景） | Gibson（88 场景） |
| 随机种子 | 42 | 42 |

**核心发现**：在核查部署产物时发现 TorchScript 导出链路存在**静默的架构不一致** ——
导出件的视觉主干从未载入训练权重、多出一个未训练分支、GRU 层数被错误构造。该缺陷不报错，
却使报告的仿真指标与实际运行的产物脱钩。完整证据链与可复现脚本见报告 §VII.A。

### 交付物索引

| 交付物 | 位置 |
|---|---|
| **期末报告**（含方法、结果、部署、失败分析、证据清单） | [`REPORT.md`](REPORT.md) |
| 环境与依赖说明（训练 / 部署 / 仿真三条链路） | [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md) |
| 周记（Week 1–8，含周记索引） | [`docs/00_weekly.md`](docs/00_weekly.md) |
| ROS 1 部署包（可直接 `catkin_make`） | [`src/deploy/s100_deploy/`](src/deploy/s100_deploy/) |
| 部署平台资料与真机素材 | [`src/deploy/wheeltec_s100/`](src/deploy/wheeltec_s100/) |
| 合作阶段材料（含出处声明） | [`src/joint_phase/`](src/joint_phase/) |

---

## Repository structure

This structure is **mandatory** — please keep it intact.

```
/docs                          ← 周记、会议记录、环境说明
 ├── 00_weekly.md              ← 周记索引
 ├── 01–06_weekly.md           ← Week 1–6（按周记录）
 ├── 07–08_weekly.md           ← Week 7（部署阶段）、Week 8（期末整理）
 ├── ENVIRONMENT.md            ← 环境与依赖说明
 └── meeting_notes/            ← 每次会议的要点与待办
/src                           ← 代码、实验、材料
 ├── lab1/  …  lab6/           ← 按周划分的实验代码
 ├── deploy/                   ← 部署代码
 │   ├── s100_deploy/          ← ROS 1 部署包（S100 / Jetson）
 │   ├── turtlebot3/           ← TB3 / D455 部署线
 │   └── wheeltec_s100/        ← 平台规格文档与真机素材
 └── joint_phase/              ← 合作阶段材料（含 PROVENANCE.md）
REPORT.md                      ← 期末报告
```

- **`docs/00_weekly.md`** — 周记索引。这是评审最先看的内容。
- **`docs/meeting_notes/`** — 每次会议一个文件，记录要点与待办。
- **`src/`** — 全部代码、脚本与实验材料。
- **`REPORT.md`** — 期末报告（本项目以报告形式交付，见下方说明）。

---

## The three rules for your certificate

To earn your FURP certificate, **all three** must be satisfied:

1. **Attend > 50%** of programme activities (weekly meetings, workshops, scheduled sessions — online or in person).
2. **Submit a poster** — place it as `FURP_Showcase.pdf` in this repo root.
3. **Present at the Poster Showcase** — in person (strongly preferred), or send a stand-in if you truly cannot attend.

> Miss any one of the three, and the certificate is not awarded this round.

**Research Track — minimum for certification:** successful replication of a cited paper with at least **10% innovation** (reproduce the work *and* add something new).

本项目的创新点：① TorchScript 导出缺陷的系统定位（张量级证据链 + 可复现验证脚本）；
② 受控条件下的双模态对比实验；③ Gazebo TCP bridge 仿真测试架构。详见报告 §I.C。

---

## Weekly cadence

Every week, you should:

- ✅ Update [`docs/00_weekly.md`](docs/00_weekly.md)
- ✅ Log meeting notes in [`docs/meeting_notes/`](docs/meeting_notes/)
- ✅ Attend the weekly meeting (online or in person)

Consistent weekly engagement is the backbone of a successful FURP project — and it feeds directly into your attendance (Rule 1).

---

## Leave & withdrawal

Any **leave of absence** or **withdrawal** must be notified to us **by email** — a verbal or chat message is not sufficient.

- **Leave:** email *before* the session where possible, state the date(s) and reason. Note that leave still counts against the >50% attendance rule.
- **Withdrawal:** email us to formally withdraw so we can free your project slot and update records.
- **Switching tracks:** email the project lead with the subject *"Project Transfer Request"* and CC your supervising faculty member.

> No email = no record. Always put leave and withdrawal in writing.

---

## Quick checklist

- [x] Forked the template and renamed the repo
- [x] Made the repo public **or** shared it with the research group
- [x] Filled in the *Project Info* table above
- [x] Started `docs/00_weekly.md`
- [x] Created meeting notes in `docs/meeting_notes/`
- [ ] (By Showcase) Added `FURP_Showcase.pdf` to the repo root

> **关于交付形式**：本项目按作者决定以**书面报告**（[`REPORT.md`](REPORT.md)）形式交付，
> 未制作演示视频与海报。仓库根目录的 `FURP_Showcase_PLACEHOLDER.md` 为模板占位文件，
> 在未提交 `FURP_Showcase.pdf` 前保留。

---

*Bridging the gap between classroom knowledge and cutting-edge research.*
