wheeltec@wheeltec:~/Desktop$ rosversion -d
noetic

wheeltec@wheeltec:~/Desktop$ python3 --version
Python 3.8.10

wheeltec@wheeltec:~/Desktop$  python3 -c "import torch; print('torch', torch.__version__)"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'torch'

wheeltec@wheeltec:~/Desktop$ python3 -c "import cv2; print('cv2', cv2.__version__)"
cv2 3.4.5

wheeltec@wheeltec:~/Desktop$ python3 -c "import numpy; print('numpy', numpy.__version__)"
numpy 1.17.4

wheeltec@wheeltec:~/Desktop$ uname -m
aarch64

wheeltec@wheeltec:~/Desktop$ roslaunch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch
... logging to /home/wheeltec/.ros/log/e4fbbec6-1de1-11b2-8ba6-d0abd5132608/roslaunch-wheeltec-6450.log
Checking log directory for disk usage. This may take a while.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://192.168.0.100:34719/

SUMMARY
========

PARAMETERS
 * /robot_BatteryCapacity: 6100
 * /robot_description: <?xml version="1....
 * /robot_pose_ekf/base_footprint_frame: base_footprint
 * /robot_pose_ekf/freq: 30.0
 * /robot_pose_ekf/imu_used: True
 * /robot_pose_ekf/odom_used: True
 * /robot_pose_ekf/output_frame: odom_combined
 * /robot_pose_ekf/sensor_timeout: 2.0
 * /robot_pose_ekf/vo_used: False
 * /rosdistro: noetic
 * /rosversion: 1.17.0
 * /wheeltec_robot/car_mode: brushless_senior_...
 * /wheeltec_robot/gyro_frame_id: gyro_link
 * /wheeltec_robot/odom_frame_id: odom_combined
 * /wheeltec_robot/odom_x_scale: 1.0
 * /wheeltec_robot/odom_y_scale: 1.0
 * /wheeltec_robot/odom_z_scale_negative: 1.0
 * /wheeltec_robot/odom_z_scale_positive: 1.0
 * /wheeltec_robot/robot_frame_id: base_footprint
 * /wheeltec_robot/serial_baud_rate: 115200
 * /wheeltec_robot/usart_port_name: /dev/wheeltec_con...

NODES
  /
    base_to_camera (tf/static_transform_publisher)
    base_to_gyro (tf/static_transform_publisher)
    base_to_laser (tf/static_transform_publisher)
    base_to_link (tf/static_transform_publisher)
    joint_state_publisher (joint_state_publisher/joint_state_publisher)
    robot_pose_ekf (robot_pose_ekf/robot_pose_ekf)
    robot_state_publisher (robot_state_publisher/robot_state_publisher)
    wheeltec_robot (turn_on_wheeltec_robot/wheeltec_robot_node)

auto-starting new master
process[master]: started with pid [6468]
ROS_MASTER_URI=http://192.168.0.100:11311

setting /run_id to e4fbbec6-1de1-11b2-8ba6-d0abd5132608
process[rosout-1]: started with pid [6488]
started core service [/rosout]
process[wheeltec_robot-2]: started with pid [6494]
process[base_to_link-3]: started with pid [6496]
process[base_to_laser-4]: started with pid [6497]
process[base_to_camera-5]: started with pid [6498]
process[base_to_gyro-6]: started with pid [6507]
process[joint_state_publisher-7]: started with pid [6514]
process[robot_state_publisher-8]: started with pid [6516]
[ INFO] [6796.327530144]: Data ready
[ INFO] [6796.346115680]: wheeltec_robot serial port opened
process[robot_pose_ekf-9]: started with pid [6523]
[ WARN] [6796.419017952]: The root link base_link has an inertia specified in the URDF, but KDL does not support a root link with an inertia.  As a workaround, you can add an extra dummy link to your URDF.
[ INFO] [6796.450162304]: output frame: odom_combined
[ INFO] [6796.453698912]: base frame: base_footprint
[ INFO] [6796.691938144]: Initializing Odom sensor
[ INFO] [6797.194212672]: Odom sensor activated
[ INFO] [6797.696583072]: Initializing Imu sensor
[ INFO] [6797.697037024]: Kalman filter initialized with odom measurement
[ INFO] [6797.697479168]: Imu sensor activated

wheeltec@wheeltec:~$ rostopic list
/PowerVoltage
/cmd_vel
/imu
/joint_states
/odom
/red_vel
/robot_charging_current
/robot_charging_flag
/robot_pose_ekf/odom_combined
/robot_recharge_flag
/robot_red_flag
/rosout
/rosout_agg
/tf
/tf_static

wheeltec@wheeltec:~$ rostopic info /cmd_vel

Type: geometry_msgs/Twist

Publishers: None

Subscribers: 
 * /wheeltec_robot (http://192.168.0.100:46553/)

wheeltec@wheeltec:~$ rostopic info /odom

Type: nav_msgs/Odometry

Publishers: 
 * /wheeltec_robot (http://192.168.0.100:46553/)

Subscribers: 
 * /robot_pose_ekf (http://192.168.0.100:34559/)

wheeltec@wheeltec:~$ rostopic echo /tf_static -n 10
transforms: 
  - 
    header: 
      seq: 0
      stamp: 
        secs: 6796
        nsecs: 459492192
      frame_id: "base_link"
    child_frame_id: "camera_link"
    transform: 
      translation: 
        x: 0.190243733941222
        y: -0.000234999999999987
        z: 0.220221921922286
      rotation: 
        x: 0.0
        y: 0.0
        z: 0.0
        w: 1.0
  - 
    header: 
      seq: 0
      stamp: 
        secs: 6796
        nsecs: 459509344
      frame_id: "base_link"
    child_frame_id: "controller_link"
    transform: 
      translation: 
        x: 0.113281206629993
        y: 0.0622012251396801
        z: 0.125099999999996
      rotation: 
        x: 0.0
        y: 0.0
        z: 0.0
        w: 1.0
  - 
    header: 
      seq: 0
      stamp: 
        secs: 6796
        nsecs: 459511328
      frame_id: "base_link"
    child_frame_id: "laser"
    transform: 
      translation: 
        x: 0.101154812773979
        y: 0.0
        z: 0.236182105663717
      rotation: 
        x: 0.0
        y: 0.0
        z: 1.0
        w: -1.6155445744325867e-15
---

wheeltec@wheeltec:~$ rosrun tf tf_echo base_link camera_link
At time 0.000
- Translation: [0.190, -0.000, 0.220]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7353.184
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7354.185
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7355.186
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7356.187
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7357.189
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7358.190
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7359.191
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7360.192
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7361.193
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7362.194
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7363.196
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7364.197
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7365.198
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7366.199
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7367.200
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7368.201
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7369.203
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7370.204
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7371.205
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7372.206
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7373.207
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7374.209
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
^CAt time 7375.210
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]

wheeltec@wheeltec:~$ rosrun tf tf_echo base_link camera_link 2>&1 | head -20
At time 0.000
- Translation: [0.190, -0.000, 0.220]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7406.946
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7407.947
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]
At time 7408.949
- Translation: [0.190, 0.000, 0.152]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
            in RPY (radian) [0.000, -0.000, 0.000]
            in RPY (degree) [0.000, -0.000, 0.000]

wheeltec@wheeltec:~$ rospack list | grep wheeltec
amcl /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/amcl
arm_demo /home/wheeltec/wheeltec_arm/src/arm_demo
aruco /home/wheeltec/wheeltec_robot/src/aruco_ros-noetic-devel/aruco
aruco_msgs /home/wheeltec/wheeltec_robot/src/aruco_ros-noetic-devel/aruco_msgs
aruco_ros /home/wheeltec/wheeltec_robot/src/aruco_ros-noetic-devel/aruco_ros
astra_camera /home/wheeltec/wheeltec_robot/src/ros_astra_camera-main
auto_recharge_ros /home/wheeltec/wheeltec_robot/src/auto_recharge_ros
base_local_planner /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/base_local_planner
bodyreader /home/wheeltec/wheeltec_robot/src/bodyreader
carrot_planner /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/carrot_planner
cartographer /home/wheeltec/cartographer_ws/install_isolated/share/cartographer
cartographer_ros /home/wheeltec/cartographer_ws/src/cartographer_ros/cartographer_ros
cartographer_ros_msgs /home/wheeltec/cartographer_ws/install_isolated/share/cartographer_ros_msgs
cartographer_rviz /home/wheeltec/cartographer_ws/install_isolated/share/cartographer_rviz
clear_costmap_recovery /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/clear_costmap_recovery
cloud_msgs /home/wheeltec/wheeltec_lidar/src/3D_SLAM/LeGO-LOAM-master/cloud_msgs
code_utils /home/wheeltec/wheeltec_lidar/src/3D_SLAM/code_utils-master
costmap_2d /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/costmap_2d
cv_bridge /home/wheeltec/wheeltec_robot/src/vision_opencv-noetic/cv_bridge
darknet_ros /home/wheeltec/wheeltec_robot/src/darknet_ros/darknet_ros
darknet_ros_msgs /home/wheeltec/wheeltec_robot/src/darknet_ros/darknet_ros_msgs
depthimage_to_laserscan /home/wheeltec/wheeltec_robot/src/depthimage_to_laserscan-melodic-devel
dwa_local_planner /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/dwa_local_planner
fake_localization /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/fake_localization
fdilink_ahrs /home/wheeltec/wheeltec_robot/src/fdilink_ahrs
global_planner /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/global_planner
gmapping /home/wheeltec/wheeltec_lidar/src/slam_gmapping/gmapping
hipnuc_imu /home/wheeltec/wheeltec_robot/src/hipnuc_imu
image_geometry /home/wheeltec/wheeltec_robot/src/vision_opencv-noetic/image_geometry
imu_tf_broadcaster /home/wheeltec/wheeltec_robot/src/imu_tf_broadcaster
imu_utils /home/wheeltec/wheeltec_lidar/src/3D_SLAM/imu_utils-master
ipa_building_msgs /home/wheeltec/wheeltec_robot/src/ipa_exploration/ipa_building_msgs
ipa_building_navigation /home/wheeltec/wheeltec_robot/src/ipa_exploration/ipa_building_navigation
ipa_room_exploration /home/wheeltec/wheeltec_robot/src/ipa_exploration/ipa_room_exploration
ira_laser_tools /home/wheeltec/wheeltec_robot/src/ira_laser_tools-ros1-master
kcf_track /home/wheeltec/wheeltec_robot/src/kcf_track
laserscan_merger /home/wheeltec/wheeltec_robot/src/laserscan_merger-master
ldlidar /home/wheeltec/wheeltec_robot/src/ldlidar_stl06n_ros1/ldlidar
ldlidar_14 /home/wheeltec/wheeltec_robot/src/ldlidar_14
lego_loam /home/wheeltec/wheeltec_lidar/src/3D_SLAM/LeGO-LOAM-master/LeGO-LOAM
lio_sam /home/wheeltec/wheeltec_lidar/src/3D_SLAM/LIO-SAM-master
lslidar_cx_driver /home/wheeltec/wheeltec_lidar/src/lslidar_cx_driver
lslidar_driver /home/wheeltec/wheeltec_robot/src/lsx10/lslidar_driver
lslidar_msgs /home/wheeltec/wheeltec_robot/src/lsx10/lslidar_msgs
map_server /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/map_server
mini_4wd_four_arm /home/wheeltec/wheeltec_arm/src/mini_4wd_four_arm
mini_4wd_four_arm_moveit_config /home/wheeltec/wheeltec_arm/src/mini_4wd_four_arm_moveit_config
mini_4wd_six_arm /home/wheeltec/wheeltec_arm/src/mini_4wd_six_arm
mini_4wd_six_arm_moveit_config /home/wheeltec/wheeltec_arm/src/mini_4wd_six_arm_moveit_config
mini_mec_four_arm /home/wheeltec/wheeltec_arm/src/mini_mec_four_arm
mini_mec_four_arm_moveit_config /home/wheeltec/wheeltec_arm/src/mini_mec_four_arm_moveit_config
mini_mec_six_arm /home/wheeltec/wheeltec_arm/src/mini_mec_six_arm
mini_mec_six_arm_moveit_config /home/wheeltec/wheeltec_arm/src/mini_mec_six_arm_moveit_config
mini_tank_four_arm /home/wheeltec/wheeltec_arm/src/mini_tank_four_arm
mini_tank_four_arm_moveit_config /home/wheeltec/wheeltec_arm/src/mini_tank_four_arm_moveit_config
move_base /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/move_base
move_slow_and_clear /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/move_slow_and_clear
nav_core /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/nav_core
navfn /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/navfn
nmea_msgs /home/wheeltec/wheeltec_robot/src/wheeltec_gps/nmea_msgs-master
ollama_chat_ros /home/wheeltec/wheeltec_robot/src/ollama_chat_ros
open_karto /home/wheeltec/wheeltec_robot/src/slam_karto/open_karto-melodic-devel
opencv_tests /home/wheeltec/wheeltec_robot/src/vision_opencv-noetic/opencv_tests
openslam_gmapping /home/wheeltec/wheeltec_lidar/src/openslam_gmapping
orb_slam2_ros /home/wheeltec/wheeltec_robot/src/orb_slam_2_ros-master
pointcloud_to_laserscan /home/wheeltec/wheeltec_lidar/src/pointcloud_to_laserscan
qt_ros_test /home/wheeltec/wheeltec_robot/src/qt_ros_test
ros_tensorflow /home/wheeltec/wheeltec_robot/src/ros_tensorflow
rotate_recovery /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/rotate_recovery
rplidar_ros /home/wheeltec/wheeltec_robot/src/rplidar_ros
rrt_exploration /home/wheeltec/wheeltec_robot/src/rrt_exploration
sh_manager /home/wheeltec/wheeltec_robot/src/sh_manager
simple_follower /home/wheeltec/wheeltec_robot/src/simple_follower
slam_karto /home/wheeltec/wheeltec_robot/src/slam_karto/slam_karto-melodic-devel
sparse_bundle_adjustment /home/wheeltec/wheeltec_robot/src/slam_karto/sparse_bundle_adjustment-melodic-devel
teb_local_planner /home/wheeltec/wheeltec_robot/src/teb_local_planner-noetic-devel
turn_on_wheeltec_robot /home/wheeltec/wheeltec_robot/src/turn_on_wheeltec_robot
ublox_gps /home/wheeltec/wheeltec_robot/src/wheeltec_gps/ublox-master/ublox_gps
ublox_msg_filters /home/wheeltec/wheeltec_robot/src/wheeltec_gps/ublox-master/ublox_msg_filters
ublox_msgs /home/wheeltec/wheeltec_robot/src/wheeltec_gps/ublox-master/ublox_msgs
ublox_serialization /home/wheeltec/wheeltec_robot/src/wheeltec_gps/ublox-master/ublox_serialization
usb_cam /home/wheeltec/wheeltec_robot/src/usb_cam
voxel_grid /home/wheeltec/wheeltec_robot/src/navigation-noetic-devel/voxel_grid
web_video_server /home/wheeltec/wheeltec_robot/src/web_video_server
wheeltec_aiui_ros /home/wheeltec/wheeltec_robot/src/wheeltec_aiui_ros
wheeltec_arm_pick /home/wheeltec/wheeltec_arm/src/wheeltec_arm_pick
wheeltec_arm_rc /home/wheeltec/wheeltec_arm/src/wheeltec_arm_rc
wheeltec_gps_driver /home/wheeltec/wheeltec_robot/src/wheeltec_gps/wheeltec_gps_driver
wheeltec_joy /home/wheeltec/wheeltec_robot/src/wheeltec_joy_control
wheeltec_multi /home/wheeltec/wheeltec_robot/src/wheeltec_multi
wheeltec_robot_rc /home/wheeltec/wheeltec_robot/src/wheeltec_robot_rc
wheeltec_tracker_pkg /home/wheeltec/wheeltec_arm/src/wheeltec_tracker_pkg
wheeltec_yolo_action /home/wheeltec/wheeltec_robot/src/wheeltec_yolo_action
world_canvas_msgs /home/wheeltec/wheeltec_robot/src/world_canvas_msgs
xf_mic_asr_offline_circle /home/wheeltec/wheeltec_robot/src/xf_mic_asr_offline_circle
yesense_imu /home/wheeltec/wheeltec_robot/src/yesense_imu

wheeltec@wheeltec:~$ find /opt/ros -name "*.launch" 2>/dev/null | grep -i nav
/opt/ros/noetic/share/rtabmap_demos/launch/demo_turtlebot3_navigation.launch
/opt/ros/noetic/share/rtabmap_demos/launch/demo_isaac_carter_navigation.launch
/opt/ros/noetic/share/nmea_navsat_driver/launch/nmea_serial_driver.launch
/opt/ros/noetic/share/husky_navigation/launch/gmapping.launch
/opt/ros/noetic/share/husky_navigation/launch/amcl.launch
/opt/ros/noetic/share/husky_navigation/launch/move_base_mapless_demo.launch
/opt/ros/noetic/share/husky_navigation/launch/gmapping_demo.launch
/opt/ros/noetic/share/husky_navigation/launch/move_base.launch
/opt/ros/noetic/share/husky_navigation/launch/amcl_demo.launch
/opt/ros/noetic/share/husky_navigation/launch/exploration.launch
/opt/ros/noetic/share/husky_navigation/launch/exploration_demo.launch
/opt/ros/noetic/share/turtlebot3_navigation/launch/turtlebot3_navigation.launch
/opt/ros/noetic/share/turtlebot3_navigation/launch/amcl.launch
/opt/ros/noetic/share/turtlebot3_navigation/launch/move_base.launch
/opt/ros/noetic/share/robot_localization/launch/dual_ekf_navsat_example.launch
/opt/ros/noetic/share/robot_localization/launch/navsat_transform_template.launch
/opt/ros/noetic/share/rtabmap_legacy/launch/azimut3/az3_mapping_robot_stereo_nav.launch
/opt/ros/noetic/share/rtabmap_legacy/launch/azimut3/az3_nav_kinect-only.launch
/opt/ros/noetic/share/rtabmap_legacy/launch/azimut3/az3_mapping_client_stereo_nav.launch
/opt/ros/noetic/share/rtabmap_legacy/launch/azimut3/az3_nav_client.launch
/opt/ros/noetic/share/rtabmap_legacy/launch/azimut3/az3_nav.launch
/opt/ros/noetic/share/rtabmap_legacy/launch/azimut3/az3_nav_kinect_odom.launch

wheeltec@wheeltec:~$ roslaunch astra_camera astra_pro.launch
... logging to /home/wheeltec/.ros/log/e4fbbec6-1de1-11b2-8ba6-d0abd5132608/roslaunch-wheeltec-7392.log
Checking log directory for disk usage. This may take a while.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://192.168.0.100:40131/

SUMMARY
========

PARAMETERS
 * /camera/camera/camera_name: camera
 * /camera/camera/color_depth_synchronization: False
 * /camera/camera/color_format: RGB
 * /camera/camera/color_fps: 30
 * /camera/camera/color_height: 480
 * /camera/camera/color_info_uri: 
 * /camera/camera/color_roi_height: -1
 * /camera/camera/color_roi_width: -1
 * /camera/camera/color_roi_x: -1
 * /camera/camera/color_roi_y: -1
 * /camera/camera/color_width: 640
 * /camera/camera/connection_delay: 100
 * /camera/camera/depth_align: False
 * /camera/camera/depth_format: Y11
 * /camera/camera/depth_fps: 30
 * /camera/camera/depth_height: 480
 * /camera/camera/depth_roi_height: -1
 * /camera/camera/depth_roi_width: -1
 * /camera/camera/depth_roi_x: -1
 * /camera/camera/depth_roi_y: -1
 * /camera/camera/depth_scale: 1
 * /camera/camera/depth_width: 640
 * /camera/camera/device_num: 1
 * /camera/camera/enable_color: True
 * /camera/camera/enable_d2c_viewer: False
 * /camera/camera/enable_depth: True
 * /camera/camera/enable_ir: True
 * /camera/camera/enable_point_cloud: True
 * /camera/camera/enable_point_cloud_xyzrgb: False
 * /camera/camera/enable_publish_extrinsic: False
 * /camera/camera/flip_color: False
 * /camera/camera/flip_depth: False
 * /camera/camera/flip_ir: False
 * /camera/camera/ir_format: Y10
 * /camera/camera/ir_fps: 30
 * /camera/camera/ir_height: 480
 * /camera/camera/ir_info_uri: 
 * /camera/camera/ir_width: 640
 * /camera/camera/oni_log_level: verbose
 * /camera/camera/oni_log_to_console: False
 * /camera/camera/oni_log_to_file: False
 * /camera/camera/product_id: 0
 * /camera/camera/publish_tf: True
 * /camera/camera/serial_number: 
 * /camera/camera/tf_publish_rate: 10.0
 * /camera/camera/use_uvc_camera: True
 * /camera/camera/uvc_camera_format: mjpeg
 * /camera/camera/uvc_flip: False
 * /camera/camera/uvc_product_id: 0x0501
 * /camera/camera/uvc_retry_count: 100
 * /camera/camera/uvc_vendor_id: 0x2bc5
 * /camera/camera/vendor_id: 0
 * /rosdistro: noetic
 * /rosversion: 1.17.0

NODES
  /camera/
    camera (astra_camera/astra_camera_node)

ROS_MASTER_URI=http://192.168.0.100:11311

process[camera/camera-1]: started with pid [7417]
[ INFO] [7771.363351808]: Starting camera node...
[ INFO] [7771.374316448]: Creating camera node...
[ INFO] [7771.375603232]: OBCameraNodeFactory::OBCameraNodeFactory
[ INFO] [7771.375753376]: Initializing OBCameraNodeFactory...
[ INFO] [7771.406042368]: init Done
[ INFO] [7771.406121120]: Query device
[ INFO] [7771.406177376]: Creating camera node done...
[ INFO] [7771.406259584]: Found 1 devices
[ INFO] [7771.506479872]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [7771.506581632]: Trying to open device: 2bc5/0402@1/4
[ INFO] [7771.606782400]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [7772.406174688]: wait for device  to be connected
[ INFO] [7773.406063136]: wait for device  to be connected
[ INFO] [7774.406074880]: wait for device  to be connected
[ INFO] [7775.406060736]: wait for device  to be connected
[ INFO] [7776.406064320]: wait for device  to be connected
[ INFO] [7776.691351744]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [7776.691427456]: Device connected: Astra serial number: 17112810687
[ INFO] [7776.691473728]: Start device 
[ INFO] [7776.785968864]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [7776.786988128]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [7776.790006944]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [7776.790156512]: OBCameraNode::setupUVCCamera
[ WARN] [7776.790299776]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [7776.819005824]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [7776.819217472]: find uvc device failed, retry 100 times
[ INFO] [7777.323714624]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [7777.323848576]: Find device error No such device process will be exit
[ERROR] [7777.336456640]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [7777.336568544]: OBCameraNode::clean stop poll frame
[ INFO] [7777.336624352]: OBCameraNode::clean stop poll frame done
[ INFO] [7777.336664896]: OBCameraNode::clean stop tf
[ INFO] [7777.391332640]: OBCameraNode::clean stop tf done.
[ INFO] [7777.391823968]: OBCameraNode::clean stop streams done.
[ INFO] [7777.391886816]: OBCameraNode::clean close device
[ INFO] [7777.391917376]: OBCameraNode::clean close device done.
[ INFO] [7777.391937216]: OBCameraNode::clean stop streams done.
[ INFO] [7777.405984896]: wait for device  to be connected
[ERROR] [7777.422844416]: Start device  failed: std::exception
[ INFO] [7777.422916416]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [7777.422958272]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [7777.422991680]: Query device
[ INFO] [7777.523149856]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [7777.523297152]: Trying to open device: 2bc5/0402@1/4
[ INFO] [7777.623498176]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [7777.623630080]: Device connected: Astra serial number: 17112810687
[ INFO] [7777.623689792]: Start device 
[ INFO] [7777.709141472]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [7777.709508448]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [7777.712374976]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [7777.712492384]: OBCameraNode::setupUVCCamera
[ WARN] [7777.712599136]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [7777.742908768]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [7777.743065888]: find uvc device failed, retry 100 times
[ INFO] [7778.248454400]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [7778.248610560]: Find device error No such device process will be exit
[ERROR] [7778.259854592]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [7778.259953760]: OBCameraNode::clean stop poll frame
[ INFO] [7778.260033760]: OBCameraNode::clean stop poll frame done
[ INFO] [7778.260080032]: OBCameraNode::clean stop tf
[ INFO] [7778.313580288]: OBCameraNode::clean stop tf done.
[ INFO] [7778.314060320]: OBCameraNode::clean stop streams done.
[ INFO] [7778.314103136]: OBCameraNode::clean close device
[ INFO] [7778.314128384]: OBCameraNode::clean close device done.
[ INFO] [7778.314146176]: OBCameraNode::clean stop streams done.
[ERROR] [7778.358870624]: Start device  failed: std::exception
[ INFO] [7778.358957696]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [7778.358991200]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [7778.406046400]: wait for device  to be connected
[ INFO] [7778.559270528]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [7778.559393568]: Device connected: Astra serial number: 17112810687
[ INFO] [7778.559451072]: Start device 
[ INFO] [7778.647461920]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [7778.647599392]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [7778.650814112]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [7778.650941184]: OBCameraNode::setupUVCCamera
[ WARN] [7778.651171808]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [7778.682459744]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [7778.682615456]: find uvc device failed, retry 100 times
[ INFO] [7779.187872896]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [7779.188005440]: Find device error No such device process will be exit
[ERROR] [7779.202989920]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [7779.203101408]: OBCameraNode::clean stop poll frame
[ INFO] [7779.203151616]: OBCameraNode::clean stop poll frame done
[ INFO] [7779.203196000]: OBCameraNode::clean stop tf
[ INFO] [7779.252065600]: OBCameraNode::clean stop tf done.
[ INFO] [7779.252717632]: OBCameraNode::clean stop streams done.
[ INFO] [7779.252793696]: OBCameraNode::clean close device
[ INFO] [7779.252836832]: OBCameraNode::clean close device done.
[ INFO] [7779.252909312]: OBCameraNode::clean stop streams done.
[ERROR] [7779.295823936]: Start device  failed: std::exception
[ INFO] [7779.295915104]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [7779.295950272]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [7779.295985312]: Query device
[ INFO] [7779.396155712]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [7779.396271904]: Trying to open device: 2bc5/0402@1/4
[ INFO] [7779.406007872]: wait for device  to be connected
[ INFO] [7779.496531072]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [7779.496652896]: Device connected: Astra serial number: 17112810687
[ INFO] [7779.496707424]: Start device 
[ INFO] [7779.582142016]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [7779.582296448]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [7779.584971616]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [7779.585114464]: OBCameraNode::setupUVCCamera
[ WARN] [7779.585434912]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [7779.614077344]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [7779.614273120]: find uvc device failed, retry 100 times
[ INFO] [7780.119439424]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [7780.119574560]: Find device error No such device process will be exit
[ERROR] [7780.130721536]: Failed to initialize UVC camera: Find device error No such device process will be exit

wheeltec@wheeltec:~$ rostopic list | grep -iE 'camera|depth|rgb|astra|image'
/camera/color/camera_info
/camera/color/image_raw
/camera/depth/camera_info
/camera/depth/image_raw
/camera/ir/camera_info
/camera/ir/image_raw
/camera/rgb/camera_info
/camera/rgb/image_raw

wheeltec@wheeltec:~$ rostopic echo /camera/depth/camera_info -n 1
# No output

wheeltec@wheeltec:~$ roslaunch astra_camera astra_pro.launch enable_color:=false
... logging to /home/wheeltec/.ros/log/e4fbbec6-1de1-11b2-8ba6-d0abd5132608/roslaunch-wheeltec-9431.log
Checking log directory for disk usage. This may take a while.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://192.168.0.100:33087/

SUMMARY
========

PARAMETERS
 * /camera/camera/camera_name: camera
 * /camera/camera/color_depth_synchronization: False
 * /camera/camera/color_format: RGB
 * /camera/camera/color_fps: 30
 * /camera/camera/color_height: 480
 * /camera/camera/color_info_uri: 
 * /camera/camera/color_roi_height: -1
 * /camera/camera/color_roi_width: -1
 * /camera/camera/color_roi_x: -1
 * /camera/camera/color_roi_y: -1
 * /camera/camera/color_width: 640
 * /camera/camera/connection_delay: 100
 * /camera/camera/depth_align: False
 * /camera/camera/depth_format: Y11
 * /camera/camera/depth_fps: 30
 * /camera/camera/depth_height: 480
 * /camera/camera/depth_roi_height: -1
 * /camera/camera/depth_roi_width: -1
 * /camera/camera/depth_roi_x: -1
 * /camera/camera/depth_roi_y: -1
 * /camera/camera/depth_scale: 1
 * /camera/camera/depth_width: 640
 * /camera/camera/device_num: 1
 * /camera/camera/enable_color: False
 * /camera/camera/enable_d2c_viewer: False
 * /camera/camera/enable_depth: True
 * /camera/camera/enable_ir: True
 * /camera/camera/enable_point_cloud: True
 * /camera/camera/enable_point_cloud_xyzrgb: False
 * /camera/camera/enable_publish_extrinsic: False
 * /camera/camera/flip_color: False
 * /camera/camera/flip_depth: False
 * /camera/camera/flip_ir: False
 * /camera/camera/ir_format: Y10
 * /camera/camera/ir_fps: 30
 * /camera/camera/ir_height: 480
 * /camera/camera/ir_info_uri: 
 * /camera/camera/ir_width: 640
 * /camera/camera/oni_log_level: verbose
 * /camera/camera/oni_log_to_console: False
 * /camera/camera/oni_log_to_file: False
 * /camera/camera/product_id: 0
 * /camera/camera/publish_tf: True
 * /camera/camera/serial_number: 
 * /camera/camera/tf_publish_rate: 10.0
 * /camera/camera/use_uvc_camera: True
 * /camera/camera/uvc_camera_format: mjpeg
 * /camera/camera/uvc_flip: False
 * /camera/camera/uvc_product_id: 0x0501
 * /camera/camera/uvc_retry_count: 100
 * /camera/camera/uvc_vendor_id: 0x2bc5
 * /camera/camera/vendor_id: 0
 * /rosdistro: noetic
 * /rosversion: 1.17.0

NODES
  /camera/
    camera (astra_camera/astra_camera_node)

ROS_MASTER_URI=http://192.168.0.100:11311

process[camera/camera-1]: started with pid [9455]
[ INFO] [8580.002760000]: Starting camera node...
[ INFO] [8580.013913344]: Creating camera node...
[ INFO] [8580.015179808]: OBCameraNodeFactory::OBCameraNodeFactory
[ INFO] [8580.015226848]: Initializing OBCameraNodeFactory...
[ INFO] [8580.040846432]: init Done
[ INFO] [8580.040938784]: Query device
[ INFO] [8580.040999072]: Creating camera node done...
[ INFO] [8580.041036800]: Found 1 devices
[ INFO] [8580.141262112]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [8580.141344640]: Trying to open device: 2bc5/0402@1/4
[ INFO] [8580.241479424]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [8581.040681952]: wait for device  to be connected
[ INFO] [8582.040522048]: wait for device  to be connected
[ INFO] [8583.040556384]: wait for device  to be connected
[ INFO] [8584.040540320]: wait for device  to be connected
[ INFO] [8585.040541376]: wait for device  to be connected
[ INFO] [8585.325199168]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [8585.325314272]: Device connected: Astra serial number: 17112810687
[ INFO] [8585.325365280]: Start device 
[ INFO] [8585.423018624]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [8585.423481216]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [8585.426681504]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [8585.427076288]: OBCameraNode::setupUVCCamera
[ WARN] [8585.427179744]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [8585.459052448]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [8585.459269056]: find uvc device failed, retry 100 times
[ INFO] [8585.965368448]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [8585.965502592]: Find device error No such device process will be exit
[ERROR] [8585.979305376]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [8585.979408320]: OBCameraNode::clean stop poll frame
[ INFO] [8585.979459904]: OBCameraNode::clean stop poll frame done
[ INFO] [8585.979495488]: OBCameraNode::clean stop tf
[ INFO] [8586.028317952]: OBCameraNode::clean stop tf done.
[ INFO] [8586.028827872]: OBCameraNode::clean stop streams done.
[ INFO] [8586.028888800]: OBCameraNode::clean close device
[ INFO] [8586.028937088]: OBCameraNode::clean close device done.
[ INFO] [8586.028980000]: OBCameraNode::clean stop streams done.
[ INFO] [8586.040451488]: wait for device  to be connected
[ERROR] [8586.072485312]: Start device  failed: std::exception
[ INFO] [8586.072572864]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [8586.072613568]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [8586.072662240]: Query device
[ INFO] [8586.172827648]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [8586.172968320]: Trying to open device: 2bc5/0402@1/4
[ INFO] [8586.273127360]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [8586.273240480]: Device connected: Astra serial number: 17112810687
[ INFO] [8586.273289088]: Start device 
[ INFO] [8586.364124448]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [8586.364487424]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [8586.367611936]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [8586.367754048]: OBCameraNode::setupUVCCamera
[ WARN] [8586.367891616]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [8586.398639232]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [8586.398822176]: find uvc device failed, retry 100 times
[ INFO] [8586.904788544]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [8586.904916288]: Find device error No such device process will be exit
[ERROR] [8586.918490144]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [8586.918580576]: OBCameraNode::clean stop poll frame
[ INFO] [8586.918623072]: OBCameraNode::clean stop poll frame done
[ INFO] [8586.918662528]: OBCameraNode::clean stop tf
[ INFO] [8586.968690240]: OBCameraNode::clean stop tf done.
[ INFO] [8586.969183648]: OBCameraNode::clean stop streams done.
[ INFO] [8586.969249536]: OBCameraNode::clean close device
[ INFO] [8586.969289760]: OBCameraNode::clean close device done.
[ INFO] [8586.969325312]: OBCameraNode::clean stop streams done.
[ERROR] [8587.017847680]: Start device  failed: std::exception
[ INFO] [8587.017951200]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [8587.017994400]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [8587.040517920]: wait for device  to be connected
[ INFO] [8587.218291776]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [8587.218400192]: Device connected: Astra serial number: 17112810687
[ INFO] [8587.218449888]: Start device 
[ INFO] [8587.309609024]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [8587.309742528]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [8587.312528928]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [8587.312671008]: OBCameraNode::setupUVCCamera
[ WARN] [8587.312753440]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [8587.341358752]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [8587.341507104]: find uvc device failed, retry 100 times
[ INFO] [8587.847136512]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [8587.847264448]: Find device error No such device process will be exit
[ERROR] [8587.860653568]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [8587.860746848]: OBCameraNode::clean stop poll frame
[ INFO] [8587.860804192]: OBCameraNode::clean stop poll frame done
[ INFO] [8587.860838112]: OBCameraNode::clean stop tf
[ INFO] [8587.913692992]: OBCameraNode::clean stop tf done.
[ INFO] [8587.914237920]: OBCameraNode::clean stop streams done.
[ INFO] [8587.914281152]: OBCameraNode::clean close device
[ INFO] [8587.914302624]: OBCameraNode::clean close device done.
[ INFO] [8587.914326016]: OBCameraNode::clean stop streams done.
[ERROR] [8587.958404352]: Start device  failed: std::exception
[ INFO] [8587.958505408]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [8587.958542400]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [8587.958588832]: Query device
[ INFO] [8588.040518624]: wait for device  to be connected
[ INFO] [8588.058749472]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [8588.058859168]: Trying to open device: 2bc5/0402@1/4
[ INFO] [8588.159007872]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [8588.159110944]: Device connected: Astra serial number: 17112810687
[ INFO] [8588.159156512]: Start device 
[ INFO] [8588.251259520]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [8588.251399104]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [8588.254030496]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [8588.254169696]: OBCameraNode::setupUVCCamera
[ WARN] [8588.254273536]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [8588.283690048]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [8588.283857280]: find uvc device failed, retry 100 times
^C[camera/camera-1] killing on exit
shutting down processing monitor...
... shutting down processing monitor complete
done

wheeltec@wheeltec:~$ ls /home/wheeltec/wheeltec_robot/src/ros_astra_camera-main/launch/
astra.launch           dabai_pro.launch      multi_dabai_dcw2.launch
astra_pro.launch       dabai_u3.launch       multi_dabai_dcw.launch
astra_pro_plus.launch  deeyea.launch         multi_dabai.launch
dabai_dc1.launch       embedded_s.launch     multi_dabai_pro.launch
dabai_dcw2.launch      embedded_u3.launch    multi_deeyea.launch
dabai_dcw.launch       gemini_e.launch       multi_device.launch
dabai_dw2.launch       gemini_e_lite.launch  multi_gemini.launch
dabai_dw.launch        gemini.launch         stereo_s.launch
dabai.launch           gemini_uw.launch      stereo_s_u3.launch
dabai_max.launch       list_devices.launch
dabai_max_pro.launch   multi_astra.launch

wheeltec@wheeltec:~$ rostopic echo /camera/depth/camera_info -n 1
^Cwheeltec@wheeltec:~$ rostopic hz /camera/depth/image_raw
subscribed to [/camera/depth/image_raw]
no new messages
no new messages
no new messages
no new messages
no new messages
^Cno new messages

wheeltec@wheeltec:~$ lsusb | grep -i orbbec
wheeltec@wheeltec:~$ lsusb
Bus 002 Device 002: ID 0bda:0489 Realtek Semiconductor Corp. 4-Port USB 3.0 Hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 8087:0a2b Intel Corp. 
Bus 001 Device 006: ID 1a86:55d4 QinHeng Electronics 
Bus 001 Device 013: ID 1a86:55d4 QinHeng Electronics 
Bus 001 Device 012: ID 1a40:0101 Terminus Technology Inc. Hub
Bus 001 Device 009: ID 046d:c52b Logitech, Inc. Unifying Receiver
Bus 001 Device 008: ID 1a86:55d4 QinHeng Electronics 4-Port USB 2.0 Hub
Bus 001 Device 007: ID 0d8c:0012 C-Media Electronics, Inc. 
Bus 001 Device 005: ID 1a86:8095 QinHeng Electronics 4-Port USB 2.0 Hub
Bus 001 Device 004: ID 2bc5:0402  
Bus 001 Device 002: ID 0bda:5489 Realtek Semiconductor Corp. 4-Port USB 2.0 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

wheeltec@wheeltec:~$ ls /dev/video*
ls: cannot access '/dev/video*': No such file or directory

wheeltec@wheeltec:~$ ls /dev/video*
ls: cannot access '/dev/video*': No such file or directory
wheeltec@wheeltec:~$ ls /dev/
astra_s                capture-vi-channel8  stdout
autofs                 capture-vi-channel9  tee0
block                  ch343_iodev0         teepriv0
btrfs-control          ch343_iodev1         tegra_camera_ctrl
bus                    ch343_iodev2         tegra-crypto
camchar-dbg            char                 tegra-nvvse-crypto
camchar-echo           console              tegra-soc-hwpm
capture-isp-channel0   cpu_dma_latency      tty
capture-isp-channel1   cuse                 tty0
capture-isp-channel10  disk                 tty1
capture-isp-channel11  dma_heap             tty10
capture-isp-channel12  efi_capsule_loader   tty11
capture-isp-channel13  fd                   tty12
capture-isp-channel14  full                 tty13
capture-isp-channel15  fuse                 tty14
capture-isp-channel16  gpiochip0            tty15
capture-isp-channel17  gpiochip1            tty16
capture-isp-channel18  hidraw0              tty17
capture-isp-channel19  hidraw1              tty18
capture-isp-channel2   hidraw2              tty19
capture-isp-channel20  hugepages            tty2
capture-isp-channel21  i2c-0                tty20
capture-isp-channel22  i2c-1                tty21
capture-isp-channel23  i2c-10               tty22
capture-isp-channel24  i2c-11               tty23
capture-isp-channel25  i2c-2                tty24
capture-isp-channel26  i2c-3                tty25
capture-isp-channel27  i2c-4                tty26
capture-isp-channel28  i2c-5                tty27
capture-isp-channel29  i2c-6                tty28
capture-isp-channel3   i2c-7                tty29
capture-isp-channel30  i2c-8                tty3
capture-isp-channel31  i2c-9                tty30
capture-isp-channel32  initctl              tty31
capture-isp-channel33  input                tty32
capture-isp-channel34  kmsg                 tty33
capture-isp-channel35  kvm                  tty34
capture-isp-channel36  l3cache              tty35
capture-isp-channel37  log                  tty36
capture-isp-channel38  loop0                tty37
capture-isp-channel39  loop1                tty38
capture-isp-channel4   loop10               tty39
capture-isp-channel40  loop11               tty4
capture-isp-channel41  loop2                tty40
capture-isp-channel42  loop3                tty41
capture-isp-channel43  loop4                tty42
capture-isp-channel44  loop5                tty43
capture-isp-channel45  loop6                tty44
capture-isp-channel46  loop7                tty45
capture-isp-channel47  loop8                tty46
capture-isp-channel48  loop9                tty47
capture-isp-channel49  loop-control         tty48
capture-isp-channel5   mapper               tty49
capture-isp-channel50  media0               tty5
capture-isp-channel51  mem                  tty50
capture-isp-channel52  mqueue               tty51
capture-isp-channel53  net                  tty52
capture-isp-channel54  null                 tty53
capture-isp-channel55  nvgpu                tty54
capture-isp-channel56  nvhost-as-gpu        tty55
capture-isp-channel57  nvhost-ctrl          tty56
capture-isp-channel58  nvhost-ctrl-gpu      tty57
capture-isp-channel59  nvhost-ctrl-isp      tty58
capture-isp-channel6   nvhost-ctrl-nvdec    tty59
capture-isp-channel60  nvhost-ctxsw-gpu     tty6
capture-isp-channel61  nvhost-dbg-gpu       tty60
capture-isp-channel62  nvhost-gpu           tty61
capture-isp-channel63  nvhost-isp           tty62
capture-isp-channel7   nvhost-isp-thi       tty63
capture-isp-channel8   nvhost-nvcsi         tty7
capture-isp-channel9   nvhost-nvdec         tty8
capture-vi-channel0    nvhost-nvjpg         tty9
capture-vi-channel1    nvhost-nvjpg1        ttyAMA0
capture-vi-channel10   nvhost-nvsched-gpu   ttyCH343USB0
capture-vi-channel11   nvhost-ofa           ttyCH343USB1
capture-vi-channel12   nvhost-power-gpu     ttyCH343USB2
capture-vi-channel13   nvhost-prof-ctx-gpu  ttyGS0
capture-vi-channel14   nvhost-prof-dev-gpu  ttyp0
capture-vi-channel15   nvhost-prof-gpu      ttyp1
capture-vi-channel16   nvhost-sched-gpu     ttyp2
capture-vi-channel17   nvhost-tsec          ttyp3
capture-vi-channel18   nvhost-tsg-gpu       ttyp4
capture-vi-channel19   nvhost-vi0           ttyp5
capture-vi-channel2    nvhost-vi0-thi       ttyp6
capture-vi-channel20   nvhost-vi1           ttyp7
capture-vi-channel21   nvhost-vi1-thi       ttyp8
capture-vi-channel22   nvhost-vic           ttyp9
capture-vi-channel23   nvidia0              ttypa
capture-vi-channel24   nvidiactl            ttypb
capture-vi-channel25   nvidia-modeset       ttypc
capture-vi-channel26   nvmap                ttypd
capture-vi-channel27   nvme0                ttype
capture-vi-channel28   nvme0n1              ttypf
capture-vi-channel29   nvme0n1p1            ttyS0
capture-vi-channel3    nvme0n1p10           ttyS1
capture-vi-channel30   nvme0n1p11           ttyS2
capture-vi-channel31   nvme0n1p12           ttyS3
capture-vi-channel32   nvme0n1p13           ttyTCU0
capture-vi-channel33   nvme0n1p14           ttyTHS0
capture-vi-channel34   nvme0n1p15           ttyTHS3
capture-vi-channel35   nvme0n1p2            ttyTHS4
capture-vi-channel36   nvme0n1p3            uhid
capture-vi-channel37   nvme0n1p4            uinput
capture-vi-channel38   nvme0n1p5            urandom
capture-vi-channel39   nvme0n1p6            usb
capture-vi-channel4    nvme0n1p7            vcs
capture-vi-channel40   nvme0n1p8            vcs1
capture-vi-channel41   nvme0n1p9            vcs2
capture-vi-channel42   nvsciipc             vcs3
capture-vi-channel43   port                 vcs4
capture-vi-channel44   ppp                  vcs5
capture-vi-channel45   pps0                 vcs6
capture-vi-channel46   ptmx                 vcsa
capture-vi-channel47   pts                  vcsa1
capture-vi-channel48   ptyp0                vcsa2
capture-vi-channel49   ptyp1                vcsa3
capture-vi-channel5    ptyp2                vcsa4
capture-vi-channel50   ptyp3                vcsa5
capture-vi-channel51   ptyp4                vcsa6
capture-vi-channel52   ptyp5                vcsu
capture-vi-channel53   ptyp6                vcsu1
capture-vi-channel54   ptyp7                vcsu2
capture-vi-channel55   ptyp8                vcsu3
capture-vi-channel56   ptyp9                vcsu4
capture-vi-channel57   ptypa                vcsu5
capture-vi-channel58   ptypb                vcsu6
capture-vi-channel59   ptypc                vfio
capture-vi-channel6    ptypd                vhci
capture-vi-channel60   ptype                watchdog
capture-vi-channel61   ptypf                watchdog0
capture-vi-channel62   quadd                wheeltec_controller
capture-vi-channel63   quadd_auth           wheeltec_lidar
capture-vi-channel64   random               wheeltec_mic
capture-vi-channel65   rfkill               zero
capture-vi-channel66   rtc                  zram0
capture-vi-channel67   rtc0                 zram1
capture-vi-channel68   rtc1                 zram2
capture-vi-channel69   shm                  zram3
capture-vi-channel7    snd                  zram4
capture-vi-channel70   stderr               zram5
capture-vi-channel71   stdin

wheeltec@wheeltec:~$ lsmod | grep uvc
wheeltec@wheeltec:~$ lsmod
Module                  Size  Used by
fuse                  118784  3
xt_state               16384  0
ipt_REJECT             16384  2
nf_reject_ipv4         16384  1 ipt_REJECT
xt_tcpudp              16384  4
nf_nat_h323            20480  0
nf_conntrack_h323      53248  1 nf_nat_h323
nf_nat_pptp            16384  0
nf_conntrack_pptp      20480  1 nf_nat_pptp
nf_nat_tftp            16384  0
nf_conntrack_tftp      16384  1 nf_nat_tftp
nf_nat_sip             20480  0
nf_conntrack_sip       32768  1 nf_nat_sip
nf_nat_irc             16384  0
nf_conntrack_irc       16384  1 nf_nat_irc
nf_nat_ftp             16384  0
nf_conntrack_ftp       16384  1 nf_nat_ftp
nvidia_modeset       1093632  3
xt_conntrack           16384  2
xt_MASQUERADE          16384  2
nf_conntrack_netlink    45056  0
nfnetlink              20480  2 nf_conntrack_netlink
iptable_nat            16384  1
nf_nat                 45056  8 nf_nat_irc,nf_nat_ftp,nf_nat_tftp,nf_nat_pptp,nf_nat_h323,iptable_nat,xt_MASQUERADE,nf_nat_sip
nf_conntrack          122880  17 xt_conntrack,nf_nat_irc,nf_nat,nf_conntrack_tftp,nf_nat_ftp,xt_state,nf_conntrack_pptp,nf_nat_tftp,nf_conntrack_sip,nf_conntrack_h323,nf_nat_pptp,nf_conntrack_irc,nf_conntrack_netlink,nf_conntrack_ftp,nf_nat_h323,xt_MASQUERADE,nf_nat_sip
nf_defrag_ipv6         24576  1 nf_conntrack
nf_defrag_ipv4         16384  1 nf_conntrack
libcrc32c              16384  2 nf_conntrack,nf_nat
xt_addrtype            16384  2
iptable_filter         16384  1
br_netfilter           32768  0
lzo_rle                16384  36
lzo_compress           16384  1 lzo_rle
zram                   32768  6
overlay               114688  0
ramoops                28672  0
reed_solomon           20480  1 ramoops
bnep                   28672  2
hid_logitech_hidpp     45056  0
input_leds             16384  0
hid_logitech_dj        28672  0
cdc_acm                36864  0
snd_soc_tegra210_ope    32768  1
snd_soc_tegra186_dspk    20480  2
snd_soc_tegra210_iqc    16384  0
snd_soc_tegra210_mvc    20480  2
snd_soc_tegra186_asrc    36864  1
snd_soc_tegra186_arad    24576  2 snd_soc_tegra186_asrc
snd_soc_tegra210_afc    20480  6
snd_soc_tegra210_dmic    20480  4
snd_soc_tegra210_adx    28672  4
snd_soc_tegra210_amx    32768  4
snd_soc_tegra210_i2s    24576  6
snd_soc_tegra210_mixer    45056  1
snd_soc_tegra210_admaif   118784  1
snd_soc_tegra210_sfc    57344  4
snd_soc_tegra_pcm      16384  1 snd_soc_tegra210_admaif
iwlmvm                425984  0
mac80211              811008  1 iwlmvm
btusb                  57344  0
btrtl                  24576  1 btusb
btbcm                  24576  1 btusb
btintel                32768  1 btusb
aes_ce_blk             36864  1
binfmt_misc            24576  1
crypto_simd            24576  1 aes_ce_blk
cryptd                 24576  1 crypto_simd
aes_ce_cipher          20480  1 aes_ce_blk
ghash_ce               28672  0
sha2_ce                20480  0
sha256_arm64           28672  1 sha2_ce
sha1_ce                20480  0
snd_soc_tegra_machine_driver    16384  0
snd_soc_tegra_utils    28672  2 snd_soc_tegra210_admaif,snd_soc_tegra_machine_driver
snd_soc_simple_card_utils    24576  1 snd_soc_tegra_utils
snd_soc_spdif_tx       16384  0
snd_soc_tegra210_ahub  1257472  3 snd_soc_tegra210_ope,snd_soc_tegra210_sfc
tegra210_adma          28672  1 snd_soc_tegra210_admaif
userspace_alert        16384  0
tegra_bpmp_thermal     16384  0
snd_hda_codec_hdmi     57344  1
snd_hda_tegra          16384  0
snd_hda_codec         118784  2 snd_hda_codec_hdmi,snd_hda_tegra
snd_hda_core           81920  3 snd_hda_codec_hdmi,snd_hda_codec,snd_hda_tegra
iwlwifi               348160  1 iwlmvm
cfg80211              724992  3 iwlmvm,iwlwifi,mac80211
r8168                 507904  0
nv_imx219              20480  0
nvidia               1327104  7 nvidia_modeset
spi_tegra114           32768  0
loop                   36864  21
ina3221                24576  0
pwm_fan                24576  0
nvgpu                2510848  19
nvmap                 192512  72 nvgpu
ch343                  45056  2
nfsd                  200704  11
ip_tables              36864  2 iptable_filter,iptable_nat
x_tables               49152  8 xt_conntrack,iptable_filter,xt_state,xt_tcpudp,xt_addrtype,ipt_REJECT,ip_tables,xt_MASQUERADE

wheeltec@wheeltec:~$ roslaunch astra_camera astra.launch
... logging to /home/wheeltec/.ros/log/e4fbbec6-1de1-11b2-8ba6-d0abd5132608/roslaunch-wheeltec-9672.log
Checking log directory for disk usage. This may take a while.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://192.168.0.100:44905/

SUMMARY
========

PARAMETERS
 * /camera/camera/camera_name: camera
 * /camera/camera/color_depth_synchronization: False
 * /camera/camera/color_format: RGB
 * /camera/camera/color_fps: 30
 * /camera/camera/color_height: 480
 * /camera/camera/color_info_uri: 
 * /camera/camera/color_width: 640
 * /camera/camera/connection_delay: 100
 * /camera/camera/depth_align: False
 * /camera/camera/depth_format: Y11
 * /camera/camera/depth_fps: 30
 * /camera/camera/depth_height: 480
 * /camera/camera/depth_scale: 1
 * /camera/camera/depth_width: 640
 * /camera/camera/device_num: 1
 * /camera/camera/enable_color: True
 * /camera/camera/enable_d2c_viewer: False
 * /camera/camera/enable_depth: True
 * /camera/camera/enable_ir: True
 * /camera/camera/enable_point_cloud: True
 * /camera/camera/enable_point_cloud_xyzrgb: False
 * /camera/camera/enable_publish_extrinsic: False
 * /camera/camera/flip_color: False
 * /camera/camera/flip_depth: False
 * /camera/camera/flip_ir: False
 * /camera/camera/ir_format: Y10
 * /camera/camera/ir_fps: 30
 * /camera/camera/ir_height: 480
 * /camera/camera/ir_info_uri: 
 * /camera/camera/ir_width: 640
 * /camera/camera/oni_log_level: verbose
 * /camera/camera/oni_log_to_console: False
 * /camera/camera/oni_log_to_file: False
 * /camera/camera/product_id: 
 * /camera/camera/publish_tf: True
 * /camera/camera/serial_number: 
 * /camera/camera/soft_filter: 2
 * /camera/camera/soft_filter_max_diff: 16
 * /camera/camera/soft_filter_max_speckle_size: 480
 * /camera/camera/tf_publish_rate: 10.0
 * /camera/camera/vendor_id: 0x2bc5
 * /rosdistro: noetic
 * /rosversion: 1.17.0

NODES
  /camera/
    camera (astra_camera/astra_camera_node)

ROS_MASTER_URI=http://192.168.0.100:11311

process[camera/camera-1]: started with pid [9697]
[ INFO] [9272.868177088]: Starting camera node...
[ INFO] [9272.879483968]: Creating camera node...
[ INFO] [9272.880553824]: OBCameraNodeFactory::OBCameraNodeFactory
[ INFO] [9272.880602656]: Initializing OBCameraNodeFactory...
[ INFO] [9272.905773568]: init Done
[ INFO] [9272.905850688]: Query device
[ INFO] [9272.905904352]: Creating camera node done...
[ INFO] [9272.905938816]: Found 1 devices
[ INFO] [9273.006145088]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [9273.006242464]: Trying to open device: 2bc5/0402@1/4
[ INFO] [9273.106376544]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [9273.905948160]: wait for device  to be connected
[ INFO] [9274.905796736]: wait for device  to be connected
[ INFO] [9275.905809312]: wait for device  to be connected
[ INFO] [9276.905800416]: wait for device  to be connected
[ INFO] [9277.905762464]: wait for device  to be connected
[ INFO] [9278.189737280]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [9278.189856672]: Device connected: Astra serial number: 17112810687
[ INFO] [9278.189920768]: Start device 
[ INFO] [9278.282674880]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [9278.283125792]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [9278.286092544]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [9278.286507296]: OBCameraNode::setupUVCCamera
[ WARN] [9278.286635296]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [9278.315165312]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [9278.315374816]: find uvc device failed, retry 100 times
[ INFO] [9278.821383488]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [9278.821551904]: Find device error No such device process will be exit
[ERROR] [9278.835371744]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [9278.835477792]: OBCameraNode::clean stop poll frame
[ INFO] [9278.835538624]: OBCameraNode::clean stop poll frame done
[ INFO] [9278.835583936]: OBCameraNode::clean stop tf
[ INFO] [9278.887715232]: OBCameraNode::clean stop tf done.
[ INFO] [9278.888256224]: OBCameraNode::clean stop streams done.
[ INFO] [9278.888306848]: OBCameraNode::clean close device
[ INFO] [9278.888336672]: OBCameraNode::clean close device done.
[ INFO] [9278.888360288]: OBCameraNode::clean stop streams done.
[ INFO] [9278.905770976]: wait for device  to be connected
[ERROR] [9278.936763424]: Start device  failed: std::exception
[ INFO] [9278.936960768]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [9278.937016000]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [9278.937062784]: Query device
[ INFO] [9279.037243680]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [9279.037436512]: Trying to open device: 2bc5/0402@1/4
[ INFO] [9279.137607584]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [9279.137731936]: Device connected: Astra serial number: 17112810687
[ INFO] [9279.137791712]: Start device 
[ INFO] [9279.218448992]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [9279.218868608]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [9279.221717632]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [9279.221843680]: OBCameraNode::setupUVCCamera
[ WARN] [9279.222057504]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [9279.252184896]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [9279.252338688]: find uvc device failed, retry 100 times
[ INFO] [9279.758374528]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [9279.758513504]: Find device error No such device process will be exit
[ERROR] [9279.770659360]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [9279.770755904]: OBCameraNode::clean stop poll frame
[ INFO] [9279.770814272]: OBCameraNode::clean stop poll frame done
[ INFO] [9279.770853216]: OBCameraNode::clean stop tf
[ INFO] [9279.823089984]: OBCameraNode::clean stop tf done.
[ INFO] [9279.823671744]: OBCameraNode::clean stop streams done.
[ INFO] [9279.823756000]: OBCameraNode::clean close device
[ INFO] [9279.823788960]: OBCameraNode::clean close device done.
[ INFO] [9279.823814656]: OBCameraNode::clean stop streams done.
[ERROR] [9279.876241728]: Start device  failed: std::exception
[ INFO] [9279.876335264]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [9279.876364640]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [9279.905781472]: wait for device  to be connected
[ INFO] [9280.076648640]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [9280.076761824]: Device connected: Astra serial number: 17112810687
[ INFO] [9280.076807808]: Start device 
[ INFO] [9280.171856736]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [9280.171988928]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [9280.174715232]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [9280.174840256]: OBCameraNode::setupUVCCamera
[ WARN] [9280.174933728]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [9280.206021056]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [9280.206213376]: find uvc device failed, retry 100 times
[ INFO] [9280.712196384]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [9280.712339424]: Find device error No such device process will be exit
[ERROR] [9280.726232608]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [9280.726327968]: OBCameraNode::clean stop poll frame
[ INFO] [9280.726373152]: OBCameraNode::clean stop poll frame done
[ INFO] [9280.726411296]: OBCameraNode::clean stop tf
^C[camera/camera-1] killing on exit
ERROR: uvc_find_device: No such device (-4)
shutting down processing monitor...
... shutting down processing monitor complete
done

wheeltec@wheeltec:~$ roslaunch astra_camera astra.launch use_uvc_camera:=false
... logging to /home/wheeltec/.ros/log/e4fbbec6-1de1-11b2-8ba6-d0abd5132608/roslaunch-wheeltec-9860.log
Checking log directory for disk usage. This may take a while.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://192.168.0.100:35769/

SUMMARY
========

PARAMETERS
 * /camera/camera/camera_name: camera
 * /camera/camera/color_depth_synchronization: False
 * /camera/camera/color_format: RGB
 * /camera/camera/color_fps: 30
 * /camera/camera/color_height: 480
 * /camera/camera/color_info_uri: 
 * /camera/camera/color_width: 640
 * /camera/camera/connection_delay: 100
 * /camera/camera/depth_align: False
 * /camera/camera/depth_format: Y11
 * /camera/camera/depth_fps: 30
 * /camera/camera/depth_height: 480
 * /camera/camera/depth_scale: 1
 * /camera/camera/depth_width: 640
 * /camera/camera/device_num: 1
 * /camera/camera/enable_color: True
 * /camera/camera/enable_d2c_viewer: False
 * /camera/camera/enable_depth: True
 * /camera/camera/enable_ir: True
 * /camera/camera/enable_point_cloud: True
 * /camera/camera/enable_point_cloud_xyzrgb: False
 * /camera/camera/enable_publish_extrinsic: False
 * /camera/camera/flip_color: False
 * /camera/camera/flip_depth: False
 * /camera/camera/flip_ir: False
 * /camera/camera/ir_format: Y10
 * /camera/camera/ir_fps: 30
 * /camera/camera/ir_height: 480
 * /camera/camera/ir_info_uri: 
 * /camera/camera/ir_width: 640
 * /camera/camera/oni_log_level: verbose
 * /camera/camera/oni_log_to_console: False
 * /camera/camera/oni_log_to_file: False
 * /camera/camera/product_id: 
 * /camera/camera/publish_tf: True
 * /camera/camera/serial_number: 
 * /camera/camera/soft_filter: 2
 * /camera/camera/soft_filter_max_diff: 16
 * /camera/camera/soft_filter_max_speckle_size: 480
 * /camera/camera/tf_publish_rate: 10.0
 * /camera/camera/vendor_id: 0x2bc5
 * /rosdistro: noetic
 * /rosversion: 1.17.0

NODES
  /camera/
    camera (astra_camera/astra_camera_node)

ROS_MASTER_URI=http://192.168.0.100:11311

process[camera/camera-1]: started with pid [9884]
[ INFO] [9305.668047424]: Starting camera node...
[ INFO] [9305.679720704]: Creating camera node...
[ INFO] [9305.681012320]: OBCameraNodeFactory::OBCameraNodeFactory
[ INFO] [9305.681062944]: Initializing OBCameraNodeFactory...
[ INFO] [9305.707499072]: init Done
[ INFO] [9305.707579296]: Query device
[ INFO] [9305.707634304]: Creating camera node done...
[ INFO] [9305.707675200]: Found 1 devices
[ INFO] [9305.807863872]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [9305.807935392]: Trying to open device: 2bc5/0402@1/4
[ INFO] [9305.908069632]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [9306.707697216]: wait for device  to be connected
[ INFO] [9307.707514944]: wait for device  to be connected
[ INFO] [9308.707513568]: wait for device  to be connected
[ INFO] [9309.707512128]: wait for device  to be connected
[ INFO] [9310.707518656]: wait for device  to be connected
[ INFO] [9311.012928608]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [9311.013055552]: Device connected: Astra serial number: 17112810687
[ INFO] [9311.013127232]: Start device 
[ INFO] [9311.102841728]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [9311.103306240]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [9311.106216320]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [9311.106375648]: OBCameraNode::setupUVCCamera
[ WARN] [9311.106582656]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [9311.134915616]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [9311.135134528]: find uvc device failed, retry 100 times
[ INFO] [9311.641232512]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [9311.641388352]: Find device error No such device process will be exit
[ERROR] [9311.654106848]: Failed to initialize UVC camera: Find device error No such device process will be exit
[ INFO] [9311.654174688]: OBCameraNode::clean stop poll frame
[ INFO] [9311.654335392]: OBCameraNode::clean stop poll frame done
[ INFO] [9311.654363328]: OBCameraNode::clean stop tf
[ INFO] [9311.707476288]: wait for device  to be connected
[ INFO] [9311.707721408]: OBCameraNode::clean stop tf done.
[ INFO] [9311.708193024]: OBCameraNode::clean stop streams done.
[ INFO] [9311.708232544]: OBCameraNode::clean close device
[ INFO] [9311.708264608]: OBCameraNode::clean close device done.
[ INFO] [9311.708286144]: OBCameraNode::clean stop streams done.
[ERROR] [9311.747932736]: Start device  failed: std::exception
[ INFO] [9311.748004160]: Device: 2bc5/0402@1/4 is not connected
[ INFO] [9311.748037344]: OBCameraNodeFactory::onDeviceConnected close done.
[ INFO] [9311.748079296]: Query device
[ INFO] [9311.848247936]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [9311.848407808]: Trying to open device: 2bc5/0402@1/4
[ INFO] [9311.948711872]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [9311.948833312]: Device connected: Astra serial number: 17112810687
[ INFO] [9311.948894816]: Start device 
[ INFO] [9312.030893088]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [9312.031264032]: set ir video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_GRAY8
[ WARN] [9312.034033696]: No color sensor found or transition is invalid , setting translation to 0
[ INFO] [9312.034145888]: OBCameraNode::setupUVCCamera
[ WARN] [9312.034296544]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [9312.062698528]: open uvc camera
ERROR: uvc_find_device: No such device (-4)
[ERROR] [9312.062849152]: find uvc device failed, retry 100 times
^C[camera/camera-1] killing on exit
[ INFO] [9312.568850368]: uvc config: vendor_id: 0
product_id: 0
width: 640
height: 480
fps: 30
serial_number: 17112810687
format: mjpeg

[ERROR] [9312.568940768]: Find device error No such device process will be exit
ERROR: uvc_find_device: No such device (-4)
shutting down processing monitor...
... shutting down processing monitor complete
done

wheeltec@wheeltec:~$ roslaunch astra_camera embedded_s.launch
... logging to /home/wheeltec/.ros/log/e4fbbec6-1de1-11b2-8ba6-d0abd5132608/roslaunch-wheeltec-10045.log
Checking log directory for disk usage. This may take a while.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://192.168.0.100:42241/

SUMMARY
========

PARAMETERS
 * /camera/camera/camera_name: camera
 * /camera/camera/color_depth_synchronization: False
 * /camera/camera/color_format: RGB
 * /camera/camera/color_fps: 30
 * /camera/camera/color_height: 480
 * /camera/camera/color_info_uri: 
 * /camera/camera/color_roi_height: -1
 * /camera/camera/color_roi_width: -1
 * /camera/camera/color_roi_x: -1
 * /camera/camera/color_roi_y: -1
 * /camera/camera/color_width: 640
 * /camera/camera/connection_delay: 100
 * /camera/camera/depth_align: False
 * /camera/camera/depth_format: Y11
 * /camera/camera/depth_fps: 30
 * /camera/camera/depth_height: 480
 * /camera/camera/depth_roi_height: -1
 * /camera/camera/depth_roi_width: -1
 * /camera/camera/depth_roi_x: -1
 * /camera/camera/depth_roi_y: -1
 * /camera/camera/depth_scale: 1
 * /camera/camera/depth_width: 640
 * /camera/camera/device_num: 1
 * /camera/camera/enable_color: True
 * /camera/camera/enable_d2c_viewer: False
 * /camera/camera/enable_depth: True
 * /camera/camera/enable_ir: True
 * /camera/camera/enable_point_cloud: True
 * /camera/camera/enable_point_cloud_xyzrgb: False
 * /camera/camera/enable_publish_extrinsic: False
 * /camera/camera/flip_color: False
 * /camera/camera/flip_depth: False
 * /camera/camera/flip_ir: False
 * /camera/camera/ir_format: Y10
 * /camera/camera/ir_fps: 30
 * /camera/camera/ir_height: 480
 * /camera/camera/ir_info_uri: 
 * /camera/camera/ir_width: 640
 * /camera/camera/oni_log_level: verbose
 * /camera/camera/oni_log_to_console: False
 * /camera/camera/oni_log_to_file: False
 * /camera/camera/product_id: 
 * /camera/camera/publish_tf: True
 * /camera/camera/serial_number: 
 * /camera/camera/tf_publish_rate: 10.0
 * /camera/camera/use_uvc_camera: False
 * /camera/camera/uvc_camera_format: mjpeg
 * /camera/camera/uvc_flip: False
 * /camera/camera/uvc_product_id: 0x050b
 * /camera/camera/uvc_retry_count: 100
 * /camera/camera/uvc_vendor_id: 0x2bc5
 * /camera/camera/vendor_id: 0x2bc5
 * /rosdistro: noetic
 * /rosversion: 1.17.0

NODES
  /camera/
    camera (astra_camera/astra_camera_node)

ROS_MASTER_URI=http://192.168.0.100:11311

process[camera/camera-1]: started with pid [10069]
[ INFO] [9339.268060736]: Starting camera node...
[ INFO] [9339.279247552]: Creating camera node...
[ INFO] [9339.280639808]: OBCameraNodeFactory::OBCameraNodeFactory
[ INFO] [9339.280693344]: Initializing OBCameraNodeFactory...
[ INFO] [9339.305872992]: init Done
[ INFO] [9339.305955232]: Query device
[ INFO] [9339.306009568]: Creating camera node done...
[ INFO] [9339.306049344]: Found 1 devices
[ INFO] [9339.406242592]: Device connected: (name, Astra) (uri, 2bc5/0402@1/4) (vendor, Orbbec)
[ INFO] [9339.406310432]: Trying to open device: 2bc5/0402@1/4
[ INFO] [9339.506395264]: OBCameraNodeFactory::onDeviceConnected Open device start
[ INFO] [9340.306047328]: wait for device  to be connected
[ INFO] [9341.305864704]: wait for device  to be connected
[ INFO] [9342.305888448]: wait for device  to be connected
[ INFO] [9343.305854880]: wait for device  to be connected
[ INFO] [9344.305855008]: wait for device  to be connected
[ INFO] [9344.590570784]: OBCameraNodeFactory::onDeviceConnected Open device done, STATUS 0
[ INFO] [9344.590700416]: Device connected: Astra serial number: 17112810687
[ INFO] [9344.590769568]: Start device 
[ WARN] [9344.685837664]: Infrared and Color streams are enabled. Infrared stream will be disabled.
[ INFO] [9344.685947680]: set depth video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_DEPTH_1_MM
[ INFO] [9344.686376224]: set color video mode Resolution :640x480@30Hz
format PIXEL_FORMAT_RGB888
[ WARN] [9344.689618592]: No color sensor found or transition is invalid , setting translation to 0
[ WARN] [9344.690028064]: Publishing dynamic camera transforms (/tf) at 10 Hz
[ INFO] [9344.793545824]: using default calibration URL
[ INFO] [9344.793655968]: camera calibration URL: file:///home/wheeltec/.ros/camera_info/ir_camera.yaml
[ INFO] [9344.795082784]: using default calibration URL
[ INFO] [9344.795135680]: camera calibration URL: file:///home/wheeltec/.ros/camera_info/rgb_camera.yaml
[ INFO] [9344.795799328]: OBCameraNode initialized
[ INFO] [9344.795835616]: Start device  done

wheeltec@wheeltec:~$ rostopic echo /camera/depth/camera_info -n 1
header: 
  seq: 0
  stamp: 
    secs: 9344
    nsecs: 795016928
  frame_id: "camera_depth_optical_frame"
height: 480
width: 640
distortion_model: "plumb_bob"
D: [-0.068613, 0.174404, 0.001015, 0.00624, 0.0]
K: [582.795354, 0.0, 321.415982, 0.0, 584.395006, 245.98941, 0.0, 0.0, 1.0]
R: [nan, nan, nan, nan, nan, nan, nan, nan, nan]
P: [586.186035, 0.0, 324.702427, 0.0, 0.0, 590.631409, 246.167765, 0.0, 0.0, 0.0, 1.0, 0.0]
binning_x: 0
binning_y: 0
roi: 
  x_offset: 0
  y_offset: 0
  height: 0
  width: 0
  do_rectify: False
---

wheeltec@wheeltec:~$ rostopic hz /camera/depth/image_raw
subscribed to [/camera/depth/image_raw]
average rate: 29.858
	min: 0.029s max: 0.042s std dev: 0.00342s window: 27
average rate: 29.782
	min: 0.029s max: 0.042s std dev: 0.00306s window: 56
average rate: 29.710
	min: 0.027s max: 0.044s std dev: 0.00337s window: 86
average rate: 29.721
	min: 0.027s max: 0.044s std dev: 0.00322s window: 116
average rate: 29.744
	min: 0.027s max: 0.044s std dev: 0.00309s window: 146
average rate: 29.708
	min: 0.027s max: 0.044s std dev: 0.00320s window: 175
average rate: 29.702
	min: 0.027s max: 0.044s std dev: 0.00318s window: 205
average rate: 29.708
	min: 0.027s max: 0.044s std dev: 0.00317s window: 235
^Caverage rate: 29.716
	min: 0.027s max: 0.044s std dev: 0.00316s window: 249
wheeltec@wheeltec:~$ 

rostopic list | grep -i -E "camera|rgb|depth|image"
/camera/depth/camera_info
  /camera/depth/image_raw
  /camera/depth/points
  /camera/ir/camera_info
  /camera/ir/image_raw
  /camera/rgb/camera_info
  /camera/rgb/image_raw
  /camera/rgb/image_raw/compressed
  /camera/rgb/image_raw/compressed/parameter_descriptions

wheeltec@wheeltec:~$ rostopic echo /camera/rgb/camera_info -n 1
header: 
  seq: 21998
  stamp: 
    secs: 2319
    nsecs: 579459744
  frame_id: ''
height: 480
width: 640
distortion_model: "plumb_bob"
D: [-0.068613, 0.174404, 0.001015, 0.00624, 0.0]
K: [582.795354, 0.0, 321.415982, 0.0, 584.395006, 245.98941, 0.0, 0.0, 1.0]
R: [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
P: [586.186035, 0.0, 324.702427, 0.0, 0.0, 590.631409, 246.167765, 0.0, 0.0, 0.0, 1.0, 0.0]
binning_x: 0
binning_y: 0
roi: 
  x_offset: 0
  y_offset: 0
  height: 0
  width: 0
  do_rectify: False
---

wheeltec@wheeltec:~$ rostopic echo /camera/depth/camera_info -n 1
header: 
  seq: 3
  stamp: 
    secs: 1601
    nsecs: 422871392
  frame_id: ''
height: 480
width: 640
distortion_model: "plumb_bob"
D: [-0.068613, 0.174404, 0.001015, 0.00624, 0.0]
K: [582.795354, 0.0, 321.415982, 0.0, 584.395006, 245.98941, 0.0, 0.0, 1.0]
R: [nan, nan, nan, nan, nan, nan, nan, nan, nan]
P: [586.186035, 0.0, 324.702427, 0.0, 0.0, 590.631409, 246.167765, 0.0, 0.0, 0.0, 1.0, 0.0]
binning_x: 0
binning_y: 0
roi: 
  x_offset: 0
  y_offset: 0
  height: 0
  width: 0
  do_rectify: False
---

wheeltec@wheeltec:~$ ps aux | grep -i body
nobody      2901  0.0  0.0  15736  3724 ?        S    08:00   0:00 /usr/sbin/dnsmasq --conf-file=/dev/null --no-hosts --keep-in-foreground --bind-interfaces --except-interface=lo --clear-on-reload --strict-order --listen-address=192.168.0.100 --dhcp-range=192.168.0.109,192.168.0.254,60m --dhcp-option=option:router,192.168.0.100 --dhcp-lease-max=50 --dhcp-leasefile=/var/lib/NetworkManager/dnsmasq-wlan0.leases --pid-file=/run/nm-dnsmasq-wlan0.pid --conf-dir=/etc/NetworkManager/dnsmasq-shared.d
wheeltec    7267  0.0  0.0  11648   656 pts/5    S+   08:39   0:00 grep --color=auto -i body

wheeltec@wheeltec:~$ rostopic echo /camera/rgb/image_raw -n 1 | head -10
header: 
  seq: 27609
  stamp: 
    secs: 2509
    nsecs: 166015520
  frame_id: "camera_color_optical_frame"
height: 480
width: 640
encoding: "rgb8"
is_bigendian: 0
