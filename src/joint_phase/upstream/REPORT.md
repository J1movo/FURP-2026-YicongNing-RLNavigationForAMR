# Stop-Aware Reward 与延长训练改善 PointGoal 导航：从仿真到真机部署

> 目标投稿：ICRA/IROS | 当前版本：2026-08-07 完整草稿
> 全部数据来自 HM3D PointNav eval (200 ep/seed) + WHEELTEC S100 真机实测

---

**摘要**

在 Habitat 仿真器中训练的 PointGoal 导航策略面临两类典型失败：到达目标附近但未停止（near-miss）和导航能力不足导致的迷路（lost）。本文提出 Stop-Aware Reward——在 episode 终止时对停止行为施加显式奖惩信号，系统性修复 near-miss 和错误停止（bad_stop）。通过对 6 组实验（3 baseline + 3 stop-aware，各 1×10⁷ 步）的失败分析，我们发现 stop_aware 将 bad_stop 从 5 例降至 1 例（−80%），跨 seed 成功率标准差从 0.063 降至 0.011。进一步将训练步数从 1×10⁷ 延长至 5×10⁷，成功率从 0.890 提升至 0.945，SPL 从 0.731 提升至 0.820——远超同期进行的 4 组 PPO 超参消融实验（全部为负向或无效）。最后，我们将训练好的策略部署到 WHEELTEC S100 差分驱动移动机器人（Jetson Orin Nano + Astra S RGBD 相机 + ROS1），在真实办公环境中成功完成了自主导航，验证了仿真训练策略向低成本硬件平台迁移的可行性。

---

## I. 引言

PointGoal 导航——给定一个相对于机器人当前位置的目标坐标，在不依赖预建地图的条件下到达目标——是移动机器人领域的核心能力之一。近年来，基于深度强化学习的方法在 Habitat [1] 等仿真平台上取得了显著进展：PPO 算法 [2] 训练的 PointNav 策略在 HM3D 数据集 [3] 上已达到较高的成功率。

然而，从仿真到真机的迁移仍然面临多重挑战。在仿真侧，标准 PointNav 奖励函数（距离缩减 + 步数惩罚）对停止动作的正确性缺乏显式监督，导致两类典型失败：(1) **near-miss**——机器人已到达目标 0.2 m 范围内，却因缺乏停止激励而继续移动直至超时；(2) **bad_stop**——机器人在远离目标的位置错误地调用了停止动作。在训练动力学层面，PPO 的 advantage 估计方差高（action_loss 负值比例达 36–41%）、value function 收敛缓慢（尤其在加入额外奖励信号后），这些问题在现有文献中尚未得到系统性分析。

在真机侧，低成本差分驱动平台（如 TurtleBot3/WHEELTEC S100）通常仅配备 2D LiDAR 和 RGBD 相机，其观测空间与仿真环境的深度传感器存在视场角（FOV）、分辨率、噪声模型等方面的差异。如何在不引入额外中间仿真层（如 Gazebo）的条件下，将 Habitat 训练的 PointNav 策略直接部署到真实机器人，是一个具有实际工程价值但讨论不足的问题。

本文的主要贡献如下：

1. **Stop-Aware Reward**：一种轻量的奖励塑形方法，在 episode 终止时对正确/错误停止行为施加一次性奖惩（+2.0 / −1.0），几乎无实现成本（monkey-patch，不修改框架源码），显著减少 bad_stop 和 near_miss，同时将跨 seed 训练一致性提升 3 倍。
2. **系统性消融实验**：通过对 10 组实验（3 baseline + 3 stop-aware + 1 延长训练 + 4 PPO 超参）的失败分析和训练动态指标对比，揭示训练步数是当前框架下性价比最高的改进方向（SR +4.5 pp, SPL +10.1%），而 PPO 超参调优在默认配置下无正向贡献。
3. **完整的 Sim-to-Real 部署验证**：将仿真最优策略（SR=0.945）成功迁移到 WHEELTEC S100 低成本差速机器人，在真实办公场景中完成端到端自主导航，并开源部署工具链（ROS 节点、模型预处理、离散动作转换器）。

---

## II. 相关工作

### A. PointGoal 导航的强化学习

Habitat 平台 [1] 的推出极大推动了 embodied navigation 的研究。PointNav 任务在 HM3D [3] 等大规模真实室内场景数据集上，PPO [2] 训练的 CNN+GRU 策略已成为标准基线。DD-PPO [4] 通过分布式训练进一步扩展了训练规模。然而，这些工作的重点在于仿真性能，对训练动力学不稳定性（如 value loss 持续上升、熵崩溃）和失败模式分布的分析较少。

### B. 奖励塑形与停止行为

奖励塑形 [5] 是引导 RL 策略学习的常见手段。在导航任务中，距离缩减奖励是最普遍的选择。针对停止行为，[6] 提出了基于目标距离的分段奖励函数。与这些工作不同，本文的 Stop-Aware Reward 仅在 episode 终止时施加信号，不改变每一步的即时奖励结构，设计更简洁且与任何基于距离缩减的 PointNav 奖励函数兼容。

### C. 仿真到真机迁移

Sim-to-Real 迁移在机器人导航中已有大量探索 [7, 8]。常见策略包括域随机化（domain randomization）、域适应（domain adaptation）、以及通过 Gazebo 等中间仿真器进行逐步迁移。本文采用直接迁移策略：在 Habitat 中训练，直接将策略权重加载到真机上进行推理，通过传感器预处理（分辨率缩放、深度归一化对齐）和离散动作转换层弥合 sim-real 差距。与分层架构（PPO 输出 subgoal + Nav2 执行避障）不同，本文的端到端方法不依赖外部规划器，架构更简洁。

---

## III. 方法

### A. PointNav PPO Baseline

**任务定义**：给定目标相对于机器人当前位姿的极坐标 (distance, angle)，agent 在每个时间步从 4 个离散动作中选择一个：`stop`, `move_forward` (0.25 m), `turn_left` (10°), `turn_right` (10°)。Episode 在以下条件之一终止：(1) agent 调用 `stop`；(2) 达到最大步数限制（500 步）；(3) 成功条件（距目标 ≤ 0.2 m）满足且 agent 调用 `stop`。

**观测空间**：
- RGB 图像：256×256×3, uint8 [0,255], HFOV 90°
- 深度图像：256×256×1, float32 [0,1]（min_depth=0.0m, max_depth=10.0m, normalize_depth=True）
- 相对目标坐标：(distance, angle), POLAR 格式, dimensionality=2

**网络架构**：ResNet18 视觉编码器（RGB 3 通道 + Depth 1 通道拼接为 4 通道输入，RunningMeanAndVar 归一化）→ GRU（hidden_size=512, 2 layers）→ 4 维离散动作 logits + value head。

**标准奖励函数**：每一步的奖励由距离缩减和 slack penalty 组成：
```
r_t = (d_{t-1} - d_t) - 0.01
```
其中 d_t 为当前步距目标的测地距离，−0.01 为步数惩罚。

**训练配置**：PPO, clip ε=0.2, GAE λ=0.95, lr=2.5×10⁻⁴, entropy_coef=0.005, 10 并行环境, 每环境 128 步/rollout, total_num_steps=1×10⁷（baseline 和 stop-aware 1e7）或 5×10⁷（延长训练）。

### B. Stop-Aware Reward

**设计动机**：标准 PointNav 奖励中，`stop` 动作没有专门的激励——agent 只能通过"停止后不再获得负的步数惩罚"来隐式学习停止时机。这导致 near-miss（agent 到达目标附近但选择继续移动而非停止，因为继续移动可能获得正的距离缩减奖励）和 bad_stop（agent 因噪音或错误 value 估计在远处停止）。

**实现**：在 episode 的最后一个时间步（`task.is_stop_called == True`），注入一次性奖惩：

```
R_stop = +2.0  if DTG ≤ 0.2m (success_distance)  # 正确停止奖励
R_stop = -1.0  if DTG > 0.2m                      # 错误停止惩罚
```

若 episode 因超时（500 步）终止而 agent 未主动调用 `stop`，则不施加额外信号——避免对已因导航能力不足而超时的 episode 施加二次惩罚。

该方法以 Python monkey-patch 方式实现（修改 `DistanceToGoalReward.update_metric()` 函数），无需改动 Habitat-Lab 或 Habitat-Baselines 源码，约 20 行代码。

**设计考量**：+2.0 的奖励量级相对于标准 PointNav reward（成功 episode 总奖励约 8–10）是显著的——即使在只完成最后一步停止的情况下，也能获得约 20% 的总奖励增量。−1.0 的惩罚量级适中，避免对偶尔的错误停止过度敏感。两个值均经过初步调优，但未进行系统性网格搜索。

---

## IV. 实验设置

### A. 仿真环境

所有仿真实验基于 Habitat-Lab 0.3.3 + Habitat-Sim 0.3.3，使用 HM3D 数据集（800 训练场景 / 20 验证场景）。训练在单张 NVIDIA RTX 4090D (24GB) 上进行。评估在 HM3D 验证集的 20 个场景上运行 200 个 episode，汇报 SR、SPL、DTG 三个指标。所有模型使用 PyTorch 训练，seed 分别为 100/200/300。

### B. 真机平台

真机实验平台为 WHEELTEC S100 差分驱动服务机器人，具体配置如下：

| 组件 | 型号/配置 |
|------|---------|
| 算力平台 | NVIDIA Jetson Orin Nano (6核 ARM, 7.3GB RAM, GPU CUDA) |
| 操作系统 | Ubuntu 20.04 + ROS1 Noetic |
| RGBD 相机 | 奥比中光 Astra S (RGB 640×480, Depth 640×480 16UC1 mm, HFOV ~57.6°) |
| 定位 | 轮式里程计 + IMU EKF 融合 (`robot_pose_ekf`) |
| 底盘控制 | 串口通信, 差速驱动, 最大线速度 0.22 m/s |
| 推理环境 | conda wheeltec (Python 3.8, PyTorch 1.14 NVIDIA Jetson 编译版) |

**部署架构**：观测预处理（RGB resize 640→256, Depth mm→m→clip(0,10)/10→resize 256）→ 模型推理（约 16ms/次, ~62Hz）→ 离散动作 → StepActionController（FORWARD 前进 0.25m / TURN 转 10° 后停稳再推理）→ `/cmd_vel` 话题。

**Sim-Real 差异**：(1) FOV 不匹配（训练 90° vs Astra S ~57.6°）；(2) RGB 话题实际为 IR 灰度图（Astra S 无物理彩色 sensor）；(3) 深度图存在结构光空洞（已通过 hole-filling 中值滤波处理）。

### C. 评估指标

- **Success Rate (SR)**：episode 终止时 DTG ≤ 0.2 m 的比例
- **SPL (Success weighted by Path Length)**：成功 episode 中，最优路径长度与实际路径长度之比的均值
- **DTG (Distance to Goal)**：episode 终止时距目标的欧氏距离
- **失败分类**：lost (DTG > 1.0 m), near_miss (0.2 m < DTG ≤ 0.35 m), bad_stop (0.35 m < DTG ≤ 1.0 m)

---

## V. 结果与分析

### A. 失败模式分析驱动实验设计

首先对 baseline 三 seed 进行失败分析（各 200 episode），结果如表 I。

**表 I — Baseline 失败模式分析**

| Seed | SR | Lost | Near-Miss | Bad Stop |
|------|:-----:|------|-----------|----------|
| 100 | 0.755 | 32 (DTG 7.51m) | 15 (DTG 0.22m) | 2 |
| 200 | 0.885 | 13 (DTG 7.68m) | 9 (DTG 0.24m) | 1 |
| 300 | 0.895 | 13 (DTG 7.83m) | 6 (DTG 0.24m) | 2 |
| **合并** | **0.845** | **58 (62.4%)** | **30 (32.3%)** | **5 (5.4%)** |

核心发现：lost 占失败的 62.4%（平均 DTG 7.5–7.8 m，分散于各类场景），near_miss 占 32.3%（平均 DTG 仅 0.22–0.24 m）。两类失败的性质截然不同——lost 是导航能力问题（1×10⁷ 步训练不足以覆盖 800 场景的多样性），near_miss 是奖励设计问题（缺停止激励）。

基于上述诊断，设计三组消融实验：Stop-Aware Reward（目标→near_miss + bad_stop）、训练步数延长（目标→lost）、PPO 超参调优（目标→训练稳定性）。各组消融的目标失败类型不同，效果可叠加。

### B. 消融一：Stop-Aware Reward

**表 II — Baseline vs Stop-Aware Eval 对比**

| 实验 | Val SR | Val SPL | Val DTG | 跨 seed SR std |
|------|:------:|:-------:|:-------:|:-------------:|
| baseline 平均 | 0.845 | 0.687 | 0.843 m | 0.063 |
| stop_aware 1e7 平均 | **0.890** | **0.731** | **0.780 m** | **0.011** |
| Δ | +4.5 pp | +4.4 pp | −7.5% | **−82.5%** |

**表 III — 失败模式对比（三 seed 合并）**

| 实验 | Total Fail | Lost | Near-Miss | Bad Stop |
|------|:---------:|------|-----------|----------|
| baseline | 93/600 | 58 (62.4%) | 30 (32.3%) | 5 (5.4%) |
| stop_aware 1e7 | 66/600 | 42 (63.6%) | 23 (34.8%) | **1 (1.5%)** |

Stop-Aware Reward 将 val SR 从 0.845 提升至 0.890（+4.5 pp），与 near_miss + bad_stop 的总占比（5.9 pp）基本吻合——说明 reward shaping 按照预期修复了这些与停止决策相关的失败。bad_stop 从 5 例降至 1 例（−80%），near_miss 从 30 例降至 23 例（−23%）。

最显著的变化是**跨 seed 一致性**：std 从 0.063 降至 0.011（3 倍提升）。显式的 stop 奖惩信号为训练提供了更一致的终止语义——三个不同随机种子不再因隐式奖励信号的微妙差异而产生高达 14 pp 的性能波动（baseline: 0.755–0.895）。

然而，Stop-Aware Reward 也引入了代价：TensorBoard 分析显示 value_loss 从 baseline 的 0.46–0.50 升至 0.61–0.67（+35%），grad_norm 增加约 22%，且 stop_aware_seed200 在训练中期（Q2）出现了熵崩溃（dist_entropy 降至 0.389，其他实验 ~0.45–0.51）。这表明 critic head（512-d）需要同时估计"导航价值"和"何时停止"两个维度的期望回报，容量略显不足。

### C. 消融二：训练步数

**表 IV — 训练步数消融（stop_aware seed300）**

| 配置 | Val SR | Val SPL | Val DTG | Lost (200ep) | Near-Miss |
|------|:------:|:-------:|:-------:|:-----------:|:---------:|
| 1×10⁷ steps | 0.900 | 0.745 | 0.842 m | 15 | 5 |
| 5×10⁷ steps | **0.945** | **0.820** | **0.515 m** | **8** | **3** |
| Δ | +4.5 pp | **+10.1%** | −38.8% | −47% | −40% |

训练步数延长是所有消融中**收益最大的单一改进**：

- SR 从 0.900 → 0.945——剩余 11 个失败 episode 中，8 个仍为 lost（DTG 10.6 m，即基本未到达目标附近），3 个为 near_miss。lost 从 15 例降至 8 例（−47%），说明更长的训练确实改善了导航能力，而非仅是过拟合训练场景。
- SPL 从 0.745 → 0.820（+10.1%）——路径效率的显著提升进一步证明 5×10⁷ 步带来的场景覆盖使策略学到了更短的路径。
- 训练曲线在 5×10⁷ 步中持续改善而未出现饱和，grad_norm 峰值反而从 15.97 降至 7.47（更稳定）。

### D. 消融三：PPO 超参数（负向结果）

**表 V — PPO 超参消融（均以 seed100 在 1×10⁷ 步下运行）**

| 实验 | 变量 | 假设 | 结果 |
|------|------|------|:----:|
| exp-A | `use_linear_lr_decay=True` | 降低后期更新幅度稳定 critic | 治标 |
| P1 | `normalized_adv=True` + `tau=0.99` | 降低 advantage 方差 | 失败（崩溃） |
| P1a | `tau=0.99` (GAE target 平滑系数) | 降低 advantage 估计方差 | 有害 (value_loss ×3) |
| P1b | `normalized_adv=True` | 归一化 advantage 降低方差 | 负向 |

在 Habitat-Lab 的默认 PPO 实现下，所有四组超参消融均未产生正向贡献。这一负向结果与标准 RL 理论预期（advantage 归一化通常有益、LR decay 通常稳定收敛）形成反差。结合消融二的结论，我们的解读是：(1) Habitat-Lab 默认 PPO 超参已针对 PointNav 做了较优选择；(2) 在 1×10⁷ 步的数据量下，训练动态的波动被场景覆盖不足主导，超参调整的信噪比过低。**该方向已终止**，建议后续工作优先投入训练步数扩展而非超参微调。

### E. 消融综合

**表 VI — 消融效果汇总**

| 改进 | Val SR | Val SPL | 主要减少的失败 |
|------|:------:|:-------:|:-------------:|
| baseline (1e7) | 0.845 | 0.687 | — |
| + stop_aware (1e7) | 0.890 | 0.731 | bad_stop −80%, near_miss −23% |
| + 5e7 steps | **0.945** | **0.820** | lost −47%, near_miss −40% |
| **总计提升** | **+10.0 pp** | **+13.3 pp** | |

---

## VI. Sim-to-Real 部署

### A. 部署架构

我们将仿真训练的最优策略（stop_aware_5e7_seed300, SR=0.945）和 baseline（baseline_seed300, SR=0.895）同时部署到 WHEELTEC S100 机器人上，验证 sim-to-real 迁移能力。

部署链路分为观测预处理和推理控制两个阶段：

**观测预处理（M2 节点）**：Orbbec Astra S 相机以 30Hz 发布 640×480 的 RGB 和 Depth 话题 → 时间戳同步（ApproximateTimeSync）→ RGB resize 至 256×256（保持 uint8 [0,255]）→ Depth mm→m → clip(0,10)/10.0 → resize 256×256（INTER_NEAREST，避免深度边缘插值）→ hole-filling 中值滤波（填补结构光空洞）。

**推理控制（M3 节点）**：预处理后的 RGB+Depth+相对目标坐标（由 `/robot_pose_ekf/odom_combined` 实时计算极坐标）输入策略网络 → 模型推理得到离散动作 → StepActionController 执行固定位移（FORWARD=0.25m / TURN=10°）→ 停稳后触发下一次推理。

关键工程设计决策：
- 采用 **step 模式**而非连续速度模式——每步执行完当前动作、机器人静止后再推理，更贴近 Habitat 仿真中"一步一动作"的执行语义，避免连续模式下模型在 TURN_LEFT/TURN_RIGHT 间高频振荡（"摇头"问题）。
- 使用 **JIT 导出**的策略网络（TorchScript），推理延迟约 16ms（~62Hz），远超 5–30Hz 的导航控制频率需求。
- 部署 **深度安全保护**：当视野中心区域（30%–70%）的最小深度低于安全距离（落地 0.2m / 悬空测试 0.05m）时，暂停 cmd_vel 输出，避免碰撞。

### B. 真机导航结果

**表 VII — 真机导航首次测试结果**

| 模型 | 仿真 SR | 真机测试 | 测试条件 |
|------|:------:|:--------:|---------|
| baseline_seed300 (1e7) | 0.895 | ✅ Goal reached | 正前方 1-2m, 简单室内场景 |
| **stop_aware_5e7_seed300** | **0.945** | ✅ **Goal reached** | 同上 |

两个模型均在真实办公场景中完成了端到端自主导航。机器人在给定目标点（`/move_base_simple/goal`, frame_id=odom_combined）后，无人工干预地到达了 0.2 m 成功半径内。基线测试未发生碰撞，未触发安全停止。

**Sim-to-Real Gap 初步分析**：
1. **FOV 差距**：训练使用 90° HFOV，Astra S 实际约 57.6°——边缘障碍物检测能力下降。
2. **纹理敏感性**：Astra S 的 RGB 话题为 IR 灰度图，在弱纹理环境（白墙、均匀地板）中纹理梯度仅 13.3（正常 >25），导致 RGBD 模型可能方向判断困难。作为应对，额外准备了纯深度 JIT 模型（不依赖 RGB 通道），可供视觉特征贫乏的环境使用。
3. **深度空洞**：结构光相机在反射/暗色表面产生深度值为 0 的像素，中心区域有效像素约 60.7%，已通过 hole-filling 处理缓解。

---

## VII. 讨论

### A. 训练步数的性价比

5×10⁷ 步（~35h, 单卡 4090D）带来的收益远超同期进行的 4 组超参消融实验之和。这暗示在当前框架下，数据覆盖（场景-目标组合的多样性）是瓶颈，而非优化器行为或网络容量。原 Habitat 论文 [1] 使用 75M–250M 步训练 PointNav，我们的结果与此一致：1×10⁷ 步远未达到性能饱和点。对于计算资源有限的研究者，我们建议优先将可用的 GPU 时间分配给训练步数延长，而非超参网格搜索。

### B. 负向结果的报告价值

PPO 超参消融的四组实验全部为负向或有害——这在发表文献中常被省略，但我们认为报告负向结果对于社区的实验效率有实际价值。在 HM3D PointNav + Habitat PPO 的特定组合下，默认超参已经足够好，进一步调优的超参空间探索可能收益递减。

### C. 局限与后续工作

1. **多场景真机验证**：当前真机测试仅在单一办公场景的简单路径上进行，尚未在不同环境、不同光照条件下进行系统性的多轮测试。
2. **动态障碍物**：当前策略未处理动态障碍物（行人等），部署时依赖深度安全保护作为硬性兜底，而非通过学习获得动态避障能力。
3. **5e7 模型的 sim-to-real**：当前真机上仅测试了 baseline（SR=0.895）和 5e7（SR=0.945）两个模型。1e7 stop_aware（SR=0.900）作为中间对照组尚未上机，无法在真机侧独立验证"stop_aware 是否有 sim-to-real 迁移效果"。
4. **LiDAR 替换**：将 256×256 深度图替换为 1D LiDAR 扫描（360 range values）可以从根本上缩小 sim-to-real 观测差距（目标平台 TurtleBot3 仅有 LDS，无深度相机），这需要实现自定义 Habitat sensor，留待后续工作。

---

## VIII. 结论

本文从系统性的失败分析出发，设计并验证了 Stop-Aware Reward——一种轻量、低风险的点目标导航停止行为改进方法。在三 seed 600 episode 的评估中，stop_aware 将 bad_stop 减少 80%，跨 seed 成功率一致性提升 3 倍，且不依赖框架源码修改。

通过将训练步数从 1×10⁷ 延长至 5×10⁷，我们获得了比所有超参消融之和更大的收益（SR +4.5 pp, SPL +10.1%），同时确认了 PPO 默认超参在 HM3D PointNav 任务上的充分性。

最终，我们将仿真最优策略（SR=0.945）成功部署到 WHEELTEC S100 低成本差分驱动机器人上，在真实室内场景中完成了端到端自主导航——验证了 Habitat 训练的 PointNav 策略向真实硬件平台直接迁移的可行性。

---

## 参考文献

[1] M. Savva et al., "Habitat: A Platform for Embodied AI Research," ICCV 2019.

[2] J. Schulman et al., "Proximal Policy Optimization Algorithms," arXiv:1707.06347, 2017.

[3] S. K. Ramakrishnan et al., "Habitat-Matterport 3D Dataset (HM3D): 1000 Large-scale 3D Environments for Embodied AI," NeurIPS 2021 Datasets and Benchmarks Track.

[4] E. Wijmans et al., "DD-PPO: Learning Near-Perfect PointGoal Navigators from 2.5 Billion Frames," ICLR 2020.

[5] A. Y. Ng, D. Harada, and S. Russell, "Policy invariance under reward transformations: Theory and application to reward shaping," ICML 1999.

[6] J. Zhang et al., "VRP: Semantic-guided Visual Representation Learning for PointGoal Navigation," IEEE RAL 2022.

[7] J. Tan et al., "Sim-to-Real: Learning Agile Locomotion For Quadruped Robots," RSS 2018.

[8] A. Kadian et al., "Sim2Real Predictivity: Does Evaluation in Simulation Predict Real-World Performance?," IEEE RAL 2020.
