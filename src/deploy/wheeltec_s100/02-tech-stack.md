# 真机部署 — 技术栈

> 本文件记录真机部署阶段涉及的软硬件技术栈事实。已确认项直接写入，未确认项标注「TBD」并注明需要去哪份资料/如何确认，禁止臆测填写。

## 硬件平台

| 项目 | 状态 | 说明 |
|---|---|---|
| 机器人本体 | 已确认 | WHEELTEC S100 差速服务机器人。实机 SSH 地址示例：`wheeltec@192.168.0.100`（注：readme 里写的 `.158` 与实测 `.100` 不一致，以现场实际 IP 为准，可能随网络环境变化） |
| 底盘控制 | 部分确认 | 串口通信（非 CAN）。系统存在 `/dev/wheeltec_controller`（udev 规则固定命名），对应 `/etc/udev/rules.d/wheeltec_controller*.rules`。具体协议细节仍需看 `turn_on_wheeltec_robot` 包源码（`wheeltec_robot.cpp`） |
| 车载算力平台 | 已确认 | **NVIDIA Jetson Orin Nano**（Engineering Reference Developer Kit Super）。JetPack对应 R35.6.1 (L4T)。6核ARM CPU，7.3GB内存，GPU CUDA可用（见下方推理环境） |
| 深度相机型号 | 已确认 | **奥比中光 ORBBEC Astra S**。`lsusb -v` 检测到 `iManufacturer: ORBBEC`、`iProduct: ASTRA S`、以及 `ORBBEC Close Depth Sensor`/`ORBBEC Audio Device` 两个接口。硬件已连接，但驱动节点目前未启动（无 `/dev/video*`，无 `/camera/*` 话题）。驱动包已现成：`~/wheeltec_robot/src/ros_astra_camera-main`，配套 `wheeltec_camera.launch` 默认 `camera_mode=Astra_S`，启动后会发布 `/camera/rgb/*` 和深度相关话题（具体深度话题名/分辨率待启动后用 `rostopic list`/`rostopic echo camera_info` 确认，并核对与训练时 config.yaml 中 depth_sensor 的 256x256/hfov90/max_depth10m 是否一致，可能需要做 resize/reformat） |
| 定位/里程计来源 | 已确认，且已可用 | 轮式里程计 `/odom` + IMU `/imu` 融合，`robot_pose_ekf` 节点常驻运行，发布 `/robot_pose_ekf/odom_combined`。`/tf`、`/tf_static` 也已发布。**这部分不需要重新开发**，可直接用于计算「相对目标坐标」 |
| 2D 激光雷达 | 已确认存在 | `/dev/wheeltec_lidar` 设备节点存在（udev 固定命名），tf 树里有 `base_to_laser`。本次 PointGoal PPO 的 observation 不使用它，暂不接入 |

## 软件系统

| 项目 | 状态 | 说明 |
|---|---|---|
| ROS 版本 | **已确认：ROS1 Noetic** | `printenv \| grep ros` 显示 `ROS_DISTRO=noetic`、`ROS_VERSION=1`。`/opt/ros/` 下只有 `noetic` 目录，没有装 ROS2。后续节点一律用 `rospy`/`roscpp`，不用 `rclpy` |
| 操作系统 | 已确认 | Ubuntu 20.04.6 LTS (Focal Fossa)，aarch64 架构（对应上方 Jetson 平台） |
| 网络连接方式 | 已确认 | WiFi：SSID `ORBBOT`，密码 `dongguan`；虚拟机用户需桥接模式连接 |
| 远程登录方式 | 已确认（IP需现场确认） | `ssh wheeltec@<机器人IP>`，密码 `dongguan`。实测过 `192.168.0.100`（成功），readme 中写的是 `192.168.0.158` —— **IP 会变化，以实际路由器分配为准**，登录前建议先确认当前IP |
| 现有功能包示例 | 已确认，且已在运行 | 车载主机开机后已有一套 body 交互 demo 常驻运行（节点 `/body_display`、`/body_interaction`、`/body_main` 等，另有 `wheeltec_robot` 底盘驱动节点、`robot_pose_ekf`、`robot_state_publisher`）。**注意**：这套 demo 会持续发布/订阅话题，正式开发 PPO 节点时要留意是否需要先停掉它，避免话题/资源冲突（尤其 `/cmd_vel` 控制权争抢，见下方发现） |
| 可视化工具 | 已确认 | `rqt_image_view`，订阅压缩图像话题（如 `/repub/body/body_display/compressed`）可获得更流畅画面 |
| 现有工作空间 | 已确认 | 家目录下有多个 catkin 工作空间：`wheeltec_robot`（底盘/外设驱动核心包，含 `turn_on_wheeltec_robot`、GPS、机械臂、语音等）、`wheeltec_lidar`、`wheeltec_arm`、`cartographer_ws`（Cartographer SLAM）。新的 PPO 推理节点建议新建独立工作空间，避免污染这些现有包 |
| 现有 cmd_vel 相关话题 | 已确认，需注意冲突 | 已存在 `/cmd_vel`、`/body_process/cmd_vel`、`/red_vel` 等多个速度控制话题，说明当前系统里有多路速度指令源（body交互demo等）在共同影响底盘。PPO 节点发布 `/cmd_vel` 前需搞清楚谁最终会被 `wheeltec_robot` 底盘驱动节点采纳，是否有话题重映射/优先级机制 |

## 策略推理侧技术栈

| 项目 | 状态 | 说明 |
|---|---|---|
| 策略性质 | 已确认 | PointGoal PPO，**离散动作空间**（非连续cmd_vel输出，见下方"模型输出"），训练完成，权重冻结（frozen），本阶段不训练/不微调 |
| 部署 checkpoint | 已确认 | `D:\AMR-Navigation-Project\autodl\exp\baseline_seed300\checkpoints\ckpt.49.pth`。训练于 HM3D val 数据集，1000万步（total_num_steps=1e7），200 episodes 评估 success_rate=0.895 |
| 训练框架 | 已确认 | habitat-baselines（来自私有 fork：`furp-2026-Zhihao-Chen-End-to-End-RL-Navigation`），`habitat_baselines==0.3.3` / `habitat_lab==0.3.3` / `habitat_sim==0.3.3`，云端训练环境为 conda `habitat39`（Python 3.9, torch 2.4/2.5+cu12, **x86_64架构**，不能直接搬到 Jetson aarch64，仅供参考模型结构定义代码） |
| 模型输入 (observation) | **已确认（2026-08-02 订正）** | **RGB图像（256×256, hfov 90°, uint8[0,255]）+ 深度相机图像（256×256, hfov 90°, min_depth 0.0, max_depth 10.0, normalize_depth true）+ 相对目标坐标**（`PointGoalWithGPSCompassSensor`, goal_format POLAR, dimensionality 2，即距离+角度）。此前文档误记为"只有深度相机"，M1阶段实机加载checkpoint时因网络第一层卷积输入通道数不匹配（报错显示4通道 vs 期望1通道）才发现训练时同时用了RGB+Depth，回查config.yaml确认。**深度归一化公式**（`habitat_simulator.py` `HabitatSimDepthSensor.get_observation`）：`normalized = clip(depth_meters, 0, 10) / 10`，真机深度相机预处理必须复现这个精确公式。因为存在RGB输入，`normalize_visual_inputs=True`（`RunningMeanAndVar`归一化层，训练时统计的均值/方差已打包在checkpoint的state_dict里，加载时随卷积层权重一并还原） |
| 模型输出 (action) | **已确认（订正）** | **离散动作**：`{stop, move_forward, turn_left, turn_right}` 四选一（`action_distribution_type: categorical`），非连续速度值。对应固定运动量：`forward_step_size=0.25m`, `turn_angle=10°`。真机部署需要额外一层「离散动作→cmd_vel」的转换逻辑（见 `01-goal.md`「执行方式」章节的两种候选思路），不能把网络输出直接当速度数值使用 |
| 推理运行环境 | 已确认 | conda 环境 `wheeltec`（`~/anaconda3/envs/wheeltec`）内已装 torch 1.14.0a0+44dac51c.nv23.2（NVIDIA Jetson专用编译版），`torch.cuda.is_available()` 返回 `True`——**GPU 推理可用**。该环境 Python 3.8.20，numpy 1.24.4，torchvision 0.14.1。系统级 pip3（非conda）只有 numpy 1.17.4 + torchvision 0.14.1，无 torch——**必须激活 `conda activate wheeltec` 环境才能跑 PPO 推理**，后续 ROS 节点启动脚本需注意这一点 |
| Jetson 侧最小依赖方案 | **已确认（2026-08-02 梳理完毕）** | 不在 Jetson 上装 `habitat_sim`（GPU渲染仿真器，机器人推理不需要）。`habitat-lab`/`habitat-baselines` 官方设计上支持脱离 habitat_sim 单独安装（requirements.txt 本身不含它），但 `resnet_policy.py`（`PointNavResNetPolicy` 所在文件）顶部有一行意外耦合的 import：`from habitat.tasks.nav.instance_image_nav_task import InstanceImageGoalSensor`，而该文件无条件 `import habitat_sim`。我们的 checkpoint 不使用 InstanceImageGoal 传感器，这行 import 是死代码路径。解决方案：在 import 任何 habitat_baselines 策略代码前，往 `sys.modules` 注入一个 stub 模块提供 `InstanceImageGoalSensor.cls_uuid` 常量，绕开真实文件里的 `import habitat_sim`。已验证 `nav.py`、`object_nav_task.py`、`ppo/policy.py`、`resnet.py`、`rnn_state_encoder.py` 等其余依赖链均不涉及 habitat_sim |
| Jetson 加载/推理脚本 | 已完成（待上机验证） | 见 `src/deploy/s100_deploy/jetson_inference/`：`habitat_stub.py`（依赖注入桩）+ `load_and_infer.py`（加载checkpoint、重建`PointNavResNetPolicy`网络结构、跑通离线推理，验证输出无NaN）。checkpoint 内部打包了完整训练config（`torch.load()`后`ckpt["state_dict"]`为权重、`ckpt["config"]`含网络超参数），脚本据此自动重建网络结构，不需要手动硬编码超参数 |
| ROS 节点封装方式 | 待开发 | 需新建一个 ROS1 节点：订阅 RGB + 深度相机话题（相机驱动待启动，见上方，Astra S 本身同时支持这两路输出）+ 用现有 `/robot_pose_ekf/odom_combined`（或 `/tf`）计算相对目标坐标（转极坐标）→ 模型推理得到离散动作（需在 `wheeltec` conda 环境中运行）→ 离散动作转换层 → 发布 `cmd_vel` 话题给底盘驱动节点。发布话题名需先解决下方"cmd_vel 冲突"问题 |

## 已明确排除/延后的技术选型

- 本次不采用「PPO 输出 subgoal + Nav2 执行避障」的分层架构（那是给其他/后续模型准备的架构预案，与本次离散动作 PointGoal PPO 不是同一套）。
- 本阶段不涉及 NeuPan（2D激光雷达避障规划器）接入，除非后续决定给本模型加安全兜底层。
- 本阶段不涉及模型训练/微调工具链。
- 不在 Jetson 上复刻云端 `habitat39`（x86_64+CUDA12）训练环境，仅按需移植模型结构定义代码到本地 `wheeltec` conda 环境。

## 待确认清单（汇总，2026-08-02 更新）

- [x] S100 实际使用 ROS1 or ROS2 → **ROS1 Noetic**
- [x] 车载算力平台型号 → **NVIDIA Jetson Orin Nano**（JetPack R35.6.1）
- [x] 深度相机具体型号 → **奥比中光 Astra S**，硬件已连接，驱动待启动（`wheeltec_camera.launch`）
- [x] 里程计/定位方案 → **轮式里程计+IMU的EKF融合（`robot_pose_ekf`），已现成可用**
- [x] 底盘通信协议 → **串口**（非CAN），udev固定命名为 `/dev/wheeltec_controller`
- [x] 车载平台的推理性能是否满足实时控制频率要求（初判）→ **conda环境`wheeltec`中torch GPU可用（`torch.cuda.is_available()=True`）**，具体推理延迟需实测
- [x] 训练该 PPO 模型所用的框架与模型文件格式 → **habitat-baselines 0.3.3，.pth 格式（PyTorch state_dict + 训练配置打包）**
- [x] `~/anaconda3/envs/wheeltec` conda 环境的 torch/CUDA 是否可用 → **可用**，torch 1.14.0a0+44dac51c.nv23.2，Python 3.8.20，无 habitat 相关包（需额外移植 `PointNavResNetPolicy` 模型结构定义代码，不依赖 habitat_sim 仿真器本身）
- [ ] 深度相机驱动启动后（`roslaunch turn_on_wheeltec_robot wheeltec_camera.launch`），确认实际发布的RGB和深度话题名、分辨率、深度单位（米/毫米），并与训练时的RGB(256×256,hfov90°)/depth_sensor参数（256×256, hfov 90°, max_depth 10.0m, normalize_depth true）核对/做预处理适配
- [ ] 现有 body 交互 demo（`/body_display`等节点）的启动方式仍不明确 —— 不在 `~/.bashrc`、也没查到对应 systemd service，但登录时已在运行，需进一步排查（如 crontab、rc.local、桌面自启动项）才能确定开发/测试期间如何安全停用
- [x] `/cmd_vel` 最终由哪个节点消费 → **确认是 `wheeltec_robot` 节点**（`wheeltec_robot.cpp:729`, `Cmd_Vel_Sub = n.subscribe("cmd_vel", 100, ...)`），直接订阅话题名 `cmd_vel`，无重映射。**PPO 节点（经离散动作转换层后）需向 `/cmd_vel` 发布**，但需先停掉/确认 body demo 是否也在发布同一话题，避免指令冲突
- [ ] **新增**：离散动作 → cmd_vel 转换层的具体实现方式（见 `01-goal.md`）
- [ ] **新增**：Jetson 上部署所需的最小依赖集——从 `habitat_baselines`/`habitat_lab` 源码中提取 `PointNavResNetPolicy` 模型定义、checkpoint 加载逻辑、observation 预处理逻辑，需要哪些具体文件/模块，待代码梳理确认
- [ ] **安全提醒**：habitat39 环境导出信息中，`habitat_baselines`/`habitat_lab` 的 pip 安装源里包含明文 GitHub Personal Access Token（`ghp_...`），已提醒用户尽快吊销/轮换，任何后续文档/代码/commit 中都不应再包含该 token 明文
