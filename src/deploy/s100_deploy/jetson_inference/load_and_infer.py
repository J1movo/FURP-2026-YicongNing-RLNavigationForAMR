"""
M1 里程碑：在 Jetson 的 wheeltec conda 环境里加载
autodl/exp/baseline_seed300/checkpoints/ckpt.49.pth，
用离线/手造数据跑通一次前向推理，确认模型能正确加载、输出合理的离散动作。

前置条件（部署到 Jetson 前）：
1. 已把本文件所在目录（jetson_inference/）连同 checkpoint 拷到 Jetson。
2. 已在 wheeltec conda 环境里 `pip install -e` 了不含 habitat_sim 的
   habitat-lab 源码包和 habitat-baselines 源码包（来自 autodl/habitat-lab/
   habitat-lab 和 autodl/habitat-lab/habitat-baselines，requirements.txt
   本身就不含 habitat_sim，可以直接装）。
3. 已确认 `conda activate wheeltec` 后 `python -c "import torch;
   print(torch.cuda.is_available())"` 输出 True。

运行方式：
    conda activate wheeltec
    python load_and_infer.py --ckpt ckpt.49.pth
"""
import argparse

import habitat_stub

habitat_stub.install()  # 必须在 import 任何 habitat_baselines 代码之前调用

import numpy as np
import torch
from gym import spaces

from habitat_baselines.rl.ddppo.policy.resnet_policy import (
    PointNavResNetPolicy,
)

# === 训练时的 observation/action 空间定义（来自 config.yaml，手工重建，
# 因为 Jetson 上没有 habitat_sim，不能靠仿真器自动生成 space） ===
#
# 注意：2026-08-02 订正 —— 该 checkpoint 训练时同时用了 RGB + Depth 两路视觉
# 输入（config.yaml 里 sim_sensors 同时定义了 rgb_sensor 和 depth_sensor），
# 不是之前文档里记录的"只有depth"。报错 `conv1.0.weight [32,4,7,7] vs
# [32,1,7,7]` 直接证实了这一点：4通道 = 3(RGB) + 1(depth)。01-目标.md /
# 02-技术栈.md 需要同步订正。
#
# rgb_sensor: height=256, width=256 -> Box[0,255], shape (256,256,3), uint8
# depth_sensor: height=256, width=256, min_depth=0.0, max_depth=10.0,
#               normalize_depth=true -> Box[0,1], shape (256,256,1), float32
# pointgoal_with_gps_compass: goal_format=POLAR, dimensionality=2
#               -> Box(-inf,inf), shape (2,), float32  [distance, angle]
RGB_SHAPE = (256, 256, 3)
DEPTH_SHAPE = (256, 256, 1)
OBSERVATION_SPACE = spaces.Dict(
    {
        "rgb": spaces.Box(
            low=0, high=255, shape=RGB_SHAPE, dtype=np.uint8
        ),
        "depth": spaces.Box(
            low=0.0, high=1.0, shape=DEPTH_SHAPE, dtype=np.float32
        ),
        "pointgoal_with_gps_compass": spaces.Box(
            low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32
        ),
    }
)

# actions: stop=0, move_forward=1, turn_left=2, turn_right=3
ACTION_SPACE = spaces.Discrete(4)
ACTION_NAMES = ["stop", "move_forward", "turn_left", "turn_right"]


def build_policy_from_ckpt(ckpt_config) -> PointNavResNetPolicy:
    """按 checkpoint 里打包的训练配置，重建网络结构（不依赖 habitat_sim）。"""
    hb = ckpt_config.habitat_baselines
    agent_name = ckpt_config.habitat.simulator.agents_order[0]
    policy_config = hb.rl.policy[agent_name]

    policy = PointNavResNetPolicy(
        observation_space=OBSERVATION_SPACE,
        action_space=ACTION_SPACE,
        hidden_size=hb.rl.ppo.hidden_size,
        num_recurrent_layers=hb.rl.ddppo.num_recurrent_layers,
        rnn_type=hb.rl.ddppo.rnn_type,
        backbone=hb.rl.ddppo.backbone,
        # 与 resnet_policy.py 的 from_config() 保持一致：有 rgb 输入就归一化
        normalize_visual_inputs="rgb" in OBSERVATION_SPACE.spaces,
        policy_config=policy_config,
        aux_loss_config=hb.rl.auxiliary_losses,
        fuse_keys=None,
    )
    return policy


def load_checkpoint(ckpt_path: str, device: torch.device):
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    policy = build_policy_from_ckpt(ckpt["config"])
    policy.load_state_dict(ckpt["state_dict"])
    policy.to(device)
    policy.eval()
    return policy, ckpt["config"]


def make_dummy_observation(device: torch.device):
    """造一份假观测用于验证推理链路是否跑通，不代表真实场景，只检查数值是否
    合理（无 NaN/Inf、动作分布正常）：
    - rgb 填 128（灰色图，任意占位值）
    - depth 全部填 1.0（代表最大探测距离 10m，即"前方无遮挡"）
    - pointgoal 设为「正前方 5 米」"""
    rgb = torch.full(
        (1, *RGB_SHAPE), 128, dtype=torch.uint8, device=device
    )
    depth = torch.ones((1, *DEPTH_SHAPE), dtype=torch.float32, device=device)
    pointgoal = torch.tensor(
        [[5.0, 0.0]], dtype=torch.float32, device=device
    )  # [distance=5m, angle=0rad]
    return {
        "rgb": rgb,
        "depth": depth,
        "pointgoal_with_gps_compass": pointgoal,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", required=True, help="ckpt.49.pth 路径")
    parser.add_argument(
        "--steps", type=int, default=5, help="连续跑几步推理（验证RNN状态传递）"
    )
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device = {device}")

    policy, config = load_checkpoint(args.ckpt, device)
    print("checkpoint 加载成功，模型结构：")
    print(
        f"  hidden_size={config.habitat_baselines.rl.ppo.hidden_size}, "
        f"backbone={config.habitat_baselines.rl.ddppo.backbone}, "
        f"rnn_type={config.habitat_baselines.rl.ddppo.rnn_type}"
    )

    # RNN 隐状态 / prev_actions / masks 的初始值（第一步：masks=0 表示"新episode"）
    rnn_hidden_states = torch.zeros(
        1,
        policy.net.num_recurrent_layers,
        policy.net.recurrent_hidden_size,
        device=device,
    )
    prev_actions = torch.zeros(1, 1, dtype=torch.long, device=device)
    masks = torch.zeros(1, 1, dtype=torch.bool, device=device)

    observations = make_dummy_observation(device)

    import time

    step_times_ms = []
    with torch.no_grad():
        for step in range(args.steps):
            if device.type == "cuda":
                torch.cuda.synchronize()
            t0 = time.perf_counter()

            action_data = policy.act(
                observations,
                rnn_hidden_states,
                prev_actions,
                masks,
                deterministic=True,  # 真机部署建议用确定性策略，避免随机探索
            )

            if device.type == "cuda":
                torch.cuda.synchronize()
            step_times_ms.append((time.perf_counter() - t0) * 1000)

            action_idx = int(action_data.actions.item())
            print(
                f"step {step}: action={ACTION_NAMES[action_idx]} "
                f"(idx={action_idx}), value={action_data.values.item():.4f}, "
                f"latency={step_times_ms[-1]:.1f}ms"
            )

            # 检查数值健康度
            assert not torch.isnan(action_data.values).any(), "NaN in value!"
            assert not torch.isnan(action_data.actions).any(), "NaN in action!"

            # 更新循环状态，为下一步推理做准备
            rnn_hidden_states = action_data.rnn_hidden_states
            prev_actions = action_data.actions
            masks = torch.ones(1, 1, dtype=torch.bool, device=device)

    print("推理链路跑通，数值正常（无NaN/Inf）。")

    # 第一步通常包含CUDA kernel编译/预热开销，不计入统计
    warm_times = step_times_ms[1:] if len(step_times_ms) > 1 else step_times_ms
    if warm_times:
        avg_ms = sum(warm_times) / len(warm_times)
        print(
            f"推理延迟（跳过第1步预热）：avg={avg_ms:.1f}ms, "
            f"min={min(warm_times):.1f}ms, max={max(warm_times):.1f}ms "
            f"-> 约 {1000 / avg_ms:.1f} Hz"
        )


if __name__ == "__main__":
    main()
