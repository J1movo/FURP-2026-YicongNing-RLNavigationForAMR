# 真机部署 — 目标

> 本文件与本目录下的 `02-tech-stack.md`、`03-roadmap.md` 共同构成本项目「真机部署」阶段的统一规范。
> 所有 Claude 实例在处理本目录相关任务时，应先读取这三份文件建立一致认知，再展开具体工作。

## 一句话目标

把已经训练好的、端到端（观测 → 动作）的 PointGoal PPO 导航强化学习策略，部署到 WHEELTEC S100 差速服务机器人上，让它在真实环境中跑通。

## 具体部署对象（已锁定，2026-08-02 确认）

`D:\AMR-Navigation-Project\autodl\exp\baseline_seed300\checkpoints\ckpt.49.pth`
（等价文件：`D:\AMR-Navigation-Project\autodl\ckpt.49.pth`，MD5 一致，确认是同一份）

- 训练配置：`pointnav/ppo_pointnav.yaml` + `benchmark/nav/pointnav=pointnav_hm3d` 覆盖，数据集为 **HM3D**（`data/scene_datasets/hm3d/val/...`，真实大规模室内场景数据集），非流程验证性质的小场景 baseline。
- 训练规模：`total_num_steps=1e7`（1000万步，`checkpoint_folder=baseline_seed300` 下有两次训练记录，分别配置 5e7 和 1e7，实际产出该 ckpt.49 的是 1e7 这次），seed=300，"baseline" 实验臂（不含 stop-aware reward patch）。
- 评估结果（`autodl/exp/baseline_seed300/failure_analysis.json`，200 episodes，HM3D val）：success_rate = **0.895**，成功案例平均到目标点距离误差约 0.10m。失败细分：bad_stop 2例、near_miss 6例、lost（迷路/超时）13例。
- 策略结构：`PointNavResNetPolicy`（ResNet18 图像编码器 + GRU）。
- 判定「成功抵达目标」的阈值（来自训练配置 `success_distance`）：**0.2m**。

## 背景与定位

- 这是「模型部署队列」的第一个模型：先把 PointGoal PPO 在 S100 上完整走通一遍（从模型文件到能在真机上执行），验证整条部署链路可行。
- 后续会有更多训练好的模型（`autodl/exp` 下同批次训练的 `baseline_seed100`/`baseline_seed200`/`stop_aware_seed100` 等，以及未来引入 Transformer 等结构的策略）依次沿用同一条部署链路上机验证。本次目标只覆盖上述这一个 checkpoint，但产出的 ROS 节点/部署流程应尽量可复用给后续模型。
- 本阶段**不包含**：重新训练、微调模型、针对真机做策略参数调整。策略权重视为冻结（frozen），不在本阶段改动。

## 执行方式（本次模型的关键约束 —— 已订正，2026-08-02）

- **该 PointGoal PPO 是离散动作空间策略，不是连续 cmd_vel 输出。** 策略每一步从 `{stop, move_forward, turn_left, turn_right}` 四个离散动作中选一个（`action_distribution_type: categorical`），对应固定的运动量：`forward_step_size: 0.25`（每次前进0.25米）、`turn_angle: 10`（每次转向10度）。
  - 这与此前版本文档中「模型直接输出线速度+角速度」的记录**不一致，现已订正**。若之前读过旧版本文档或据此做过设计假设，需要重新核对。
- 因此真机部署链路中必须新增一层**「离散动作 → 底盘执行」的转换逻辑**，而不是把网络输出直接当作 cmd_vel 数值使用。转换方式待设计，两种候选思路：
  1. 每次推理得到一个离散动作后，直接换算成一段短时间的 `cmd_vel` 指令（如 move_forward → 以某固定线速度持续行驶至累计0.25m再停止，issue 下一次推理；turn_left/right → 原地旋转固定10度）。
  2. 封装成「离散步进指令」执行，每步执行完当前动作、机器人静止后再触发下一次推理（更贴近 habitat 仿真里「一步一动作」的执行节奏，实现更简单但整体导航会偏慢、走走停停）。
  - 采用哪种方式待 M2/M3 阶段结合实测延迟与体验决定，本文件届时更新。
- 不经过 Nav2 局部规划/避障，不输出 subgoal——这一点仍然成立，「离散动作直接驱动底盘」与「PPO 输出 subgoal + Nav2 负责局部执行/避障」的分层架构（此前记忆中的预案）依然是两回事，本次不采用后者。若后续要加一层 Nav2 安全兜底（例如限速/紧急避障），需另行讨论并在本文件更新说明，不默认启用。

## 模型的 Observation 输入（决定传感器需求）

策略训练时的观测空间（**2026-08-02 订正**：M1 阶段实机加载 checkpoint 时报出网络第一层输入通道数不匹配的错误，回查 config.yaml 发现训练时实际用了 RGB+Depth 双路视觉输入，此前文档记录的"只有深度相机"是错误的）：

1. **RGB 图像**——256×256，hfov 90°，`HabitatSimRGBSensor`，uint8 [0,255]。
2. **深度相机图像**（Depth camera）——256×256，hfov 90°，min_depth 0.0m / max_depth 10.0m，`normalize_depth: true`（训练时深度值归一化到 [0,1]，真机深度相机原始输出通常是米或毫米，接入前需按同样方式归一化）。
3. **相对目标坐标**（`PointGoalWithGPSCompassSensor`，`goal_format: POLAR`，`dimensionality: 2`）——极坐标形式的相对目标：距离 + 角度，等价于 Habitat 的 GPS+Compass 信息。

网络会把 RGB(3通道) + Depth(1通道) 拼接成 4通道输入喂进 ResNet18 视觉编码器第一层卷积，且因为存在 RGB 输入，`normalize_visual_inputs=True`（对应 `RunningMeanAndVar` 归一化层，训练时统计的均值/方差也打包在 checkpoint 里，加载时需要一并还原，不能只加载卷积层权重）。

因此真机部署必须给 S100 提供：
- **一路RGB图像 + 一路深度图像**（不是只有深度），分辨率/FOV/深度范围/归一化方式需与上述参数对齐。S100 的奥比中光 Astra S 本身就是 RGB-D 相机，硬件上同时支持这两路输出，不需要额外加相机，但驱动/ROS节点需要同时订阅两个话题。
- 一个能实时计算「机器人当前位姿 → 目标点」相对距离和角度（极坐标）的定位来源——S100 已有 `robot_pose_ekf`（轮式里程计+IMU融合）可直接使用，详见 `02-tech-stack.md`。

## 成功标准（跑通的定义）

一次部署尝试被视为「跑通」，需同时满足：

1. **到达目标**：给定一个真实环境中的目标点（pointgoal），机器人在没有人工干预（无遥控介入、无中途手动纠偏）的情况下，依靠 PPO 策略推理（离散动作 → 转换为底盘执行）驱动底盘，实际到达目标点半径 **0.2m** 以内（`success_distance=0.2`，与训练时评估标准一致）。
2. **零碰撞**：全程不与障碍物/墙体/人发生碰撞。
3. **无人工干预**：从下发目标点到抵达目标点的整个过程，不允许人工介入控制。

达不到以上三点的尝试记为失败，需要记录失败原因（如：观测对齐问题、坐标系转换错误、推理延迟过高、传感器数据缺失、离散动作转换执行误差累积等），但不要求本阶段解决所有失败模式——先以「跑通一次完整链路」为最低目标，再逐步提高稳定性。参考训练时的失败模式分布（`failure_analysis.json`）：bad_stop（提前/错误停止）、near_miss（接近但未进入成功半径）、lost（长时间偏离/超时未达）——真机测试中出现类似问题时可对照排查。

## 待确认/待补充项

- [x] 训练时深度相机的具体参数 → 256×256, hfov 90°, min_depth 0.0m, max_depth 10.0m, normalize_depth true
- [x] 相对目标坐标的具体定义 → 极坐标（距离+角度），2维，来自 `PointGoalWithGPSCompassSensor`
- [x] 到达目标的误差阈值具体数值 → 0.2m（`success_distance`）
- [ ] 测试场地范围与障碍物复杂度（走廊 or 开放房间 or 含动态障碍）——真机测试场地与 HM3D 训练场景（真实住宅/室内扫描场景）的差异需要现场评估，室内布局、障碍物密度、光照条件都可能影响深度相机质量和策略泛化效果
- [ ] 离散动作转换为底盘执行的具体实现方式（见上方"执行方式"两种候选思路，待 M2/M3 阶段确定）
