# 可视化证据清单

> 所有媒体文件保持在原位（D盘空间不足），此文件为索引。
> 视频用于 demo video，TensorBoard 用于截图，viz_topdown 用于论文配图。

---

## 一、Episode 回放视频（MP4，第一人称视角）

**位置**：`D:\AMR-Navigation-Project\habitat-lab-original\video_dir\`

### 入选 — Near-Miss 典型案例（DTG 0.20-0.22m，差一点就成功）

| 文件 | DTG | 用途 |
|------|:---:|------|
| `episode=3_1-ckpt=9-...success=0.00-dtg=0.21.mp4` | 0.21m | ⭐ 最佳 near_miss 案例，只差 0.01m |
| `episode=31_1-ckpt=9-...success=0.00-dtg=0.22.mp4` | 0.22m | near_miss 典型案例 |
| `seed300/episode=9_1-ckpt=45-...success=0.00-dtg=0.20.mp4` | 0.20m | 刚好在边界上 |
| `seed300/episode=23_1-ckpt=17-...success=0.00-dtg=0.21.mp4` | 0.21m | 同上 |

### 入选 — Lost 典型案例（DTG > 10m，完全迷路）

| 文件 | DTG | 用途 |
|------|:---:|------|
| `seed300/episode=42_1-ckpt=1-...success=0.00-dtg=14.73.mp4` | 14.73m | ⭐ 最离谱的 lost 案例 |
| `seed300/episode=23_1-ckpt=0-...success=0.00-dtg=12.77.mp4` | 12.77m | lost 典型案例 |
| `seed300/episode=35_1-ckpt=1-...success=0.00-dtg=10.20.mp4` | 10.20m | lost 典型案例 |

### 入选 — 成功案例（对比用）

| 文件 | DTG | SPL | 用途 |
|------|:---:|:---:|------|
| `episode=33_1-ckpt=9-...success=1.00-dtg=0.05-spl=0.95.mp4` | 0.05m | 0.95 | ⭐ 近乎完美 |
| `episode=41_1-ckpt=49-...success=1.00-dtg=0.01-spl=0.94.mp4` | 0.01m | 0.94 | ⭐ 极其精准 |
| `episode=29_1-ckpt=9-...success=1.00-dtg=0.13-spl=0.90.mp4` | 0.13m | 0.90 | 平衡案例 |

---

## 二、TensorBoard 训练曲线

**位置**：`D:\AMR-Navigation-Project\autodl\exp\<实验名>\tb\`

### 所有实验及大小

| 实验 | TB 大小 | 关键曲线 |
|------|:------:|------|
| baseline_seed100 | 13 MB | success, SPL, reward, value_loss, dist_entropy, grad_norm |
| baseline_seed200 | 11 MB | 同上 |
| baseline_seed300 | 11 MB | 同上 |
| stop_aware_seed100 | 11 MB | 同上（value_loss 更高, grad_norm 更高） |
| stop_aware_seed200 | 11 MB | 同上（Q2熵崩溃可见） |
| stop_aware_seed300 | 11 MB | 同上（最稳定 stop_aware） |
| **stop_aware_5e7_seed300** | **94 MB** | ⭐ **最重要** — 5e7步完整训练曲线 |
| lr_decay_seed100 | 11 MB | exp-A 消融 |
| reward_norm_seed100 | 11 MB | P1 消融 |
| p1a_tau_seed100 | 11 MB | P1a 消融 |

### 论文需要的 TensorBoard 截图

1. **Success rate 对比** — baseline vs stop_aware vs 5e7（三线同图）
2. **Value loss 对比** — 展示 stop_aware 的 value_loss 上升（+78%）
3. **Dist_entropy** — 展示 stop_aware_seed200 的 Q2 熵崩溃
4. **SPL 对比** — 展示 5e7 的 SPL 提升 (+10.1%)

> 启动 TensorBoard：`tensorboard --logdir D:\AMR-Navigation-Project\autodl\exp --port 6006`
> 然后浏览器截图，PNG 格式，放入 `results/figures/`

---

## 三、Top-Down 轨迹图（可生成）

**脚本**：`D:\AMR-Navigation-Project\autodl\exp\experiments\baseline\viz_topdown_path.py`

### 功能

- 生成 150 DPI 俯视轨迹图（8×8 inches，适合论文配图）
- 显示：可行走区域、障碍物、agent 轨迹、起点（绿色）、目标（红色0.2m半径）
- 标题标注 SUCCESS/FAILURE + DTG + SPL + Steps
- 可生成 GIF 动画

### 建议生成的图

| 用途 | 模型 | Episode | 类型 |
|------|------|---------|:--:|
| 论文 Fig.1 | baseline_seed300 | 选择一个 lost episode | lost (DTG>10m) |
| 论文 Fig.2 | baseline_seed300 | 选择一个 success | success (DTG<0.1m) |
| 论文 Fig.3 | baseline_seed300 | 选择一个 near_miss | near_miss (DTG~0.22m) |
| 视频 | 同上 | 生成 GIF 动画版 | 三个类型各一 |

### 使用命令（需在 AutoDL 上运行）

```bash
cd /root/habitat-lab
conda activate habitat39
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json

python experiments/viz_topdown_path.py \
  --ckpt /root/autodl-tmp/exp/baseline_seed300/checkpoints/latest.pth \
  --seed 300 \
  --episode-id <从failure_analysis.json中选取> \
  --out experiments/topdown_<类型>.png \
  --gif
```

---

## 四、Habitat 平台图片（用于幻灯片）

**位置**：`D:\AMR-Navigation-Project\habitat-lab-original\`

| 文件 | 用途 |
|------|------|
| `docs/images/habitat-lab-demo-images/habitat-lab-demo.png` | 平台介绍 |
| `docs/images/habitat-lab-tdmap-viz-images/top_down_map.png` | 俯视图示例 |
| `docs/images/quickstart-images/quickstart.png` | 快速开始 |
| `res/img/habitat_logo_with_text_horizontal_blue.png` | Logo |
| `res/img/tensorboard_video_demo.gif` | TB 示例 |

---

## 五、可生成的图表（Python/matplotlib）

从 `failure_analysis.json` 数据可生成：

1. **失败模式堆叠柱状图** — lost/near_miss/bad_stop 三色堆叠，baseline vs stop_aware vs 5e7
2. **DTG 分布直方图** — 成功案例 DTG 分布 + 失败案例 DTG 分布
3. **跨 seed SR 对比箱线图** — baseline (std=0.063) vs stop_aware (std=0.011)
4. **SR vs SPL 散点图** — 每个 seed 一个点，baseline/stop_aware/5e7 三色

---

## 六、真机证据（需录制）

| 证据 | 状态 | 格式 |
|------|:----:|:----:|
| 机器人硬件空镜 | ❌ | 手机视频 1080p |
| 完整导航视频（baseline） | ✅ | 手机视频（已拍？） |
| 完整导航视频（5e7） | ✅ | 手机视频（已拍？） |
| 7 终端启动录屏 | ❌ | OBS 录屏 |
| 推理日志截图 | ❌ | 终端截图 |

---

## 优先级行动清单

| # | 行动 | 产生证据 |
|:--:|------|------|
| 1 | 打开 TensorBoard 截图 4 张关键曲线 | results/figures/tb_*.png |
| 2 | 在 AutoDL 上运行 viz_topdown_path.py 生成 3 张轨迹图 | results/figures/topdown_*.png |
| 3 | 用 Python 从 failure_analysis.json 生成 4 张统计图 | results/figures/chart_*.png |
| 4 | 手机上确认/补拍真机导航视频 | video/robot_*.mp4 |
| 5 | OBS 录屏 TensorBoard 曲线（用于视频动态展示） | video/sim_*.mp4 |
| 6 | 将 521 个 MP4 中的 5-6 个精品拷贝到 results/figures/ | results/figures/ep_*.mp4 |
