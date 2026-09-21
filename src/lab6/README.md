# Nav2 导航操作指南

TurtleBot3 + Nav2 在 Gazebo 仿真和真机上的操作速查。

---

## 1. Gazebo 仿真

### 1.1 启动仿真 + Nav2

```bash
export TURTLEBOT3_MODEL=burger
# Gazebo
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
# Nav2 + 地图
ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=$HOME/tb3_map.yaml
```

可用世界：`empty_world`、`turtlebot3_world`、`turtlebot3_house`。

### 1.2 设置初始位姿

RViz 中用 **"2D Pose Estimate"**（绿色箭头）在地图上标注机器人当前位置和朝向。AMCL 需要这个来收敛粒子。

### 1.3 导航

用 **"2D Nav Goal"**（紫色旗帜）在地图上点击目标点。

---

## 2. 真机部署（TB3 Burger）

### 2.1 硬件检查

- [ ] TB3 通电，电池充足
- [ ] 香橙派连接 D455（USB 3.0）
- [ ] 所有机器在同一 ROS 2 网络（`echo $ROS_DOMAIN_ID` 一致）
- [ ] 地图文件就绪（`~/tb3_map.yaml` + `~/tb3_map.pgm`）

### 2.2 启动顺序

**终端 1 — TB3 树莓派：**
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```

**终端 2 — 笔记本：**
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=$HOME/tb3_map.yaml
```

**终端 3 — 香橙派（可选，PointNav 控制）：**
```bash
cd ~/furp_code/YicongNing/d455_depth_only
python3 d455_deploy.py --model policy_depth_jit.pt --ros
```

### 2.3 操作流程

1. RViz 中用 **"2D Pose Estimate"** 标记机器人实际位置
2. 等待 AMCL 粒子收敛（绿色粒子聚集在机器人周围）
3. 用 **"2D Nav Goal"** 点击目标导航
4. 监控 `/cmd_vel` 和 LiDAR 扫描确保安全

---

## 3. SLAM 建图

### 3.1 Cartographer

```bash
# 终端 1: 底盘
ros2 launch turtlebot3_bringup robot.launch.py

# 终端 2: Cartographer
ros2 launch turtlebot3_cartographer cartographer.launch.py

# 终端 3: 遥控
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

缓慢遥控机器人覆盖全部区域。建图完成后：

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map
# 保存 ~/my_map.yaml 和 ~/my_map.pgm
```

### 3.2 SLAM Toolbox（备选）

```bash
ros2 launch slam_toolbox online_async_launch.py
```

---

## 4. 常见问题

| 现象 | 排查方法 |
|------|----------|
| 机器人不动 | `ros2 topic echo /cmd_vel` — 有数据发出吗？ |
| AMCL 不收敛 | 用 "2D Pose Estimate" 重新设位姿，尽量精确 |
| 目标收不到 | `ros2 topic info /goal_pose` 或 `/move_base_simple/goal` |
| 地图不显示 | 检查 `map:=` 路径是否正确 |
| 机器人来回震荡 | 降低 Nav2 配置中的最大速度 |
| 里程计漂移 | 用 "2D Pose Estimate" 重新定位 |
| 定位丢失 | 在开阔区域重新设置位姿 |

### 快速诊断

```bash
# 查看所有话题
ros2 topic list

# 确认 AMCL 正常
ros2 topic echo /amcl_pose --once

# 检查 TF 树
ros2 run tf2_tools view_frames

# 查看 Nav2 生命周期
ros2 lifecycle list /controller_server
ros2 lifecycle list /planner_server
```

---

## 5. Nav2 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `controller_server` | DWB | 局部规划器 |
| `planner_server` | Smac Hybrid-A* | 全局规划器 |
| `max_vel_x` | 0.26 m/s | 最大前进速度 |
| `max_vel_theta` | 1.0 rad/s | 最大转向速度 |
| `goal_tolerance` | 0.25 m | 到达判定距离 |
| `inflation_radius` | 0.55 m | 障碍物膨胀半径 |

可通过 TB3 导航包中的 `nav2_params.yaml` 自定义。

---

## 6. Nav2 + PointNav 集成架构

PointNav 替换 Nav2 的局部规划器，全局规划和定位保持不变。

| 组件 | 标准 Nav2 | PointNav 模式 |
|------|-----------|---------------|
| 全局规划器 | A* (smac) | A*（保留） |
| AMCL 定位 | 启用 | 启用 |
| 局部规划器 | DWB | PointNav 节点 |
| /cmd_vel | 来自 DWB | 来自 PointNav |

PointNav 订阅 `/plan` 获取全局路径上的子目标。

---

## 7. 常用话题

| 话题 | 类型 | 说明 |
|------|------|------|
| `/cmd_vel` | Twist | 发给机器人的速度指令 |
| `/odom` | Odometry | 轮式里程计 |
| `/scan` | LaserScan | LiDAR 扫描 |
| `/map` | OccupancyGrid | 地图 |
| `/plan` | Path | 全局规划路径 |
| `/amcl_pose` | PoseWithCovariance | 机器人位姿估计 |
| `/goal_pose` | PoseStamped | 导航目标点 |
| `/move_base_simple/goal` | PoseStamped | RViz 点击的目标 |
| `/camera/depth/image_raw` | Image | D455 深度图（真机） |
