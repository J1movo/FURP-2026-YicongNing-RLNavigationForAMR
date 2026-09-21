# 真机部署 — 启动命令速查

> 最后更新：2026-08-06
> 当前状态：M4 ✅ M5 进行中 | 支持模型：habitat / jit_rgbd / jit_depth

---

## 清除所有残留进程

```bash
killall -9 roslaunch roscore rosout rosmaster 2>/dev/null
pkill -9 -f "astra_camera_node" 2>/dev/null
pkill -9 -f "wheeltec_robot_node" 2>/dev/null
pkill -9 -f "camera_preprocessor" 2>/dev/null
pkill -9 -f "goal_computer" 2>/dev/null
pkill -9 -f "s100_inference_node" 2>/dev/null
sleep 3
```

---

## 完整启动（6 个终端 + 1 个可选日志终端）

### 终端 1 — roscore

```bash
roscore
```

### 终端 2 — 底盘

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

### 终端 5 — M3 推理（三选一）

```bash
source ~/ppo_ws/devel/setup.bash

# 模型 A: Habitat RGBD（原 ckpt.49.pth）
roslaunch s100_deploy s100_deploy.launch \
  model_type:=habitat \
  ckpt_path:=/home/wheeltec/M3/ckpt.49.pth \
  execution_mode:=step \
  forward_speed:=0.15 \
  min_depth_for_safety:=0.05

# 模型 B: JIT RGBD
roslaunch s100_deploy s100_deploy.launch \
  model_type:=jit_rgbd \
  ckpt_path:=/home/wheeltec/M3/policy_rgbd_jit.pt \
  execution_mode:=step \
  forward_speed:=0.15 \
  min_depth_for_safety:=0.05

# 模型 C: JIT 纯深度（不依赖 RGB 纹理）
roslaunch s100_deploy s100_deploy.launch \
  model_type:=jit_depth \
  ckpt_path:=/home/wheeltec/M3/policy_depth_jit.pt \
  execution_mode:=step \
  forward_speed:=0.15 \
  min_depth_for_safety:=0.05
```

> 首次启动建议加 `dry_run:=true`，确认模型加载成功后再去掉

### 终端 6 — 发目标点

```bash
# 正前方 1m
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  '{header: {frame_id: "odom_combined"}, pose: {position: {x: 1.0, y: 0.0}, orientation: {w: 1.0}}}'

# 正前方 2m
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  '{header: {frame_id: "odom_combined"}, pose: {position: {x: 2.0, y: 0.0}, orientation: {w: 1.0}}}'

# 左前 1m
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  '{header: {frame_id: "odom_combined"}, pose: {position: {x: 1.0, y: 1.0}, orientation: {w: 1.0}}}'
```

### 终端 7（可选）— cmd_vel 日志

```bash
source ~/ppo_ws/devel/setup.bash
python3 ~/M3/cmd_vel_logger.py _log:=~/M5_$(date +%m%d_%H%M).log
```

---

## 参数速查

| 参数 | 默认值 | 说明 |
|---|---|---|
| `model_type` | `habitat` | `habitat` / `jit_rgbd` / `jit_depth` |
| `ckpt_path` | `~/M3/ckpt.49.pth` | 模型权重路径 |
| `execution_mode` | `continuous` | `step`（推荐）/ `continuous` |
| `forward_speed` | `0.25` | 前进线速度 m/s，落地建议 `0.15` |
| `turn_speed` | `0.5` | 转弯角速度 rad/s |
| `forward_step` | `0.25` | step 模式每步前进距离 m |
| `turn_angle_deg` | `10.0` | step 模式每步转角 ° |
| `success_distance` | `0.2` | 到达判定距离 m |
| `max_steps` | `500` | 超时保护步数 |
| `min_depth_for_safety` | `0.3` | 安全距离 m，悬空 `0.05`，落地 `0.2` |
| `dry_run` | `false` | `true` = 不发 cmd_vel，只看推理输出 |

---

## 诊断命令

### 纹理梯度

```bash
python3 -c "
import rospy, numpy as np
from sensor_msgs.msg import Image
rospy.init_node('diag')
msg = rospy.wait_for_message('/ppo/rgb', Image, timeout=10)
data = np.frombuffer(msg.data, dtype=np.uint8).reshape(256,256,3)
gray = data.astype(float).mean(axis=2)
grad = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
print(f'纹理梯度={grad:.1f} (目标>25)')
"
```

### 深度图有效像素

```bash
python3 -c "
import rospy, numpy as np
from sensor_msgs.msg import Image
rospy.init_node('diag')
msg = rospy.wait_for_message('/ppo/depth', Image, timeout=10)
d = np.frombuffer(msg.data, dtype=np.float32).reshape(256,256)
center = d[77:179, 77:179]
v = center[center > 0.001]
print(f'有效像素: {len(v)}/{center.size} ({100*len(v)/center.size:.1f}%)')
print(f'min={v.min():.4f} ({v.min()*10:.2f}m) mean={v.mean():.4f} ({v.mean()*10:.2f}m)')
"
```

---

## 多轮测试流程

每轮测试必须重启底盘（odom 归零）：

```bash
# 1. Ctrl-C 终端 2 的底盘
# 2. 重启
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch

# 3. 等 "Odom sensor activated"
# 4. 终端 6 发 goal
# 5. 观察 M3 日志 → Goal reached! 或 Timeout
# 6. 回到第 1 步
```

---

## 模型文件位置（Jetson）

```
~/M3/
├── ckpt.49.pth            # Habitat RGBD
├── policy_rgbd_jit.pt     # JIT RGBD
├── policy_depth_jit.pt    # JIT Depth
├── s100_inference_node.py
├── policy_wrappers.py
├── preprocess.py
├── action_controller.py
├── habitat_stub.py
├── cmd_vel_logger.py
└── launch/s100_deploy.launch
```

## M2/M3 代码位置（Windows）

```
D:\AMR-Navigation-Project\S100差速服务机器人\真机部署\
├── M3\                        # M3 工作目录
│   ├── s100_inference_node.py
│   ├── policy_wrappers.py
│   ├── preprocess.py
│   ├── action_controller.py
│   ├── habitat_stub.py
│   ├── cmd_vel_logger.py
│   ├── CMakeLists.txt
│   └── launch/s100_deploy.launch
├── m2_nodes\                  # M2 工作目录
│   ├── ppo_navigation/        # ROS 包
│   └── camera_preprocessor.py
├── jetson_inference\          # M1 工作目录
│   └── load_and_infer.py
├── 01-目标.md
├── 02-技术栈.md
└── 03-Roadmap.md
```

---

## 常见问题

| 症状 | 原因 | 解决 |
|---|---|---|
| `No such file: conda.sh` | launch 文件残留 conda prefix | 确认 shebang 指向 conda python，去掉 launch-prefix |
| `Safety stop` 持续触发 | 相机太低看到近处地板 | 降低 `min_depth_for_safety:=0.05` |
| 机器人原地打转 | 纹理弱，模型无法判断方向 | 环境加视觉特征 或 换 `jit_depth` |
| odom 漂移，第二轮走到错误方向 | 没有重启底盘 | 每轮测试前重启终端 2 |
| 全 STOP 不前进 | 可能深度单位不匹配 | 诊断输出贴给 Claude |
| `exit code 1, cmd bash -c ...` | conda 路径或 shebang 问题 | `head -1 ~/M3/s100_inference_node.py` 确认 |
