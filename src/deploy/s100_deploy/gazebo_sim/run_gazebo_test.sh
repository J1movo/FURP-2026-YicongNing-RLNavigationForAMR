#!/bin/bash
# ============================================================================
# Run Gazebo simulation + PointNav PPO inference
# ============================================================================
#
# Usage:
#   ./run_gazebo_test.sh [MODEL] [OPTIONS]
#
#   MODEL:  latest | optimized  (default: latest)
#   OPTIONS:
#     --no-gui       Headless (gzserver only, no Gazebo window)
#     --dry-run      Don't publish cmd_vel, observe only
#     --step         Step-based action mode (default)
#     --continuous   Continuous action mode
#     --world WORLD  Gazebo world: empty | turtlebot3_world (default)
#     --goal X Y     Auto-send goal after startup
#
# Examples:
#   ./run_gazebo_test.sh latest
#   ./run_gazebo_test.sh optimized --no-gui
#   ./run_gazebo_test.sh latest --goal 2.0 0.0
#   ./run_gazebo_test.sh optimized --continuous --dry-run
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FURP_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ------------------------------------------------------------------
# Parse arguments
# ------------------------------------------------------------------

MODEL="latest"
GUI="true"
DRY_RUN=""
MODE_ARG="--step"
WORLD="turtlebot3_world"
GOAL_X=""
GOAL_Y=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        latest|optimized)
            MODEL="$1"
            ;;
        --no-gui)
            GUI="false"
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            ;;
        --step)
            MODE_ARG="--step"
            ;;
        --continuous)
            MODE_ARG="--continuous"
            ;;
        --world)
            WORLD="$2"
            shift
            ;;
        --goal)
            GOAL_X="$2"
            GOAL_Y="$3"
            shift 2
            ;;
        *)
            EXTRA_ARGS+=("$1")
            ;;
    esac
    shift
done

# Resolve model path
if [ "$MODEL" = "optimized" ]; then
    CKPT_PATH="$FURP_DIR/真机部署/latest_optimized.pth"
    MODEL_LABEL="latest_optimized"
else
    CKPT_PATH="$FURP_DIR/真机部署/latest.pth"
    MODEL_LABEL="latest"
fi

if [ ! -f "$CKPT_PATH" ]; then
    echo "ERROR: Checkpoint not found: $CKPT_PATH"
    exit 1
fi

# ------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------

export TURTLEBOT3_MODEL=burger

# Gazebo model paths
export GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:+$GAZEBO_MODEL_PATH:}/opt/ros/humble/share/turtlebot3_gazebo/models"
export GAZEBO_MODEL_PATH="$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models"

# ROS 2
source /opt/ros/humble/setup.bash 2>/dev/null || true

# ------------------------------------------------------------------
# Cleanup function
# ------------------------------------------------------------------

cleanup() {
    echo ""
    echo "=== Shutting down ==="
    # Kill inference server
    if [ -n "$SERVER_PID" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    # Kill Gazebo
    if [ -n "$GZSERVER_PID" ]; then
        kill "$GZSERVER_PID" 2>/dev/null || true
    fi
    if [ -n "$GZCLIENT_PID" ]; then
        kill "$GZCLIENT_PID" 2>/dev/null || true
    fi
    # Kill goal publisher
    if [ -n "$GOAL_PID" ]; then
        kill "$GOAL_PID" 2>/dev/null || true
    fi
    # Kill any remaining gazebo processes
    pkill -f "gzserver\|gzclient" 2>/dev/null || true
    echo "All processes stopped."
}
trap cleanup EXIT INT TERM

# ------------------------------------------------------------------
# 1. Start inference server (conda habitat env)
# ------------------------------------------------------------------

echo "=== Starting inference server ($MODEL_LABEL) ==="
echo "Checkpoint: $CKPT_PATH"

conda run -n habitat --no-capture-output \
    python3 "$SCRIPT_DIR/inference_server.py" \
    --ckpt "$CKPT_PATH" \
    --port 9876 \
    --device cuda &
SERVER_PID=$!

# Wait for server to be ready
echo "Waiting for inference server..."
for i in $(seq 1 30); do
    if python3 -c "
import socket, json
try:
    s = socket.create_connection(('127.0.0.1', 9876), timeout=1)
    s.sendall(json.dumps({'reset': True}).encode() + b'\n')
    f = s.makefile('r')
    resp = json.loads(f.readline())
    s.close()
    sys.exit(0 if resp.get('reset_ack') else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        echo "Inference server ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "ERROR: Inference server did not start in time"
        exit 1
    fi
done

# ------------------------------------------------------------------
# 2. Start Gazebo
# ------------------------------------------------------------------

echo "=== Starting Gazebo ($WORLD) ==="
WORLD_FILE="/opt/ros/humble/share/turtlebot3_gazebo/worlds/${WORLD}.world"

if [ "$GUI" = "true" ]; then
    echo "Launching Gazebo with GUI..."
    ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py \
        world:="$WORLD_FILE" &
    GAZEBO_PID=$!
else
    echo "Launching Gazebo headless..."
    ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py \
        world:="$WORLD_FILE" \
        gui:=false &
    GAZEBO_PID=$!
fi

# Wait for Gazebo + TB3 to be ready
echo "Waiting for Gazebo and TurtleBot3..."
sleep 8

# Verify TB3 is spawned
for i in $(seq 1 20); do
    if ros2 topic list 2>/dev/null | grep -q "/odom"; then
        echo "TurtleBot3 detected!"
        break
    fi
    sleep 2
    if [ $i -eq 20 ]; then
        echo "WARNING: /odom topic not found. Gazebo may still be loading."
    fi
done

# ------------------------------------------------------------------
# 3. Run PPO navigation node
# ------------------------------------------------------------------

echo "=== Starting PPO navigation node ==="
echo "Model: $MODEL_LABEL  Mode: ${MODE_ARG#--}  Dry-run: ${DRY_RUN:-false}"

# Optional: send goal after a delay
if [ -n "$GOAL_X" ] && [ -n "$GOAL_Y" ]; then
    (
        sleep 3
        echo "Sending goal: ($GOAL_X, $GOAL_Y)"
        ros2 topic pub --once /goal_pose geometry_msgs/PoseStamped \
            "{header: {frame_id: 'odom'}, pose: {position: {x: $GOAL_X, y: $GOAL_Y, z: 0.0}, orientation: {w: 1.0}}}"
    ) &
    GOAL_PID=$!
fi

# Run the node (foreground — Ctrl-C to stop)
python3 "$SCRIPT_DIR/ppo_gazebo_node.py" \
    --port 9876 \
    $MODE_ARG \
    $DRY_RUN \
    "${EXTRA_ARGS[@]}"

echo "=== Test complete ==="
