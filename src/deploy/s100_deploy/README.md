# s100_deploy — WHEELTEC S100 PointNav PPO 部署包

将 habitat-baselines 的 PointGoal PPO 策略部署到 WHEELTEC S100 差速机器人（ROS 1 Noetic）。

> **部署的模型说明**：本包部署的是 **HM3D** 数据集训练的模型（`baseline_seed300/ckpt.49.pth`，SR 0.895），**不是**本仓库 `src/lab2`/`src/lab3` 中基于 **Gibson** 训练的两个模型。两条模型线的关系见仓库根目录 `REPORT.md` §V/§VI。

---

## 包结构

```
s100_deploy/
├── package.xml                    # catkin 包定义
├── CMakeLists.txt
├── README.md                      # 本文件
├── launch/
│   └── s100_deploy.launch         # 主启动文件
├── scripts/                       # ROS 节点（四个文件必须同目录，见下）
│   ├── s100_inference_node.py     # 主推理节点
│   ├── action_controller.py       # 离散动作 → cmd_vel
│   ├── preprocess.py              # RGB / Depth 预处理
│   └── habitat_stub.py            # habitat_sim/magnum 依赖注入桩
├── jetson_inference/              # M1 单机验证脚本（离线跑通推理）
│   ├── load_and_infer.py
│   ├── habitat_stub.py
│   └── patched_init_files/        # 裁剪版 __init__.py（去掉 IL/VER trainer 预加载）
├── gazebo_sim/                    # Gazebo 仿真测试平台（TCP bridge 架构）
└── commands_reference.md          # 全部实验命令速查
```

> **`scripts/` 四个文件必须位于同一目录**：`s100_inference_node.py` 会把自己的目录插入 `sys.path`，然后 `from preprocess import ...` / `from action_controller import ...` / `import habitat_stub`。它们按设计平铺共处，而不是装成 Python 包。`CMakeLists.txt` 里的 `catkin_install_python` 已保证这一点。

---

## 编译

```bash
# 在 Jetson 上
mkdir -p ~/ppo_ws/src
cd ~/ppo_ws/src
ln -s ~/s100_deploy ./s100_deploy      # 或把整个包目录拷进来
cd ~/ppo_ws
catkin_make
source devel/setup.bash
```

纯 Python 包，无编译产物；`catkin_make` 只是生成 devel 空间与安装入口。

---

## 前置条件

| 项 | 要求 |
|---|---|
| 底盘驱动 | `roslaunch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch` |
| 相机 | `roslaunch turn_on_wheeltec_robot wheeltec_camera.launch`（Astra S） |
| conda 环境 | `wheeltec`，须含 torch(Jetson 版) + habitat-lab + habitat-baselines |
| 模型权重 | 已拷贝到 Jetson，默认路径见 launch 文件 |

> ⚠️ **必须激活 `conda activate wheeltec`**：系统级 python3 没有 torch。launch 文件已用 `launch-prefix` 自动处理这一点。

完整环境清单见 `../../../docs/ENVIRONMENT.md`。

---

## 启动

```bash
roslaunch s100_deploy s100_deploy.launch                       # 正常
roslaunch s100_deploy s100_deploy.launch dry_run:=true         # 只推理不发 cmd_vel
roslaunch s100_deploy s100_deploy.launch execution_mode:=step  # 步进模式（推荐）
roslaunch s100_deploy s100_deploy.launch forward_speed:=0.15 min_depth_for_safety:=0.05
```

发目标点（另一终端）：

```bash
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  '{header: {frame_id: "odom_combined"}, pose: {position: {x: 1.0, y: 0.0}, orientation: {w: 1.0}}}'
```

---

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `ckpt_path` | `ckpt.49.pth` | 模型路径 |
| `device` | `cuda` | `cuda` / `cpu` |
| `control_rate` | `10.0` | 控制频率 (Hz) |
| `execution_mode` | `continuous` | `continuous` / `step`（真机推荐 `step`） |
| `forward_speed` | `0.25` | FORWARD 线速度 (m/s)，落地建议 `0.15` |
| `turn_speed` | `0.5` | TURN 角速度 (rad/s) |
| `forward_step` | `0.25` | step 模式每步前进距离 (m)，= 训练值 |
| `turn_angle_deg` | `10.0` | step 模式每步转角 (°)，= 训练值 |
| `success_distance` | `0.2` | 到达判定距离 (m)，= 训练值 |
| `max_steps` | `500` | 超时保护步数 |
| `dry_run` | `false` | `true` = 不发 cmd_vel |
| `min_depth_for_safety` | `0.3` | 深度安全距离 (m)；悬空 `0.05`，落地 `0.2` |

话题可用 `rgb_topic` / `depth_topic` / `odom_topic` / `goal_topic` / `cmd_topic` 覆盖。

---

## 两种执行模式

策略输出是**离散动作** `{stop, move_forward, turn_left, turn_right}`，不是连续速度，因此必须有一层转换。本包提供两种语义：

- **`continuous`**（代码默认）：每个动作映射为一段固定速度，按控制频率持续发布。流畅，但**每步实际位移与训练不严格一致**。
- **`step`**：每个动作执行为固定位移（前进 0.25 m 或原地转 10°），到位后停住再推理下一次。更贴近 Habitat「一步一动作」的语义，但有顿挫感。**真机推荐此模式**（`commands_reference.md` 中四个示例均用 `execution_mode:=step`）。

---

## 测试流程

**Phase 1 — 离线验证**（不驱动机器人）
```bash
roslaunch s100_deploy s100_deploy.launch dry_run:=true
```
发目标点后观察日志：距离应递减、动作为 FORWARD、< 0.2 m 时触发 `Goal reached!`。

**Phase 2 — 悬空测试**（轮子离地）：确认 FORWARD/TURN_LEFT/TURN_RIGHT 转向正确。

**Phase 3 — 地面低速**：`forward_speed:=0.1`，在开阔区域跑 1–2 m。

**Phase 4 — 正常测试**。

> 多轮测试**每轮必须重启底盘**，否则 odom 不归零，第二轮会走错方向。

---

## 已知限制

1. **FOV 不匹配**：训练 90°，Astra S 约 57.6° —— 视野更窄，边缘障碍检测减弱。
2. **RGB 来源**：Astra S 无物理彩色传感器，`/camera/rgb/image_raw` 实为红外灰度图；`preprocess.py` 已按 `mono8` 复制为三通道处理。
3. **坐标系**：goal 与 odom 必须同坐标系；用 `/move_base_simple/goal` 时 frame_id 应为 `odom_combined`。
4. **head-shaking**：模型可能在 TURN_LEFT / TURN_RIGHT 之间震荡。已知应对：改用 `step` 模式；或加动作平滑（连续 N 次同向才执行）。
5. **深度单位**：`/ppo/depth` 必须为 32FC1 且已按 `clip(d,0,10)/10` 归一化；单位不匹配会导致全程 STOP。

---

## 故障排查

| 症状 | 检查 |
|---|---|
| 无相机帧 | `rostopic hz /camera/rgb/image_raw` |
| 模型加载失败 | `conda activate wheeltec && python -c "from habitat_baselines.rl.ddppo.policy.resnet_policy import PointNavResNetPolicy"` |
| cmd_vel 不响应 | `rostopic echo /cmd_vel`；确认 `wheeltec_robot` 节点在运行 |
| RNN 状态混乱 | 每次新 goal 自动重置，日志应显示 `RNN reset` |
| `FileNotFoundError: ckpt path` | `ls -lh ~/M3/*.pth` 确认权重已上传 |
| `no EGL devices found` | `export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json` |

更多症状见 `commands_reference.md` §九。

---

## 关于 `habitat_stub.py`

Jetson 上不装 `habitat_sim` / `magnum`（GPU 渲染仿真器，机器人推理用不到）。但 `habitat-baselines` 的若干**死代码路径**会无条件 import 它们，因此需要在 import 任何 habitat 代码**之前**往 `sys.modules` 注入桩模块。该文件注释中逐条记录了 5 处路径的成因与排查依据，以及全库 `grep` 验证结论。
