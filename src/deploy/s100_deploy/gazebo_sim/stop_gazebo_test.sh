#!/bin/bash
# ============================================================================
# Stop all Gazebo test processes
# ============================================================================

echo "Stopping Gazebo test processes..."

# Inference server
pkill -f "inference_server.py" 2>/dev/null && echo "  inference_server: stopped" || echo "  inference_server: not running"

# ROS 2 node
pkill -f "ppo_gazebo_node.py" 2>/dev/null && echo "  ppo_gazebo_node: stopped" || echo "  ppo_gazebo_node: not running"

# Gazebo
pkill -f "gzserver" 2>/dev/null && echo "  gzserver: stopped" || echo "  gzserver: not running"
pkill -f "gzclient" 2>/dev/null && echo "  gzclient: stopped" || echo "  gzclient: not running"

# ROS 2 daemon
pkill -f "ros2 daemon" 2>/dev/null && echo "  ros2 daemon: stopped" || echo "  ros2 daemon: not running"

echo "Done."
