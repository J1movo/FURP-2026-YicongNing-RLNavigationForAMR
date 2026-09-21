#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# === Jetson 部署精简版，2026-08-02 ===
# 原版会预加载 VectorEnvFactory / HabitatVectorEnvFactory，这两个是训练时
# 用于批量并行跑仿真环境的工厂类，机器人推理阶段（单个真实环境，不是并行仿真）
# 用不到。真机部署只需要 `habitat_baselines.common.baseline_registry` 这条路径，
# 不依赖这里预先绑定的名字，所以直接砍掉。
# 云端 habitat39 训练环境请继续用原版 __init__.py，不要用这份精简版。
