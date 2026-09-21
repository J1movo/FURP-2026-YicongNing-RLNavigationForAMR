### Week 7 — 2026-08-02 → 2026-08-11（真机部署阶段）

**Attended this week's meeting:** Yes

**Progress this week**

- **真机部署阶段启动**（2026-08-02）。部署对象确定为 HM3D 数据集训练的 `baseline_seed300/ckpt.49.pth`，目标平台 WHEELTEC S100 差分机器人（Jetson Orin Nano + Orbbec Astra S + ROS 1 Noetic）。规格文档见 `src/deploy/wheeltec_s100/` 下的 `01-goal.md` / `02-tech-stack.md` / `03-roadmap.md`。

- **M1 单机验证完成**（2026-08-02）。模型在 Jetson conda `wheeltec` 环境下成功加载（不依赖 habitat_sim），连续 5 步前向推理数值稳定。过程中订正了一个关键假设：checkpoint 实际使用 **RGB+Depth 双路输入**（4 通道），而非此前记录的"纯深度"。解决的工程问题：用 `sys.modules` 依赖注入绕过 `habitat-lab` 中 **5 处** "意外硬依赖 habitat_sim / magnum"的死代码路径。

- **ROS 1 推理节点编写完成**（M3）。包含观测预处理、极坐标目标计算、离散动作 → cmd_vel 转换层（continuous / step 两种语义）、深度安全刹停、RNN 状态自动重置。代码已整理为可 `catkin_make` 的完整包 `src/deploy/s100_deploy/`（补上了原先缺失的 `package.xml` 与 `CMakeLists.txt`）。

- **Gazebo 仿真测试平台搭建**（2026-08-08）。解决了 ROS 2（Python 3.10）与 habitat-baselines（Python 3.9）无法共存于同一进程的问题，采用**双进程 TCP 桥接**：推理服务跑在 conda 环境、ROS 2 节点跑在系统 Python，经 localhost:9876 以 JSON 行协议通信。代码见 `src/deploy/s100_deploy/gazebo_sim/`。

- **Gazebo 实测结果：失败**。模型在 Gazebo 场景中持续输出 TURN_RIGHT 直至超时。经服务端逐帧诊断确认**观测链路无误**（RGB / 深度值域正常、目标角度随朝向正确变化），判定为**域差异**——策略在 HM3D（真实室内扫描）上训练，无法泛化到 Gazebo 的几何化低纹理场景。录屏留存于 ` src/deploy/wheeltec_s100/media/gazebo_ppo_test.mp4`。

- **平台环境确认**（`src/deploy/wheeltec_s100/info.md`）：S100 实测为 aarch64 + Ubuntu 20.04 + ROS 1 Noetic + Python 3.8，系统 python3 **无 torch**，必须 `conda activate wheeltec`；Astra S 深度流实测 **29.7–29.9 Hz**。

**Challenges & blockers**

- LiDAR 投影得到的伪深度图与训练用的真实深度图分布差异过大，模型无法识别，因此 Gazebo 侧必须使用真实深度相机话题而非 LiDAR 兜底。
- TB3/Gazebo 标准模型缺少深度相机插件；本机 ROS 环境没有 `libgazebo_ros_depth_camera.so`，只有 `libgazebo_ros_camera.so`，需改写 SDF 插件配置。
- 系统级模型文件为 root 所有且本机无 sudo 权限，改用 `GAZEBO_MODEL_PATH` 指向自定义模型目录绕开。
- 部署阶段的结果留存不够完整：未系统归档运行日志与中间产物。

**Next steps**

- 整理部署阶段材料，补齐证据留存流程。
- 修复 TorchScript 导出脚本并复测真机表现。

**Repo files**

- `src/deploy/s100_deploy/` —— ROS 1 部署包（含 `gazebo_sim/` TCP bridge 平台）
- `src/deploy/wheeltec_s100/` —— 部署阶段规格文档与平台资料
