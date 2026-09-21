# 真机部署 — Roadmap

> 里程碑清单，不写具体日期。每个里程碑列出「完成标志」，作为判断是否可以推进到下一个里程碑的依据。
> 当前阶段模型：**PointGoal PPO（离散动作空间：stop/move_forward/turn_left/turn_right），checkpoint 为 `autodl/exp/baseline_seed300/checkpoints/ckpt.49.pth`**。完成本模型后，再按「模型队列」推进下一个模型。

## 模型队列（当前 & 后续）

1. **PointGoal PPO 离散动作，baseline_seed300/ckpt.49** ← 当前进行中
2. 下一个模型：`autodl/exp` 下同批次的 `baseline_seed100`/`baseline_seed200`/`stop_aware_seed100` 等，或未来引入 Transformer 结构的策略，待第1个模型跑通后再确定

---

## M0 — 环境与资料摸底

**目的**：把 `02-tech-stack.md` 中的 TBD 项确认清楚，避免带着错误假设开发节点。

- 完成标志：
  - [x] 确认 S100 使用 ROS1 还是 ROS2 → ROS1 Noetic
  - [x] 确认车载算力平台型号与推理能力 → Jetson Orin Nano，`wheeltec` conda 环境 torch GPU 可用
  - [x] 确认深度相机型号与参数 → 奥比中光 Astra S，硬件已连接，驱动待启动
  - [x] 确认定位/里程计方案 → `robot_pose_ekf`（轮式里程计+IMU融合），已现成可用
  - [x] 确认底盘通信协议对应的 ROS 话题/消息类型 → 串口，`/cmd_vel` 由 `wheeltec_robot` 节点订阅
  - [x] 确认训练该 PPO 模型的框架与模型文件格式 → habitat-baselines 0.3.3，.pth 格式
  - [ ] `02-tech-stack.md` 中的待确认清单清零或明确标注"暂不影响开发，可并行"的项 —— 剩余：深度相机驱动启动后的话题细节、body demo 启动方式、离散动作转换层设计、Jetson 侧最小依赖梳理（这几项性质上属于 M1/M2 阶段的工作内容，留到对应里程碑处理即可，不阻塞 M0 收尾）

## M1 — 单机验证：模型能在车载平台上正确推理

**目的**：先脱离机器人本体，确认模型文件能在目标算力平台上加载并推理出合理输出，排除环境/依赖问题。

- 完成标志：
  - [x] 模型权重文件（`ckpt.49.pth`）已拷贝到 Jetson，`wheeltec` conda 环境下 `PointNavResNetPolicy` 模型结构代码已移植并能成功加载 state_dict（不依赖 habitat_sim 仿真器本身）——2026-08-02 完成，用 sys.modules stub 绕开了 habitat-lab 里5处"意外硬依赖habitat_sim/magnum"的死代码路径，详见 `jetson_inference/habitat_stub.py` 注释
  - [x] 能用离线/手造的 RGB+深度图 + 手造的相对目标坐标，跑通一次前向推理，输出的离散动作（stop/move_forward/turn_left/turn_right）在合理范围内（无 NaN、无明显异常）——2026-08-02 完成，连续5步推理数值稳定。**过程中订正了一个关键假设**：checkpoint 实际用的是 RGB+Depth 双路视觉输入，不是此前文档记录的"只有深度"（`01-goal.md`/`02-tech-stack.md` 已同步更新）
  - [x] 记录单次推理耗时，初步判断是否满足实时控制频率——2026-08-02 完成：Jetson Orin Nano GPU上平均延迟16.1ms（min14.2/max21.9ms），约62Hz，远超机器人导航常用的5-30Hz控制频率需求，**推理性能不是瓶颈**

## M2 — ROS 节点编写：观测输入链路

**目的**：把真实传感器数据接入，替换 M1 中的离线数据。

- 完成标志：
  - [ ] 深度相机 ROS 话题能正常发布（`roslaunch turn_on_wheeltec_robot wheeltec_camera.launch`），话题名/分辨率/深度单位确认
  - [ ] 定位模块能输出机器人实时位姿（基于现有 `/robot_pose_ekf/odom_combined` 或 `/tf`）
  - [ ] 编写「相对目标坐标计算」节点或逻辑（给定目标点 + 当前位姿 → 极坐标下的距离/角度，对齐 `PointGoalWithGPSCompassSensor` 定义），并做正确性验证（如手动摆位置核对数值）
  - [ ] 观测数据的预处理（深度图 resize 到 256×256、按 max_depth=10.0 归一化等）与训练时保持一致，有对齐检查（如可能，用训练时的验证样本核对预处理输出）

## M3 — ROS 节点编写：推理与动作输出链路

**目的**：把 M1 的推理能力包装成 ROS 节点，接 M2 的观测，输出动作给底盘。

- 完成标志：
  - [ ] 推理节点：订阅 M2 产出的观测话题 → 模型推理得到离散动作 → 离散动作转换层（见 `01-goal.md`「执行方式」的两种候选思路，本阶段需选定一种并实现）→ 发布 `cmd_vel`
  - [ ] 已确认/处理现有 body 交互 demo 与推理节点的 `/cmd_vel` 冲突问题（停用 demo 或做优先级/互斥处理）
  - [ ] `cmd_vel` 话题能被 `wheeltec_robot` 节点正确接收并响应（先在悬空/无地面接触或极低速情况下验证，避免首次联调发生碰撞或失控）
  - [ ] 全链路话题图（rqt_graph 或等效方式）已确认，无缺失连接

## M4 — 真机联调跑通（首次完整尝试）

**目的**：在真实环境中完整跑一次「给定目标点 → 到达」的流程。

- 完成标志：
  - [ ] 在受控、简单的测试场地（障碍物少、空间开阔）完成至少一次尝试
  - [ ] 达到 `01-goal.md` 中定义的「跑通」三条标准：到达目标、零碰撞、无人工干预
  - [ ] 若失败，记录失败原因分类（观测对齐 / 坐标系错误 / 推理延迟 / 传感器缺失 / 底盘响应异常 / 离散动作转换误差累积 / 其他，参考 `01-goal.md` 中训练时的失败模式 bad_stop/near_miss/lost 作对照）

## M5 — 稳定性复核

**目的**：确认 M4 的成功不是偶然，具备一定可重复性。

- 完成标志：
  - [ ] 在同一测试场地，不同起点/目标点组合下，多次重复测试，记录成功率
  - [ ] 汇总已知失败模式及是否已规避
  - [ ] 形成本模型的部署总结（复用价值：哪些节点/流程可直接复用给下一个模型，哪些是本模型专属）

## M6 — 收尾与下一模型交接

**目的**：为下一个模型的部署做准备。

- 完成标志：
  - [ ] 本目录（`src/deploy/wheeltec_s100/`）内容更新为反映 PointGoal PPO 的最终状态
  - [ ] 明确下一个待部署模型是什么，以及其 observation/action 定义与 PointGoal PPO 的差异点
  - [ ] 根据差异点，预判 `02-tech-stack.md` 和节点架构需要做哪些调整
