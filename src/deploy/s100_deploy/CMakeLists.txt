cmake_minimum_required(VERSION 3.0.2)
project(s100_deploy)

# Pure-Python ROS 1 package — no compilation step.
find_package(catkin REQUIRED)

catkin_package()

# ---------------------------------------------------------------------------
# Python nodes / modules
# ---------------------------------------------------------------------------
# All four files must land in the SAME directory: s100_inference_node.py
# inserts its own directory into sys.path, then does
#     from preprocess import preprocess_rgb, preprocess_depth
#     from action_controller import StepActionController, ...
#     import habitat_stub
# so they are co-located by design rather than installed as a Python package.
catkin_install_python(PROGRAMS
  scripts/s100_inference_node.py
  scripts/action_controller.py
  scripts/preprocess.py
  scripts/habitat_stub.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# ---------------------------------------------------------------------------
# Launch files
# ---------------------------------------------------------------------------
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)

# ---------------------------------------------------------------------------
# Offline / auxiliary tooling (not launched by roslaunch, kept for reference)
# ---------------------------------------------------------------------------
install(DIRECTORY jetson_inference/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/jetson_inference
  PATTERN "__pycache__" EXCLUDE
)

install(DIRECTORY gazebo_sim/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/gazebo_sim
  PATTERN "__pycache__" EXCLUDE
)
