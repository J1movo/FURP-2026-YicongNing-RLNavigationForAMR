# 合作阶段材料出处声明 (Provenance)

> 本目录下的文件**不是本仓库作者（Yicong Ning）产出的成果**，而是从合作者的 FURP 仓库下载后用于期末报告的**对照与引用材料**。所有引用处均在报告正文与图注中署名。

## 来源

| 项目 | 内容 |
|------|------|
| 仓库 | `https://github.com/ssyzc19/furp-2026-Zhihao-Chen-End-to-End-RL-Navigation` |
| 分支 | `master` |
| 作者 | **Zhihao Chen**（FURP 2026，同一课题的合作阶段） |
| 许可证 | MIT License, © 2026 Zhihao Chen（见 `upstream/LICENSE.md`） |
| 下载日期 | 2026-09-21（本机） |
| 下载方式 | `raw.githubusercontent.com` 直接拉取（仓库为公开仓库，无需认证） |

## 已下载文件清单

### `results/` —— 评估数据

| 文件 | 大小 | 说明 |
|---|---|---|
| `failure_analysis/baseline_seed100.json` | 54,646 B | 200 episode 逐条记录，需重新评估 |
| `failure_analysis/baseline_seed200.json` | 55,041 B | 同上 |
| `failure_analysis/baseline_seed300.json` | 55,021 B | 同上 |
| `failure_analysis/stop_aware_summary.json` | 827 B | stop-aware 消融与真机结论（纯文本记录） |
| `eval_summary.csv` | 662 B | 7 组实验 × 10 列的汇总指标 |

逐 episode JSON 的字段为：`scene_id, episode_id, success, spl, distance_to_goal, reward`（**注意：无 collision / 碰撞字段**，故本报告无法给出碰撞率。）

文件 md5（供校验）：

```
ad901a0d12bcc91ede63f5c202734bc8  baseline_seed100.json
bfc79485a67ecdec818d7ee5fe1ba8aa  baseline_seed200.json
803444e32ea53bd58e84f4490a75f8e6  baseline_seed300.json
```

### `figures/` —— 图表

| 文件 | 说明 |
|---|---|
| `tb_{success,spl,reward}_baseline_3seeds.png` | 三 seed 训练曲线（TensorBoard 截图） |
| `tb_{success,spl,reward}_5e7.png` | 5e7 延长训练曲线 |
| `fig1_sr_comparison.png` … `fig6_improvement_path.png` | 对比 / 失败分解 / DTG 分布 / 跨 seed 一致性 / 改进路径 |
| `topdown_{success,lost,near_miss,comparison_strip}.png` | 俯视轨迹可视化 |

### `videos/` —— 演示片段

| 文件 | 说明 |
|---|---|
| `01_lost_dtg12.77m.mp4` | lost 失败案例（终点距目标 12.77 m） |
| `02_nearmiss_dtg0.21m.mp4` | near_miss 失败案例（0.21 m，差一点到 0.2 m 阈值） |
| `03_success_dtg0.01m.mp4` | 成功案例（0.01 m） |

### `upstream/` —— 上游文档原文（仅供对照，不直接引用为结论）

| 文件 | 说明 |
|---|---|
| `REPORT.md` | 合作者的报告草稿（目标会议 ICRA/IROS，2026-08-07 版） |
| `EVIDENCE_INVENTORY.md` | 合作者自撰的证据账本（明确标注哪些产物缺失） |
| `deployment_STARTUP.md` | 真机 7 终端启动指南 |
| `deployment_README.md` | 部署说明 |
| `LICENSE.md` | MIT 许可证原文 |

## 本目录内容的使用边界

1. **仅作对照与引用**：报告 §V 的主体是本人训练的 Gibson 双模型；本目录数据用于§VII.D（HM3D 模型失败分类）与 §IV/§V 的跨 seed 对照，均标注来源。
2. **不冒充本人成果**：所有引用处写明「数据来源：合作者 Zhihao Chen 仓库」。
3. **不作为已验证事实的部分**：`stop_aware_summary.json` 中 `real_robot` 条目（`"Goal reached (2026-08-05)"` / `"Goal reached (2026-08-07)"`）为纯文本断言，合作者自己的 `EVIDENCE_INVENTORY.md` 即将其真机证据标为缺失，故报告不将其列为已核实结果。
4. **本报告独立重算过的数据**：三个 `baseline_seed*.json` 的 SR / SPL / 平均 DTG /失败分解均由本人用脚本重新计算，结果与上游一致（见报告附录 A）。

## 未下载的内容

模型权重（`*.pth` / `*.pt`，约 90 MB/个）、HM3D 场景数据、TensorBoard event 文件、训练日志，以及真机视频/日志 —— 这些均不在上游仓库内（`.gitignore` 排除或存放于 AutoDL / Jetson / 本地 D 盘），因此本目录不包含，报告中亦不将其作为已核实结论引用。
