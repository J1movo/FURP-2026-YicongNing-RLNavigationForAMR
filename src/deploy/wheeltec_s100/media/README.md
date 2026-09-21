# WHEELTEC S100 真机素材

> 部署阶段拍摄的机器人实物照片与基线导航演示录像。在 `REPORT.md` §VI.A 与 §VI.I 中使用。

## 文件清单

| 文件 | 大小 | 说明 |
|---|---|---|
| `wheeltec_s100_hardware.jpg` | 236 KB | **机器人本体照片**。可见白色底盘、顶部红色急停按钮、环形指示灯、无线天线、RGB 状态灯条，以及顶部安装的**奥比中光（Orbbec）深度相机**（USB 连接）。 |
| `wheeltec_s100_nav2_baseline.mp4` | 67 MB | **Nav2 基线导航实机演示**。1920×1080 / 30 fps / 35.9 s（1078 帧）。画面交替呈现实验室走廊实景中的机器人，与同期笔记本屏幕上的 RViz 界面。 |
| `gazebo_ppo_test.mp4` | 5.0 MB | **Gazebo 仿真测试录屏**。19.1 s 屏幕录制，2136×1296，约 25 fps。内容为 PPO 策略在 Gazebo 中的实测过程（该次测试**失败**：模型持续输出 TURN_RIGHT 至超时，见报告 §VI.H）。 |
| `frames/nav2_demo_scene_{1,2,3}.png` | 各 ~0.5 MB | 演示视频中的**实景**关键帧（540×960，已校正方向）。 |
| `frames/nav2_demo_rviz_{1,2,3}.png` | 各 ~0.5 MB | 演示视频中的 **RViz 界面**关键帧（540×960，已校正方向）。可见 `Global Costmap` / `Local Costmap` / `Map` / `Particle Cloud` / `RobotModel` / `LaserScan` / `MapCloud` / `Path` 等显示项。 |

校验和：

```
2d47e1f222e75c150a5238fb2d14b815  wheeltec_s100_hardware.jpg
ea2b8d4cb833591767b85295148a8172  wheeltec_s100_nav2_baseline.mp4
```

## 出处

| 项 | 内容 |
|---|---|
| 来源 | 项目组内部提供（经微信传阅） |
| 拍摄时间 | **2026-08-02 19:10**（原始文件名 `VID20260802191053.mp4` 编码） |
| 归档日期 | 2026-09-21 |
| 拍摄地点 | 实验室走廊（人字纹地毯，含纸箱障碍物与展架） |

## 关键帧抽取方式

用 OpenCV 按视频时长比例抽帧，再统一缩放至 960×540：

```python
import cv2
cap = cv2.VideoCapture('wheeltec_s100_nav2_baseline.mp4')
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
for frac, name in [(0.02,'scene_1'),(0.42,'scene_2'),(0.62,'scene_3'),
                   (0.30,'rviz_1'),(0.83,'rviz_2'),(0.97,'rviz_3')]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(n*frac))
    ok, img = cap.read()
    if ok:
        img = cv2.resize(img, (960, 540), interpolation=cv2.INTER_AREA)
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)   # 源视频方向偏转 90°，需顺时针校正
        cv2.imwrite(f'frames/nav2_demo_{name}.png', img)
```

## ⚠️ 素材定位 —— 能说明什么、不能说明什么

**这组素材记录的是传统 Nav2 导航栈的运行，不是本项目的 PPO 策略。**

| 说明 ✅ | 不说明 ❌ |
|---|---|
| S100 硬件平台可正常上电运行 | PPO 策略已在真机上跑通 |
| 底盘驱动、里程计、传感器链路工作正常 | PPO 策略达到了「到达 + 零碰撞 + 无人工干预」标准 |
| **传统 Nav2 栈**（AMCL + costmap + 规划器）在该平台上可用 | PPO 优于或劣于 Nav2 |
| 存在可供对比的基线系统 | —— |

PPO 路线的真机状态见报告 §VI.G（单机推理验证通过）与 §VI.H（仿真测试未通过）；满足三条「跑通」标准的完整真机运行尚未实现。

## 关于体积

68 MB 的视频超过了仓库 `.gitignore` 对大文件的一般约定（该文件声明「链接来源而不提交」）。此处破例提交，理由是：这是全项目**唯一的真机实拍 footage**，且 FURP 最终提交要求包含「轨迹截图或演示片段」。若需缩减仓库体积，可只保留 `frames/`（3.2 MB）而删除视频文件，报告中的关键帧引用不受影响。
