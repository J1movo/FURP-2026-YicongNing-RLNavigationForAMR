#!/bin/bash
# Launch Gazebo + TB3 Waffle with depth camera (custom model)
# Usage: source spawn_tb3_depth.sh

export TURTLEBOT3_MODEL=waffle
export GAZEBO_MODEL_PATH="/home/jimovo/Desktop/FURP/真机部署/gazebo_sim/models:${GAZEBO_MODEL_PATH}"

source /opt/ros/humble/setup.bash

# Start Gazebo with turtlebot3_world
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py \
    gui:=true &
GZ_PID=$!

# Wait for Gazebo
sleep 5

# Kill the default spawned turtlebot (we'll spawn our own)
ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity "{name: 'waffle'}" 2>/dev/null || true

# Spawn our custom Waffle with depth camera
ros2 run gazebo_ros spawn_entity.py \
    -entity waffle_depth \
    -file /home/jimovo/Desktop/FURP/真机部署/gazebo_sim/models/turtlebot3_waffle_depth/model.sdf \
    -x -2.0 -y -0.5 -z 0.01

echo "TB3 Waffle with depth camera spawned!"
echo "Gazebo PID: $GZ_PID"
wait $GZ_PID
