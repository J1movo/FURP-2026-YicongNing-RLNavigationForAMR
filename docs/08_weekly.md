### Week 8 — 2026-09-21（期末材料整理与报告撰写）

**Attended this week's meeting:** Yes

**Progress this week**

- **期末报告撰写**（`REPORT.md`）。汇总前期 Gibson 双模型训练与后期真机部署两个阶段，按 FURP 研究轨道要求组织：复现论文、方法、实验设置、结果、部署、失败分析、结论。

- **发现并定位 TorchScript 导出缺陷**。在核查部署产物时，对导出的 `policy_depth_jit.pt` 与训练 checkpoint `ckpt.99.pth` 做**逐张量比对**，发现二者不一致：

  | 张量 | 训练后 | 导出件 | 结论 |
  |---|---|---|---|
  | `conv1.weight` | std 0.1958 | std 0.0829（均匀 ±1/7） | **默认随机初始化** |
  | `bn1` | γ 已训练 | 全为默认值 | **默认初始化** |
  | GRU 层数 | 1 | **3** | `_l1`/`_l2` 无训练对应物 |
  | `visual_fc` / `action_head` / `gru._l0` | — | 逐位相同 | 正确载入 |
  | 总参数量 | 5,817,093 | **8,969,540** | 多出 3,152,447 |

进一步全量搜索确认：**训练后的 `conv1` 在整个导出文件中根本不存在**。该缺陷静默不报错，却使对外报告的仿真指标与实际运行的模型脱钩，并可解释 Week 6/7 真机测试中观察到的动作震荡与抖动。详见 `REPORT.md` §VII.A，附可一键复现的验证脚本。

- **合作阶段材料整理**。建立 `src/joint_phase/`，收录合作者仓库（Zhihao Chen）的评估数据、图表与演示片段，并撰写 `PROVENANCE.md` 声明出处、许可证（MIT）与使用边界。对其三个 200-episode 失败分析 JSON 的 SR / SPL / 平均 DTG / 失败分解**做了独立重算**，结果与上游一致。

- **工程整理**：
  - 部署代码入库并打包为可 `catkin_make` 的 `s100_deploy` 包（补 `package.xml`、`CMakeLists.txt`），此前代码位于仓库之外且缺 ROS 包定义；
  - 新增 `docs/ENVIRONMENT.md`，汇总训练线 / 部署线 / 仿真线三套环境的完整依赖；
  - 从已有评估录像抽取关键帧嵌入报告，使轨迹行为不依赖视频也能查看。

- **补充真机素材**。从项目组取得两件此前未归档的素材，均已入库至 `src/deploy/wheeltec_s100/media/`：
  - **S100 平台照片**（`wheeltec_s100_hardware.jpg`）—— 可见车体顶部安装的奥比中光深度相机；
  - **Nav2 基线导航实机演示**（`wheeltec_s100_nav2_baseline.mp4`，1920×1080 / 30 fps / 35.9 s，拍摄于 2026-08-02 19:10）。画面为实验室走廊实景，同期笔记本屏幕显示 RViz 的 `Global/Local Costmap`、`Map`、`Particle Cloud`、`LaserScan`、`Path` 等显示项。

这组素材的定位是**平台与基线验证**，不是 PPO 策略的运行画面：它证明 S100 硬件、传感器链路与**传统 Nav2 栈**（AMCL + costmap + 规划器）在该场地上工作正常，从而为 PPO 路线提供了实机对照基线，也排除了硬件层面的疑因。已在报告 §VI.A 与 §VI.I 中使用，并明确标注其能说明与不能说明的边界。

**Challenges & blockers**

- 导出缺陷的发现说明：`load_state_dict(strict=False)` 与 TorchScript 导出的组合会在**静默状态**下产出错误产物。**部署前的权重一致性校验此前是缺失的一环**——教训已写入报告 §VII.A.6。
- 篇幅与证据强度的平衡：报告中每个定量结论都标注了证据等级（**实测有产物** / **文档记录**），避免把文档记载当作独立复验结果。

**Next steps**

- 修复 TorchScript 导出脚本（`strict=True` + 参数量/统计量/输出三重一致性校验），重新导出并复测真机表现。
- 补做多种子训练，给出跨 seed 的均值与标准差。
- 完成 `src/deploy/wheeltec_s100/03-roadmap.md` 中 M2–M6 的剩余里程碑。

**Repo files**

- `REPORT.md` —— 期末报告
- `docs/ENVIRONMENT.md` —— 环境与依赖说明
- `src/joint_phase/` —— 合作阶段材料与出处声明
- `src/deploy/s100_deploy/` —— ROS 1 部署包
