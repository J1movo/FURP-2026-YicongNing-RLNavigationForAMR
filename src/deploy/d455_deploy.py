#!/usr/bin/env python3
"""
D455 + PointNav → TurtleBot3 autonomous navigation.

Pipeline:
    /goal_pose (RViz click) → relative target (dx, dy, dθ)
    D455 depth → preprocess → model inference → discrete action
    discrete action → /cmd_vel (linear.x, angular.z)

Dependencies (on Orange Pi):
    pip install pyrealsense2 numpy opencv-python torch

Usage:
    python3 d455_deploy.py --model model_depth_only.pt

Press Enter in the terminal to cancel the current goal.
"""

import argparse
import math
import sys
import threading
import time

import numpy as np
import pyrealsense2 as rs
import torch

from d455_preprocess import preprocess


# ---------------------------------------------------------------------------
# Target tracking (odom + goal → Habitat POLAR goal)
# ---------------------------------------------------------------------------

class TargetTracker:
    """Tracks the robot pose from odometry and computes goal-relative vector."""

    def __init__(self):
        self.x: float = 0.0    # current robot x
        self.y: float = 0.0    # current robot y
        self.yaw: float = 0.0   # current heading (rad)
        self.goal_x: float | None = None
        self.goal_y: float | None = None
        self._lock = threading.Lock()

    def update_odom(self, x: float, y: float, yaw_qz: float, yaw_qw: float):
        """Update current pose from odometry."""
        with self._lock:
            self.x = x
            self.y = y
            self.yaw = _quat_to_yaw(yaw_qz, yaw_qw)

    def set_goal(self, gx: float, gy: float):
        """Set a new navigation goal."""
        with self._lock:
            self.goal_x = gx
            self.goal_y = gy

    def get_relative(self) -> tuple[float, float, float] | None:
        """
        Habitat POLAR goal: [rho (m), -phi (rad), compass_heading (rad)]

        Matches PointGoalWithGPSCompassSensor (POLAR, dim=2 + compass).
        """
        with self._lock:
            if self.goal_x is None:
                return None
            dx = self.goal_x - self.x
            dy = self.goal_y - self.y
            rho = math.hypot(dx, dy)

            # angle to goal in agent frame
            c, s = math.cos(self.yaw), math.sin(self.yaw)
            dx_r = -dx * s + dy * c   # agent's right
            dz_r =  dx * c + dy * s   # agent's forward
            phi = math.atan2(dx_r, dz_r)  # +phi = goal is to the right

            return (rho, -phi, self.yaw)


# ---------------------------------------------------------------------------
# D455 + Model Inference
# ---------------------------------------------------------------------------

class D455Navigator:
    """Reads D455 depth, runs TorchScript PointNav, returns (lin, ang)."""

    ACTION_NAMES = ["STOP", "FORWARD", "TURN_LEFT", "TURN_RIGHT"]

    def __init__(self, model_path: str):
        self.model = torch.jit.load(model_path)
        self.hx = torch.zeros(3, 1, 512)
        self.tracker = TargetTracker()

        self._pipe = rs.pipeline()
        cfg = rs.config()
        cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self._pipe.start(cfg)

        self._running = True

    def set_goal(self, x: float, y: float):
        self.tracker.set_goal(x, y)
        self.hx.zero_()  # reset GRU for new episode

    def cancel_goal(self):
        self.tracker.set_goal(None, None)
        self.hx.zero_()

    def step(self) -> tuple[float, float]:
        """Process one frame → (linear_x, angular_z). Returns (0, 0) if no goal."""
        rel = self.tracker.get_relative()
        if rel is None:
            return (0.0, 0.0)

        # read depth
        frames = self._pipe.wait_for_frames()
        depth_np = preprocess(frames.get_depth_frame())  # (1, 256, 256)

        # torch tensors
        depth_t = torch.from_numpy(depth_np).unsqueeze(0)  # (1, 1, 256, 256)
        goal_t = torch.tensor([rel], dtype=torch.float32)   # (1, 3)

        with torch.no_grad():
            logits, self.hx = self.model(depth_t, goal_t, self.hx)
        action = int(logits.argmax(dim=1).item())

        return self._action_to_twist(action)

    @staticmethod
    def _action_to_twist(action: int) -> tuple[float, float]:
        return {0: (0.0, 0.0), 1: (0.22, 0.0), 2: (0.0, 1.0), 3: (0.0, -1.0)}.get(action, (0.0, 0.0))

    def run_standalone(self, freq: float = 10.0):
        """
        Run in standalone mode (no ROS). Prints actions to stdout.
        Press Enter to stop.
        """
        print("[D455Navigator] Standalone mode — depth + model only.")
        print("[D455Navigator] Set goal via code or interactive prompt.")

        # test goal: 2 m forward (robot at 0,0, yaw=0 faces +x)
        self.set_goal(2.0, 0.0)
        period = 1.0 / freq

        try:
            while self._running:
                lin, ang = self.step()
                action_name = D455Navigator.ACTION_NAMES[
                    max(0, min(3, int(
                        0 if lin == 0 and ang == 0 else
                        1 if lin > 0 else
                        2 if ang > 0 else 3
                    )))
                ]
                print(f"  Twist: ({lin:+.2f}, {ang:+.2f})  [{action_name}]",
                      flush=True)
                time.sleep(period)
        except KeyboardInterrupt:
            print("\n[D455Navigator] Interrupted.")
        finally:
            self._pipe.stop()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _quat_to_yaw(z: float, w: float) -> float:
    """Convert quaternion (z, w) component to yaw angle."""
    return math.atan2(2.0 * w * z, 1.0 - 2.0 * z * z)


def _normalize_angle(a: float) -> float:
    """Wrap angle to [-π, π]."""
    return (a + math.pi) % (2 * math.pi) - math.pi


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="D455 + PointNav navigation")
    parser.add_argument("--model", default="policy_depth_jit.pt",
                        help="Path to exported model checkpoint")
    parser.add_argument("--freq", type=float, default=10.0,
                        help="Control frequency (Hz)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run inference but do not publish cmd_vel")
    parser.add_argument("--ros", action="store_true",
                        help="Run as ROS 2 node (requires rclpy)")
    args = parser.parse_args()

    if args.ros:
        _run_ros_node(args)
    else:
        nav = D455Navigator(args.model)
        nav.run_standalone(freq=args.freq)


def _run_ros_node(args):
    """ROS 2 mode — publishes /cmd_vel."""
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped, Twist
    from nav_msgs.msg import Odometry

    class D455Node(Node):
        def __init__(self):
            super().__init__("d455_pointnav")
            self.nav = D455Navigator(args.model)
            self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
            # subscribe to both common goal topics
            self.goal_sub1 = self.create_subscription(
                PoseStamped, "/move_base_simple/goal", self._goal_cb, 10)
            self.goal_sub2 = self.create_subscription(
                PoseStamped, "/goal_pose", self._goal_cb, 10)
            self.odom_sub = self.create_subscription(
                Odometry, "/odom", self._odom_cb, 10)
            period = 1.0 / args.freq
            self.timer = self.create_timer(period, self._control_loop)
            self.get_logger().info("D455 PointNav node ready.")
            self._step = 0

        def _goal_cb(self, msg: PoseStamped):
            gx = msg.pose.position.x
            gy = msg.pose.position.y
            self.nav.set_goal(gx, gy)
            self.get_logger().info(f"Goal: ({gx:.2f}, {gy:.2f})")

        def _odom_cb(self, msg: Odometry):
            p = msg.pose.pose.position
            q = msg.pose.pose.orientation
            self.nav.tracker.update_odom(p.x, p.y, q.z, q.w)

        def _control_loop(self):
            lin, ang = self.nav.step()
            self._step += 1
            if self._step % 20 == 0:  # every 2s
                t = self.nav.tracker
                rel = t.get_relative()
                names = D455Navigator.ACTION_NAMES
                a = 0 if lin == 0 and ang == 0 else (1 if lin > 0 else (2 if ang > 0 else 3))
                if rel is not None:
                    print(f"  Pose({t.x:.1f},{t.y:.1f}) Goal({t.goal_x},{t.goal_y}) "
                          f"rho={rel[0]:.1f} phi={rel[1]:.2f} → {names[a]}", flush=True)
            if not args.dry_run:
                twist = Twist()
                twist.linear.x = lin
                twist.angular.z = ang
                self.cmd_pub.publish(twist)

    rclpy.init()
    node = D455Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.nav._pipe.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
