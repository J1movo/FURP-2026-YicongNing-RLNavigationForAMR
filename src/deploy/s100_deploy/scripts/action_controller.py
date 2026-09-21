"""
Discrete action → cmd_vel (geometry_msgs/Twist) conversion.

The PointNav PPO policy outputs one of 4 discrete actions per step:
    0: STOP
    1: MOVE_FORWARD  (0.25m per step in simulation)
    2: TURN_LEFT     (10° per step in simulation)
    3: TURN_RIGHT    (10° per step in simulation)

Two execution modes are provided:

    "continuous" (default): Each action maps to a fixed velocity. Inference
        runs at a fixed rate and the robot moves continuously. Smooth but
        the per-step distance does not match training exactly.

    "step": Each action is executed as a fixed displacement (0.25m or 10°),
        then the robot stops and waits for the next inference. Closer to
        Habitat's step semantics but the robot moves in a stop-start pattern.

All speeds are configurable.
"""

import math
from geometry_msgs.msg import Twist


# ---------------------------------------------------------------------------
# Action table
# ---------------------------------------------------------------------------

STOP = 0
FORWARD = 1
TURN_LEFT = 2
TURN_RIGHT = 3

ACTION_NAMES = {0: "STOP", 1: "FORWARD", 2: "TURN_LEFT", 3: "TURN_RIGHT"}


# ---------------------------------------------------------------------------
# Continuous mode
# ---------------------------------------------------------------------------

class ContinuousActionController:
    """
    Map each discrete action directly to a fixed velocity command.

    Inference runs at a fixed rate (e.g. 10 Hz).  The model's closed-loop
    nature means it will chain actions — e.g. multiple consecutive FORWARD
    actions to travel a longer distance.
    """

    def __init__(self, forward_speed: float = 0.25, turn_speed: float = 0.5):
        self.forward_speed = forward_speed
        self.turn_speed = turn_speed

    def action_to_twist(self, action: int) -> Twist:
        twist = Twist()
        if action == FORWARD:
            twist.linear.x = self.forward_speed
        elif action == TURN_LEFT:
            twist.angular.z = self.turn_speed
        elif action == TURN_RIGHT:
            twist.angular.z = -self.turn_speed
        # STOP or unknown: all zeros
        return twist


# ---------------------------------------------------------------------------
# Step mode — closer to Habitat's discrete-step semantics
# ---------------------------------------------------------------------------

def _normalize_angle(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


class StepActionController:
    """
    Execute each discrete action as a fixed-distance/fixed-angle step.

    After starting an action, the controller tracks odometry displacement
    until the step is complete.  The robot stops between steps to let the
    model take a fresh observation — matching Habitat's step→observe→step
    evaluation loop more closely.

    Usage:
        # Called every control tick:
        if controller.is_done:
            action = model_infer()
            controller.start_action(action, current_pose)
        twist, done = controller.update(current_pose)
        publish(twist)
        if done:
            # next tick will trigger a new inference
            ...
    """

    def __init__(self, forward_step: float = 0.25, turn_angle_deg: float = 10.0,
                 forward_speed: float = 0.2, turn_speed: float = 0.5):
        self.forward_step = forward_step
        self.turn_angle = math.radians(turn_angle_deg)
        self.forward_speed = forward_speed
        self.turn_speed = turn_speed

        self._active = False
        self._action = None
        self._start_pose = None
        self._last_sign = 0

    @property
    def is_done(self) -> bool:
        return not self._active

    def start_action(self, action: int, pose: tuple):
        """
        Begin executing a discrete action.

        Args:
            action: 0-3 discrete action index.
            pose: (x, y, yaw) current robot pose.
        """
        self._action = action
        self._start_pose = pose
        self._active = (action != STOP)

        # Determine turn direction sign
        if action == TURN_LEFT:
            self._last_sign = 1
        elif action == TURN_RIGHT:
            self._last_sign = -1

    def update(self, pose: tuple):
        """
        Check progress and return the velocity command.

        Returns:
            (Twist, done) — done=True when the step is complete.
        """
        twist = Twist()

        if not self._active:
            return twist, True

        if self._action == FORWARD:
            dx = pose[0] - self._start_pose[0]
            dy = pose[1] - self._start_pose[1]
            dist = math.hypot(dx, dy)
            if dist >= self.forward_step:
                self._active = False
                return twist, True
            twist.linear.x = self.forward_speed

        elif self._action in (TURN_LEFT, TURN_RIGHT):
            dyaw = abs(_normalize_angle(pose[2] - self._start_pose[2]))
            if dyaw >= self.turn_angle:
                self._active = False
                return twist, True
            twist.angular.z = self._last_sign * self.turn_speed

        return twist, False
