#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# === Jetson 部署精简版，2026-08-02 ===
# 原版会无条件预加载 IL trainers（需要 lmdb/webdataset）和 VER trainer（需要
# faster_fifo/threadpoolctl），这些都是训练/模仿学习专用代码，机器人推理阶段
# 完全用不到。真机部署只需要 `habitat_baselines.rl.ddppo.policy.resnet_policy`
# 这条路径，Python import 子模块不要求父包 __init__.py 预先绑定这些名字，
# 所以直接砍掉，避免拉一堆离线机器人装不上的重依赖。
# 云端 habitat39 训练环境请继续用原版 __init__.py，不要用这份精简版。
from habitat_baselines.version import VERSION as __version__  # noqa: F401

__all__: list = []
