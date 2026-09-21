# 实验命令速查

> 最后更新：2026-08-07
> 全部 eval 和真机测试命令汇总

---

## 一、仿真 Eval（AutoDL 训练机）

### 前置

```bash
cd /root/habitat-lab
conda activate habitat39
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
```

### Baseline 三 seed

```bash
bash experiments/baseline/hm3d_baseline/eval_hm3d.sh \
  /root/autodl-tmp/exp/baseline_seed100/checkpoints/latest.pth

bash experiments/baseline/hm3d_baseline/eval_hm3d.sh \
  /root/autodl-tmp/exp/baseline_seed200/checkpoints/latest.pth

bash experiments/baseline/hm3d_baseline/eval_hm3d.sh \
  /root/autodl-tmp/exp/baseline_seed300/checkpoints/latest.pth
```

### Stop-Aware 1e7 三 seed

```bash
bash experiments/baseline/hm3d_baseline/eval_hm3d.sh \
  /root/autodl-tmp/exp/stop_aware_seed100/checkpoints/latest.pth

bash experiments/baseline/hm3d_baseline/eval_hm3d.sh \
  /root/autodl-tmp/exp/stop_aware_seed200/checkpoints/latest.pth

bash experiments/baseline/hm3d_baseline/eval_hm3d.sh \
  /root/autodl-tmp/exp/stop_aware_seed300/checkpoints/latest.pth
```

### Stop-Aware 5e7

```bash
bash experiments/baseline/hm3d_baseline/eval_hm3d.sh \
  /root/autodl-tmp/exp/stop_aware_5e7_seed300/checkpoints/latest.pth
```

---

## 二、失败分析（AutoDL 训练机）

### 前置

```bash
cd /root/habitat-lab
conda activate habitat39
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
```

### 运行

```bash
python experiments/baseline/hm3d_baseline/failure_analysis.py \
  /root/autodl-tmp/exp/baseline_seed300/checkpoints/latest.pth \
  --out /root/autodl-tmp/exp/baseline_seed300/failure_analysis.json

python experiments/baseline/hm3d_baseline/failure_analysis.py \
  /root/autodl-tmp/exp/stop_aware_seed100/checkpoints/latest.pth \
  --out /root/autodl-tmp/exp/stop_aware_seed100/failure_analysis.json

python experiments/baseline/hm3d_baseline/failure_analysis.py \
  /root/autodl-tmp/exp/stop_aware_seed200/checkpoints/latest.pth \
  --out /root/autodl-tmp/exp/stop_aware_seed200/failure_analysis.json

python experiments/baseline/hm3d_baseline/failure_analysis.py \
  /root/autodl-tmp/exp/stop_aware_seed300/checkpoints/latest.pth \
  --out /root/autodl-tmp/exp/stop_aware_seed300/failure_analysis.json

python experiments/baseline/hm3d_baseline/failure_analysis.py \
  /root/autodl-tmp/exp/stop_aware_5e7_seed300/checkpoints/latest.pth \
  --out /root/autodl-tmp/exp/stop_aware_5e7_seed300/failure_analysis.json
```

---

## 三、真机部署（Jetson Orin Nano）

### 清除残留进程

```bash
killall -9 roslaunch roscore rosout rosmaster 2>/dev/null
pkill -9 -f "astra_camera_node" 2>/dev/null
pkill -9 -f "wheeltec_robot_node" 2>/dev/null
pkill -9 -f "camera_preprocessor" 2>/dev/null
pkill -9 -f "goal_computer" 2>/dev/null
pkill -9 -f "s100_inference_node" 2>/dev/null
sleep 3
```

### 终端 1 — roscore

```bash
roscore
```

### 终端 2 — 底盘驱动

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch
```

> 等看到 `Odom sensor activated` + `Imu sensor activated`

### 终端 3 — 相机

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot wheeltec_camera.launch
```

### 终端 4 — M2 观测链路

```bash
source ~/ppo_ws/devel/setup.bash
roslaunch ppo_navigation start_m2.launch goal_x:=2.0 goal_y:=0.0
```

### 终端 5 — M3 推理节点（四选一）

```bash
source ~/ppo_ws/devel/setup.bash

# === baseline_seed300（SR 0.895）===
roslaunch s100_deploy s100_deploy.launch \
  model_type:=habitat \
  ckpt_path:=/home/wheeltec/M3/ckpt.49.pth \
  execution_mode:=step \
  forward_speed:=0.15 \
  min_depth_for_safety:=0.05

# === stop_aware 1e7 seed300（SR 0.900）===
roslaunch s100_deploy s100_deploy.launch \
  model_type:=habitat \
  ckpt_path:=/home/wheeltec/M3/stop_aware_seed300.pth \
  execution_mode:=step \
  forward_speed:=0.15 \
  min_depth_for_safety:=0.05

# === stop_aware 5e7 seed300（SR 0.945）=== 最优
roslaunch s100_deploy s100_deploy.launch \
  model_type:=habitat \
  ckpt_path:=/home/wheeltec/M3/stop_aware_5e7_seed300.pth \
  execution_mode:=step \
  forward_speed:=0.15 \
  min_depth_for_safety:=0.05

# === 纯深度（纹理弱时用）===
roslaunch s100_deploy s100_deploy.launch \
  model_type:=jit_depth \
  ckpt_path:=/home/wheeltec/M3/policy_depth_jit.pt \
  execution_mode:=step \
  forward_speed:=0.15 \
  min_depth_for_safety:=0.05
```

### 终端 6 — 发目标点

```bash
# 正前方 1m
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  '{header: {frame_id: "odom_combined"}, pose: {position: {x: 1.0, y: 0.0}, orientation: {w: 1.0}}}'

# 正前方 2m
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  '{header: {frame_id: "odom_combined"}, pose: {position: {x: 2.0, y: 0.0}, orientation: {w: 1.0}}}'
```

### 终端 7（可选）— cmd_vel 日志

```bash
source ~/ppo_ws/devel/setup.bash
python3 ~/M3/cmd_vel_logger.py _log:=~/M5_$(date +%m%d_%H%M).log
```

---

## 四、多轮测试流程

每轮必须重启底盘（odom 归零）：

```bash
# 1. Ctrl-C 终端 2（底盘）
# 2. 重新启动
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch
# 3. 等 "Odom sensor activated"
# 4. 终端 6 发 goal
# 5. 看终端 5 日志 → Goal reached! 或 Timeout
# 6. 回到第 1 步
```

---

## 五、诊断命令（Jetson）

```bash
# odom 是否归零
rostopic echo /robot_pose_ekf/odom_combined -n1 | grep -E "x:|y:|z:"

# 相机帧率
rostopic hz /camera/rgb/image_raw --window=5

# 纹理梯度（>25=OK, <25=弱纹理→用 jit_depth）
python3 -c "
import rospy, numpy as np
from sensor_msgs.msg import Image
rospy.init_node('diag')
msg = rospy.wait_for_message('/ppo/rgb', Image, timeout=10)
data = np.frombuffer(msg.data, dtype=np.uint8).reshape(256,256,3)
gray = data.astype(float).mean(axis=2)
grad = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
print(f'纹理梯度={grad:.1f} (>25=OK, <25=弱纹理)')
"

# 深度中心有效像素
python3 -c "
import rospy, numpy as np
from sensor_msgs.msg import Image
rospy.init_node('diag')
msg = rospy.wait_for_message('/ppo/depth', Image, timeout=10)
d = np.frombuffer(msg.data, dtype=np.float32).reshape(256,256)
center = d[77:179, 77:179]
v = center[center > 0.001]
print(f'有效像素: {len(v)}/{center.size} ({100*len(v)/center.size:.1f}%)')
print(f'min={v.min():.4f} ({v.min()*10:.2f}m) mean={v.mean():.4f} ({v.mean()*10:.2f}m)'
"

# cmd_vel 发布者检查
rostopic info /cmd_vel
```

---

## 六、参数速查

| 参数 | 默认值 | 说明 |
|------|:------:|------|
| `model_type` | `habitat` | `habitat` / `jit_rgbd` / `jit_depth` |
| `execution_mode` | `continuous` | `step`（推荐）/ `continuous` |
| `forward_speed` | `0.25` | 前进线速度 m/s，落地建议 `0.15` |
| `turn_speed` | `0.5` | 转弯角速度 rad/s |
| `forward_step` | `0.25` | step 模式每步前进距离 m（=训练值） |
| `turn_angle_deg` | `10.0` | step 模式每步转角 °（=训练值） |
| `success_distance` | `0.2` | 到达判定距离 m（=训练值） |
| `max_steps` | `500` | 超时保护步数 |
| `min_depth_for_safety` | `0.3` | 安全距离 m，悬空 `0.05`，落地 `0.2` |
| `dry_run` | `false` | `true` = 不发 cmd_vel，只看推理输出 |

---

## 七、模型文件位置

### Jetson（`~/M3/`）

```
ckpt.49.pth                  ← baseline_seed300      (SR 0.895)
stop_aware_seed300.pth        ← stop_aware 1e7        (SR 0.900)
stop_aware_5e7_seed300.pth    ← stop_aware 5e7        (SR 0.945)
policy_rgbd_jit.pt            ← JIT RGBD export
policy_depth_jit.pt           ← JIT Depth export
```

### 训练机（AutoDL）

```
/root/autodl-tmp/exp/
├── baseline_seed100/checkpoints/latest.pth      (SR 0.755)
├── baseline_seed200/checkpoints/latest.pth      (SR 0.885)
├── baseline_seed300/checkpoints/latest.pth      (SR 0.895)
├── stop_aware_seed100/checkpoints/latest.pth    (SR 0.895)
├── stop_aware_seed200/checkpoints/latest.pth    (SR 0.875)
├── stop_aware_seed300/checkpoints/latest.pth    (SR 0.900)
└── stop_aware_5e7_seed300/checkpoints/latest.pth (SR 0.945)
```

### Windows（本地备份）

```
D:\AMR-Navigation-Project\autodl\exp\
├── baseline_seed100/checkpoints/latest.pth
├── baseline_seed200/checkpoints/latest.pth
├── baseline_seed300/checkpoints/latest.pth
├── stop_aware_seed100/checkpoints/latest.pth
├── stop_aware_seed200/checkpoints/latest.pth
├── stop_aware_seed300/checkpoints/latest.pth
└── stop_aware_5e7_seed300/checkpoints/latest.pth
```

---

## 八、Gazebo 仿真测试（本地开发机）

> 在 Gazebo + TurtleBot3 仿真环境中测试 PPO 模型。
> 采用 TCP bridge 架构：推理服务器（conda `habitat` env）+ ROS 2 节点（系统 Python）。

### 前置

```bash
# 确认系统已安装
dpkg -l | grep "ros-humble-turtlebot3-gazebo"   # TB3 Gazebo 仿真包
dpkg -l | grep gazebo                            # Gazebo 11

# 确认模型文件存在
ls -lh ~/Desktop/FURP/真机部署/latest.pth               # 约 23 MB
ls -lh ~/Desktop/FURP/真机部署/latest_optimized.pth      # 约 23 MB
```

### 单命令启动（推荐）

```bash
cd src/deploy/s100_deploy/gazebo_sim

# 测试 latest 模型（带 GUI）
./run_gazebo_test.sh latest

# 测试 optimized 模型（带 GUI）
./run_gazebo_test.sh optimized

# 无 GUI（headless，服务器模式）
./run_gazebo_test.sh latest --no-gui

# 启动后自动发送目标点 (x=2m, y=0m)
./run_gazebo_test.sh latest --goal 2.0 0.0

# dry-run 模式（不发 cmd_vel，仅观察推理输出）
./run_gazebo_test.sh latest --dry-run

# 连续运动模式（默认 step 模式）
./run_gazebo_test.sh latest --continuous

# 使用空世界
./run_gazebo_test.sh latest --world empty_world
```

### 分步启动（调试用）

```bash
cd src/deploy/s100_deploy/gazebo_sim

# 终端 1 — 启动推理服务器
conda run -n habitat --no-capture-output \
  python3 inference_server.py \
  --ckpt ~/Desktop/FURP/真机部署/latest.pth \
  --port 9876 --device cpu

# 终端 2 — 启动 Gazebo + TB3
export TURTLEBOT3_MODEL=burger
source /opt/ros/humble/setup.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 终端 3 — 启动 PPO 推理节点
source /opt/ros/humble/setup.bash
python3 ppo_gazebo_node.py --port 9876 --step

# 终端 4 — 发送目标点
ros2 topic pub --once /goal_pose geometry_msgs/PoseStamped \
  '{header: {frame_id: "odom"}, pose: {position: {x: 2.0, y: 0.0}, orientation: {w: 1.0}}}'
```

### 停止

```bash
# Ctrl-C 逐个停止，或
./stop_gazebo_test.sh
```

### 架构说明

```
┌──────────────────────────────┐    TCP (JSON)    ┌──────────────────────┐
│  ROS 2 Node (系统 Python 3.10) │ ◄──────────────► │ 推理服务器             │
│                              │   localhost:9876  │ (conda habitat env)  │
│  /scan → LiDAR→Depth (256²) │                   │                      │
│  /camera/image_raw → RGB     │  {rgb, depth,     │  PointNavResNetPolicy│
│  /odom → Pose                │   goal, reset}    │  (GRU, ResNet18)     │
│  /goal_pose → Target         │                   │                      │
│                     ↓        │    {action,        │                      │
│              /cmd_vel        │     latency_ms}    │                      │
└──────────────────────────────┘                   └──────────────────────┘
```

### 参数速查

| 参数 | 默认值 | 说明 |
|------|:------:|------|
| `--port` | `9876` | 推理服务器端口 |
| `--step` | `true` | Step 模式（匹配 Habitat 训练） |
| `--continuous` | `false` | 连续运动模式 |
| `--dry-run` | `false` | 不发 cmd_vel，仅观察 |
| `--max-steps` | `500` | 超时步数 |
| `--success-distance` | `0.2` | 到达判定距离 (m) |
| `--min-safety-dist` | `0.25` | LiDAR 安全距离 (m) |
| `--control-rate` | `10.0` | 控制频率 (Hz) |

### Gazebo 可用世界

| 世界 | 说明 |
|------|------|
| `empty_world` | 空地，无任何障碍 |
| `turtlebot3_world` | 标准测试场（含障碍物） |
| `turtlebot3_house` | 室内场景 |
| `turtlebot3_dqn_stage1` ~ `stage4` | DQN 训练关卡 |

---

## 九、常见问题

| 症状 | 原因 | 解决 |
|------|------|------|
| `no EGL devices found` | EGL 环境变量未设 | `export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json` |
| `Safety stop` 持续触发 | 相机看到近处地板 | 降低 `min_depth_for_safety:=0.05` |
| 机器人原地打转 | 纹理弱，模型无法判断方向 | 环境加视觉特征 或 换 `jit_depth` |
| odom 漂移，第二轮走到错误方向 | 没有重启底盘 | 每轮测试前重启终端 2 |
| 全 STOP 不前进 | 可能深度单位不匹配 | 检查 `/ppo/depth` 话题的 encoding 是否 32FC1 [0,1] |
| `FileNotFoundError: ckpt path` | 模型文件未上传到 Jetson | `ls -lh ~/M3/*.pth` 确认 |
