# 环境与依赖说明

> 对应 FURP 最终提交要求第 2 项「环境与依赖说明」。本项目涉及**三条彼此独立的技术链路**，运行在不同机器、不同操作系统、不同 Python 版本上，不能混用同一套环境。每条链路单独列出。标注约定：**[实测]** = 本机命令输出或配置文件可直接验证；**[文档记录]** = 来自本仓库或 ` 真机部署/` 文档的书面记载，无独立产物可复验。

---

## 一、训练链路（本人工作主体，Gibson 双模型）

运行位置：本地工作站（Ubuntu 22.04.5 LTS）

| 组件 | 版本 | 状态 |
|---|---|---|
| 操作系统 | Ubuntu 22.04.5 LTS (x86_64) | **[实测]** |
| GPU | NVIDIA GeForce RTX 3060, 12 GB VRAM | **[实测]** |
| NVIDIA 驱动 | 595.71.05（CUDA 13.2 支持） | **[文档记录]** |
| Python | 3.9.25（conda 环境 `habitat`） | **[实测]** |
| Habitat-Sim | 0.3.3（conda 预编译，含 bullet） | **[实测]** |
| Habitat-Lab | 0.3.3（`pip install -e`） | **[实测]** |
| Habitat-Baselines | 0.3.3（`pip install -e`） | **[实测]** |
| PyTorch | 2.8.0+cu128 | **[实测]** |
| pillow | 10.4.0（habitat-sim 0.3.3 硬性要求） | **[文档记录]** |
| 随机种子 | **42**（两个模型一致） | **[实测]**（`training/train*.sh`） |

### 数据

| 数据集 | 用途 | 位置 |
|---|---|---|
| Gibson（88 场景，1.5 GB） | 双模型训练场景 | `habitat-lab/data/scene_datasets/gibson/` |
| PointNav Gibson v1 episodes（385 MB） | 训练/评估回合 | 同上 |
| Habitat test scenes（105 MB） | 第 2 周冒烟测试 | `habitat-lab/data/scene_datasets/habitat-test-scenes/` |

### 需打的两处补丁

PyTorch ≥ 2.6 把 `torch.load` 的 `weights_only` 默认值改为 `True`，而 Habitat 0.3.3 的 checkpoint 内含 `omegaconf.DictConfig`，会加载失败。需在两处显式改为 `False`：

```
habitat-baselines/habitat_baselines/rl/ddppo/ddp_utils.py:224
habitat-baselines/habitat_baselines/rl/ppo/ppo_trainer.py:341
```

### 复现训练

```bash
conda activate habitat
cd habitat-lab
# RGBD（4 通道输入）
bash ../FURP-2026-YicongNing-RLNavigationForAMR/src/lab2/training/train.sh
# Depth-only（1 通道输入）
bash ../FURP-2026-YicongNing-RLNavigationForAMR/src/lab3/training/train_depth_only.sh
```

完整配置备份见 `src/lab2/training/configs/` 与 `src/lab3/training/configs/`（注意：这些是 config 的**副本**，Hydra 解析时须置于 `habitat-lab` 内对应路径）。

### 已知环境问题

| 问题 | 处理 |
|---|---|
| 6 个并行 env 时 EGL 初始化崩溃 | 强制 NVIDIA EGL：`export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json`；env 数降到 ≤5 |
| WSL2 下无法渲染（`unable to find CUDA device 0 among 1 EGL devices`） | 第 2 周迁移到原生 Ubuntu 22.04 |
| 训练进程偶发崩溃 | `nohup` + cron watchdog 自动重启（日志中记录了 706 次重启） |

---

## 二、真机部署链路（WHEELTEC S100）

> 该链路的代码见 `src/deploy/s100_deploy/`。部署的模型是 **HM3D** 数据集训练的合作者模型，不是本仓库 Gibson 双模型 —— 详见 `REPORT.md` §V/§VI。

### 2.1 机器人平台

| 组件 | 型号 / 版本 | 状态 |
|---|---|---|
| 机器人本体 | WHEELTEC S100 差速服务机器人 | **[文档记录]** |
| 车载算力 | **NVIDIA Jetson Orin Nano**（Engineering Reference Developer Kit Super），JetPack R35.6.1 (L4T) | **[文档记录]** |
| 板载资源 | 6 核 ARM CPU, 7.3 GB RAM, CUDA GPU 可用 | **[文档记录]** |
| 相机 | 奥比中光 **ORBBEC Astra S**（`lsusb` 显示 `ORBBEC`/`ASTRA S`） | **[文档记录]** |
| 激光雷达 | 2D LiDAR 存在（`/dev/wheeltec_lidar`），**本策略不使用** | **[文档记录]** |
| 底盘通信 | 串口（非 CAN），udev 固定名 `/dev/wheeltec_controller` | **[文档记录]** |
| 里程计 | 轮式里程计 + IMU 经 `robot_pose_ekf` 融合 → `/robot_pose_ekf/odom_combined` | **[文档记录]** |

### 2.2 软件栈

| 组件 | 版本 | 状态 |
|---|---|---|
| 操作系统 | Ubuntu 20.04.6 LTS (Focal), **aarch64** | **[实测]**（`uname -m`、`rosversion -d`） |
| ROS | **ROS 1 Noetic**（`ROS_VERSION=1`，`/opt/ros/` 下仅 noetic） | **[实测]** |
| Python | **3.8.10**（系统）/ 3.8.20（conda `wheeltec`） | **[实测]** |
| PyTorch | **1.14.0a0+44dac51c.nv23.2**（NVIDIA Jetson 专用构建，`torch.cuda.is_available()=True`） | **[文档记录]** |
| numpy / torchvision | 1.24.4 / 0.14.1（conda `wheeltec`） | **[文档记录]** |
| OpenCV | 3.4.5（系统 python3） | **[实测]** |
| 关键约束 | 系统级 python3 **无 torch** → 必须 `conda activate wheeltec` | **[实测]** |

### 2.3 为何需要 `habitat_stub.py`

Jetson 上**不安装** `habitat_sim` / `magnum`（GPU 渲染仿真器，机器人推理用不到）。但 `habitat-baselines` 有几处**死代码路径**会无条件 import 它们，因此需要在 import 任何 habitat 代码之前，往 `sys.modules` 注入桩模块。共 5 处：

| # | 模块 | 成因 |
|---|---|---|
| 1 | `habitat.tasks.nav.instance_image_nav_task` | `resnet_policy.py` 顶部 import；该文件无条件 `import habitat_sim` |
| 2 | `habitat.sims.habitat_simulator.object_state_machine` | 无条件 `import magnum` |
| 3 | `habitat.tasks.rearrange`（整包） | `_try_register_rearrange_task()` 名为 try 实则无 try/except，无条件 import 24 个机械臂任务子模块 |
| 4 | `habitat.core.batch_rendering.env_batch_renderer` | 无条件 `import magnum`；仅 `VectorEnv.initialize_batch_renderer()` 用到 |
| 5 | `habitat.tasks.rearrange.rearrange_sim` | `gym_wrapper.py` 借用一个纯装饰器 `add_perf_timing_func` |

已用 `grep -rl "^import magnum\|^import habitat_sim"` 对全库排查，确认其余硬依赖文件均在上述桩覆盖范围之内或本身有 try/except 保护。

另有两份裁剪版 `__init__.py`（`jetson_inference/patched_init_files/`），去掉 IL/VER trainer 的预加载（那些需要 lmdb / webdataset / faster_fifo 等无关于推理的依赖）。**云端 `habitat39` 训练环境必须保留原版**，不可替换。

### 2.4 权限与网络

| 项 | 值 |
|---|---|
| SSH | `ssh wheeltec@<机器人 IP>`（IP 由路由器分配，会变化，需现场确认） |
| WiFi | SSID `ORBBOT`；虚拟机需桥接模式 |
| `/cmd_vel` 消费者 | `wheeltec_robot` 节点（`wheeltec_robot.cpp:729`，直接订阅话题名，无重映射） |

> ⚠️ 该系统上还存在 `/body_process/cmd_vel`、`/red_vel` 等多路速度指令源（body 交互 demo），正式测试前需确认是否停用，避免控制权争抢。

---

## 三、Gazebo 仿真链路（TCP bridge 测试平台）

运行位置：本地开发机。这是本项目**创新点③**的载体 —— 用进程隔离解决 Python 版本冲突。

### 3.1 为何需要 TCP bridge

| 侧 | Python | 依赖 |
|---|---|---|
| 推理服务 | 3.9（conda `habitat`） | habitat-baselines / torch |
| ROS 2 节点 | 3.10（系统） | rclpy / cv_bridge |

ROS 2 Humble 的 C 扩展是 **cpython-310**，而 habitat-baselines 装在 **Python 3.9** 环境里，两者无法在同一进程内共存（会报 `No module named 'rclpy._rclpy_pybind11'`）。因此拆成两个进程，用 localhost TCP + JSON 行协议通信。

### 3.2 环境

| 组件 | 版本 | 状态 |
|---|---|---|
| 操作系统 | Ubuntu 22.04（**与训练同一台机器**） | **[实测]** |
| ROS | ROS 2 **Humble** | **[实测]** |
| Gazebo | **11.10.2** | **[实测]** |
| TurtleBot3 包 | `turtlebot3_gazebo` 2.3.8 / `turtlebot3_description` 2.3.6 | **[实测]** |
| conda `habitat` | Python 3.9.25 + torch 2.8.0 | **[实测]** |
| GPU | RTX 3060（推理走 CUDA） | **[实测]** |

### 3.3 通信协议

```
请求  {"rgb": [[[r,g,b],...]], "depth": [[d,...]], "goal": [dist_m, angle_rad], "reset": false}
响应  {"action": 0-3, "error": null, "latency_ms": 12.3}
```

`reset: true` 用于新目标点时清空 RNN 隐状态。服务端为每连接维护独立 RNN 状态（`ThreadingTCPServer`），默认端口 **9876**。

### 3.4 已知环境限制

| 限制 | 说明 |
|---|---|
| TB3 Burger 无相机 | 标准 launch 只有 LiDAR；需换 Waffle 或注入 depth 插件 |
| Gazebo 的深度插件 | 该环境**没有** `libgazebo_ros_depth_camera.so`，只能用 `libgazebo_ros_camera.so` |
| 改动系统模型需 sudo | `/opt/ros/humble/share/...` 为 root 所有，本机无 sudo 权限 → 改用 `GAZEBO_MODEL_PATH` 指向自定义模型目录 |
| 无 `ffmpeg` | 视频抽帧改用 OpenCV（conda `habitat` 环境内 cv2 4.11.0） |

---

## 四、README 里的两处待补充项

两项均已回填（2026-09-22）：

1. 根 `README.md` 的「Cited paper being replicated」已填 **DD-PPO (Wijmans et al., ICLR 2020) + Habitat (ICCV 2019)**，与报告 §I.B 的复现口径一致。
2. 根 `README.md` 的「Team or individual」已填 **Team**。合作阶段的材料另行署名（见 `src/joint_phase/PROVENANCE.md`）。

README 另已补充项目概览、交付物索引，并把目录结构更新为仓库实际状态。
