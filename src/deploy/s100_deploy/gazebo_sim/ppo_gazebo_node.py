#!/usr/bin/env python3
"""
ROS 2 node — PointNav PPO inference with Gazebo TurtleBot3.

Subscribes to Gazebo TB3 topics, preprocesses observations (LiDAR→depth,
RGB resize), sends them to the inference server (conda habitat env) over
TCP, and publishes velocity commands.

Usage (system Python 3.10):
    python3 ppo_gazebo_node.py --model-name latest

Subscriptions:
    /scan          (sensor_msgs/LaserScan)
    /camera/image_raw (sensor_msgs/Image)
    /odom          (nav_msgs/Odometry)
    /goal_pose     (geometry_msgs/PoseStamped)

Publications:
    /cmd_vel       (geometry_msgs/Twist)
"""

import argparse
import json
import math
import socket
import sys
import time

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image

# ---------------------------------------------------------------------------
# Constants (must match training config)
# ---------------------------------------------------------------------------

H, W = 256, 256  # model input resolution
MAX_DEPTH_M = 10.0  # Habitat PointNav default (depth = clip(d, 0, 10) / 10)
FOV_DEG = 90  # training HFOV
MIN_DEPTH_M = 0.0

# Action table
STOP = 0
FORWARD = 1
TURN_LEFT = 2
TURN_RIGHT = 3
ACTION_NAMES = {0: "STOP", 1: "FWD", 2: "LEFT", 3: "RIGHT"}

# Movement params
FORWARD_SPEED = 0.22  # m/s (close to Habitat's 0.25 m/step at ~1 step/s)
TURN_SPEED = 1.0  # rad/s (Habitat: 10°, takes ~0.17s at this speed)
STEP_FORWARD_DIST = 0.25  # metres (matches training)
STEP_TURN_RAD = math.radians(10)  # radians (matches training)


# ---------------------------------------------------------------------------
# LiDAR → depth image
# ---------------------------------------------------------------------------


def scan_to_depth(msg: LaserScan) -> np.ndarray:
    """
    Convert a 360° LiDAR scan into a 256×256 dense depth image (metres).

    Projects points inside a ±FOV/2 wedge onto the image plane.  Each column
    receives the minimum range in that angular bin; empty columns are filled
    with MAX_DEPTH_M.
    """
    ranges = np.array(msg.ranges, dtype=np.float32)
    ranges = np.clip(ranges, msg.range_min, msg.range_max)

    angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))
    half_fov = math.radians(FOV_DEG / 2)

    # Keep only points within the FOV wedge
    mask = (angles >= -half_fov) & (angles <= half_fov)
    rf, af = ranges[mask], angles[mask]

    # Map angles to image columns
    #   angle = -half_fov  → col = 0
    #   angle = +half_fov  → col = W-1
    cols = ((af + half_fov) / (2 * half_fov) * (W - 1)).astype(np.int32)
    cols = np.clip(cols, 0, W - 1)

    # Build depth image (fill with max range as "far")
    depth_img = np.full((H, W), MAX_DEPTH_M, dtype=np.float32)

    for i, col in enumerate(cols):
        d = rf[i]
        if d < msg.range_min or d > msg.range_max - 0.1:
            continue
        # Each column gets minimum depth (closest obstacle)
        depth_img[:, col] = np.minimum(depth_img[:, col], d)
        # Slight expansion to neighbouring columns (fills gaps)
        for dc in [-1, 1]:
            nc = col + dc
            if 0 <= nc < W:
                depth_img[:, nc] = np.minimum(depth_img[:, nc], d * 1.05)

    return depth_img


def depth_to_model(depth_m: np.ndarray) -> np.ndarray:
    """Convert metres-depth to model-normalised format [0, 1]."""
    depth_m = np.clip(depth_m, MIN_DEPTH_M, MAX_DEPTH_M)
    return (depth_m / MAX_DEPTH_M).astype(np.float32)


# ---------------------------------------------------------------------------
# RGB preprocessing
# ---------------------------------------------------------------------------


def preprocess_rgb(rgb_msg: Image, bridge: CvBridge) -> np.ndarray:
    """ROS Image → 256×256 uint8 RGB (model's internal RMA handles norm)."""
    img = bridge.imgmsg_to_cv2(rgb_msg, desired_encoding="rgb8")
    return cv2.resize(img, (W, H), interpolation=cv2.INTER_LINEAR)


def preprocess_depth_camera(depth_msg: Image, bridge: CvBridge) -> np.ndarray:
    """
    Gazebo depth camera → 256×256 float32 [0,1], normalized by MAX_DEPTH_M=10.0.

    Reproduces HabitatSimDepthSensor.get_observation():
        normalized = clip(depth_meters, MIN_DEPTH, MAX_DEPTH) / MAX_DEPTH
    """
    # Gazebo depth camera outputs 32FC1 (meters) or 16UC1 (mm)
    depth_m = bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")
    if depth_msg.encoding == "16UC1":
        depth_m = depth_m.astype(np.float32) / 1000.0
    elif depth_msg.encoding in ("32FC1", "mono16"):
        depth_m = depth_m.astype(np.float32)
    # Handle potential NaN or inf from Gazebo
    depth_m = np.nan_to_num(depth_m, nan=MAX_DEPTH_M, posinf=MAX_DEPTH_M)
    depth_m = np.clip(depth_m, MIN_DEPTH_M, MAX_DEPTH_M)
    depth_norm = depth_m / MAX_DEPTH_M
    return cv2.resize(depth_norm, (W, H), interpolation=cv2.INTER_NEAREST).astype(np.float32)


# ---------------------------------------------------------------------------
# Goal computation (Habitat POLAR format)
# ---------------------------------------------------------------------------


def quat_to_yaw(orientation) -> float:
    q = orientation
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def compute_pointgoal(robot_pose: tuple, goal_pos: tuple) -> tuple:
    """Return (distance_m, angle_rad) in polar coordinates."""
    dx = goal_pos[0] - robot_pose[0]
    dy = goal_pos[1] - robot_pose[1]
    distance = math.hypot(dx, dy)

    c = math.cos(robot_pose[2])
    s = math.sin(robot_pose[2])
    forward = c * dx + s * dy
    right = -s * dx + c * dy
    angle = math.atan2(right, forward)

    return distance, angle


# ---------------------------------------------------------------------------
# TCP client to inference server
# ---------------------------------------------------------------------------


class InferenceClient:
    """Thin TCP client that talks to the inference server."""

    def __init__(self, host="127.0.0.1", port=9876, timeout=2.0):
        self._addr = (host, port)
        self._timeout = timeout
        self._sock: socket.socket | None = None
        self._file = None

    def connect(self):
        self._sock = socket.create_connection(self._addr, timeout=self._timeout)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._file = self._sock.makefile("rw", buffering=1)

    def close(self):
        try:
            if self._file:
                self._file.close()
            if self._sock:
                self._sock.close()
        except OSError:
            pass
        self._file = None
        self._sock = None

    def reset_rnn(self):
        self._send({"reset": True})
        return self._recv()

    def infer(self, rgb_np: np.ndarray, depth_np: np.ndarray, goal: tuple) -> dict:
        """Send observation, return {'action': int, 'latency_ms': float}."""
        req = {
            "rgb": rgb_np.tolist(),
            "depth": depth_np.tolist(),
            "goal": list(goal),
            "reset": False,
        }
        self._send(req)
        return self._recv()

    def _send(self, data: dict):
        try:
            self._file.write(json.dumps(data) + "\n")
            self._file.flush()
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            raise ConnectionError(f"Inference server disconnected: {e}")

    def _recv(self) -> dict:
        try:
            line = self._file.readline()
            if not line:
                raise ConnectionError("Inference server closed connection")
            return json.loads(line)
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            raise ConnectionError(f"Inference server disconnected: {e}")


# ---------------------------------------------------------------------------
# Step action controller (matches Habitat's discrete-step semantics)
# ---------------------------------------------------------------------------


def _norm_angle(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


class StepController:
    """Execute an action as a fixed-displacement step, then stop."""

    def __init__(
        self,
        forward_dist: float = STEP_FORWARD_DIST,
        turn_rad: float = STEP_TURN_RAD,
        forward_speed: float = FORWARD_SPEED,
        turn_speed: float = TURN_SPEED,
    ):
        self.fwd_dist = forward_dist
        self.turn_rad = turn_rad
        self.fwd_speed = forward_speed
        self.turn_speed = turn_speed
        self._active = False
        self._action = None
        self._start_pose = None

    @property
    def is_done(self) -> bool:
        return not self._active

    def start(self, action: int, pose: tuple):
        self._action = action
        self._start_pose = pose
        self._active = action != STOP

    def update(self, pose: tuple):
        """Return (Twist, done)."""
        twist = Twist()
        if not self._active:
            return twist, True

        if self._action == FORWARD:
            dx = pose[0] - self._start_pose[0]
            dy = pose[1] - self._start_pose[1]
            if math.hypot(dx, dy) >= self.fwd_dist:
                self._active = False
                return twist, True
            twist.linear.x = self.fwd_speed

        elif self._action == TURN_LEFT:
            if abs(_norm_angle(pose[2] - self._start_pose[2])) >= self.turn_rad:
                self._active = False
                return twist, True
            twist.angular.z = self.turn_speed

        elif self._action == TURN_RIGHT:
            if abs(_norm_angle(pose[2] - self._start_pose[2])) >= self.turn_rad:
                self._active = False
                return twist, True
            twist.angular.z = -self.turn_speed

        return twist, False


# ---------------------------------------------------------------------------
# ROS 2 Node
# ---------------------------------------------------------------------------


class PointNavGazeboNode(Node):
    def __init__(self, args):
        super().__init__("pointnav_gazebo")

        # Config
        self._server_port = args.port
        self._step_mode = args.step
        self._dry_run = args.dry_run
        self._max_steps = args.max_steps
        self._success_dist = args.success_distance
        self._min_safety_dist = args.min_safety_dist
        self._control_rate = args.control_rate

        # Bridge (ROS image → numpy)
        self.bridge = CvBridge()

        # State
        self._latest_scan: LaserScan | None = None
        self._latest_rgb: Image | None = None
        self._latest_depth: Image | None = None
        self._robot_pose = (0.0, 0.0, 0.0)
        self._goal: tuple | None = None
        self._step_count = 0
        self._episodes = 0

        # Step controller
        self._step_ctrl = StepController()

        # Inference client
        self._client = InferenceClient(port=self._server_port)
        self._client_connected = False
        self._latencies_ms: list[float] = []

        # --- Subscribers ---
        self.create_subscription(LaserScan, "/scan", self._scan_cb, 10)
        self.create_subscription(Image, "/camera/image_raw", self._rgb_cb, 10)
        self.create_subscription(Image, "/camera/depth/image_raw", self._depth_cb, 10)
        self.create_subscription(Odometry, "/odom", self._odom_cb, 10)
        self.create_subscription(PoseStamped, "/goal_pose", self._goal_cb, 10)
        # Also support RViz "2D Nav Goal" topic
        self.create_subscription(
            PoseStamped, "/move_base_simple/goal", self._goal_cb, 10
        )

        # --- Publisher ---
        self._cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        # --- Timer (control loop) ---
        period_s = 1.0 / self._control_rate
        self.create_timer(period_s, self._control_loop)

        self.get_logger().info(
            f"PointNav Gazebo node ready  "
            f"server=localhost:{self._server_port}  "
            f"step_mode={self._step_mode}  dry_run={self._dry_run}"
        )

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _scan_cb(self, msg: LaserScan):
        self._latest_scan = msg

    def _rgb_cb(self, msg: Image):
        self._latest_rgb = msg
        if self._step_count == 0:
            self.get_logger().info(
                f"RGB frame received: {msg.width}x{msg.height}, encoding={msg.encoding}"
            )

    def _depth_cb(self, msg: Image):
        self._latest_depth = msg
        if self._step_count == 0:
            self.get_logger().info(
                f"Depth frame received: {msg.width}x{msg.height}, encoding={msg.encoding}"
            )

    def _odom_cb(self, msg: Odometry):
        p = msg.pose.pose.position
        yaw = quat_to_yaw(msg.pose.pose.orientation)
        self._robot_pose = (p.x, p.y, yaw)

    def _goal_cb(self, msg: PoseStamped):
        gx = msg.pose.position.x
        gy = msg.pose.position.y
        self._goal = (gx, gy)
        self._step_count = 0
        self._step_ctrl = StepController()
        # Reset RNN on new goal
        if self._client_connected:
            try:
                self._client.reset_rnn()
            except ConnectionError:
                pass
        self.get_logger().info(f"New goal: ({gx:.2f}, {gy:.2f})")

    # ------------------------------------------------------------------
    # Control loop
    # ------------------------------------------------------------------

    def _control_loop(self):
        # --- Connect to server on first tick ---
        if not self._client_connected:
            try:
                self._client.connect()
                self._client_connected = True
                self.get_logger().info("Connected to inference server")
            except (ConnectionError, OSError) as e:
                self.get_logger().warn(
                    f"Cannot connect to inference server: {e}. Retrying..."
                )
                return

        # --- No goal → stop ---
        if self._goal is None:
            self._publish_stop()
            return

        # --- Step mode: wait for current action to finish ---
        if self._step_mode and not self._step_ctrl.is_done:
            twist, done = self._step_ctrl.update(self._robot_pose)
            if not self._dry_run:
                self._cmd_pub.publish(twist)
            return

        # --- Need data ---
        if self._latest_scan is None:
            self._publish_stop()
            if self._step_count == 0:
                self.get_logger().info("Waiting for LiDAR data...", throttle_duration_sec=10)
            return

        # --- Timeout ---
        if self._step_count >= self._max_steps:
            dist = math.hypot(
                self._goal[0] - self._robot_pose[0],
                self._goal[1] - self._robot_pose[1],
            )
            self.get_logger().warn(
                f"Episode timeout ({self._max_steps} steps). "
                f"Final distance: {dist:.2f}m"
            )
            self._goal = None
            self._publish_stop()
            return

        # --- Preprocess depth ---
        if self._latest_depth is not None:
            # Real depth camera (Gazebo plugin) — clip, normalize, resize
            depth_np = preprocess_depth_camera(self._latest_depth, self.bridge)
        else:
            # Fall back to LiDAR → pseudo-depth
            depth_m = scan_to_depth(self._latest_scan)
            depth_np = depth_to_model(depth_m)  # (256, 256) float32 [0,1]

        # --- Preprocess RGB ---
        if self._latest_rgb is not None:
            try:
                rgb_np = preprocess_rgb(self._latest_rgb, self.bridge)  # (256,256,3) uint8
            except Exception as e:
                self.get_logger().error(f"RGB preprocessing error: {e}")
                rgb_np = np.full((H, W, 3), 128, dtype=np.uint8)
        else:
            # No RGB yet (common at startup) — use grey placeholder
            rgb_np = np.full((H, W, 3), 128, dtype=np.uint8)

        # --- Goal ---
        goal_dist, goal_angle = compute_pointgoal(self._robot_pose, self._goal)

        # Success check
        if goal_dist < self._success_dist:
            self.get_logger().info(
                f"GOAL REACHED! dist={goal_dist:.3f}m  steps={self._step_count}"
            )
            self._goal = None
            self._episodes += 1
            self._publish_stop()
            return

        # --- LiDAR safety ---
        ranges = np.array(self._latest_scan.ranges, dtype=np.float32)
        angles = np.linspace(
            self._latest_scan.angle_min, self._latest_scan.angle_max, len(ranges)
        )
        front_mask = (angles > -0.4) & (angles < 0.4)
        front_ranges = ranges[front_mask]
        if len(front_ranges) > 0 and np.min(front_ranges) < self._min_safety_dist:
            self.get_logger().warn(
                f"SAFETY STOP: obstacle at {np.min(front_ranges):.2f}m "
                f"< {self._min_safety_dist}m",
                throttle_duration_sec=1.0,
            )
            self._publish_stop()
            return

        # --- Inference ---
        try:
            resp = self._client.infer(rgb_np, depth_np, (goal_dist, goal_angle))
        except ConnectionError as e:
            self.get_logger().error(f"Inference server error: {e}")
            self._client_connected = False
            self._client.close()
            self._publish_stop()
            return

        if resp.get("error"):
            self.get_logger().error(f"Inference error: {resp['error']}")
            self._publish_stop()
            return

        action = resp["action"]
        lat_ms = resp.get("latency_ms", 0)
        self._latencies_ms.append(lat_ms)

        # --- Action → cmd_vel ---
        if self._step_mode:
            self._step_ctrl.start(action, self._robot_pose)
            twist, _ = self._step_ctrl.update(self._robot_pose)
        else:
            twist = Twist()
            if action == FORWARD:
                twist.linear.x = FORWARD_SPEED
            elif action == TURN_LEFT:
                twist.angular.z = TURN_SPEED
            elif action == TURN_RIGHT:
                twist.angular.z = -TURN_SPEED

        self._step_count += 1

        if not self._dry_run:
            self._cmd_pub.publish(twist)

        # --- Periodic status ---
        if self._step_count % 20 == 0:
            avg_lat = (
                sum(self._latencies_ms[-20:]) / min(len(self._latencies_ms), 20)
                if self._latencies_ms
                else 0
            )
            yaw_deg = math.degrees(self._robot_pose[2]) % 360
            goal_angle_deg = math.degrees(goal_angle)
            self.get_logger().info(
                f"Step {self._step_count}: "
                f"pose=({self._robot_pose[0]:.1f},{self._robot_pose[1]:.1f},yaw={yaw_deg:.0f}°) "
                f"goal=({self._goal[0]:.1f},{self._goal[1]:.1f}) "
                f"dist={goal_dist:.1f}m angle_to_goal={goal_angle_deg:.0f}°  "
                f"action={ACTION_NAMES[action]}  "
                f"lat={lat_ms:.0f}ms avg={avg_lat:.0f}ms"
            )

    def _publish_stop(self):
        if not self._dry_run:
            self._cmd_pub.publish(Twist())


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="PointNav PPO Gazebo Node")
    parser.add_argument("--port", type=int, default=9876, help="Inference server port")
    parser.add_argument(
        "--step", action="store_true", default=True,
        help="Step-based action mode (default: True, matches Habitat)"
    )
    parser.add_argument(
        "--continuous", action="store_true",
        help="Continuous action mode (overrides --step)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Do not publish cmd_vel (observe only)"
    )
    parser.add_argument(
        "--max-steps", type=int, default=500, help="Episode timeout (steps)"
    )
    parser.add_argument(
        "--success-distance", type=float, default=0.2,
        help="Success threshold in metres"
    )
    parser.add_argument(
        "--min-safety-dist", type=float, default=0.25,
        help="LiDAR safety stop distance (m)"
    )
    parser.add_argument(
        "--control-rate", type=float, default=10.0,
        help="Control loop frequency (Hz)"
    )
    args = parser.parse_args()

    if args.continuous:
        args.step = False

    rclpy.init()
    node = PointNavGazeboNode(args)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
