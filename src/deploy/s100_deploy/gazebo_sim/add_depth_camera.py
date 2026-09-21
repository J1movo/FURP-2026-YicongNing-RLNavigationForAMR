#!/usr/bin/env python3
"""Insert depth camera sensor into TB3 Waffle SDF model."""
import sys

path = "/home/jimovo/Desktop/FURP/真机部署/gazebo_sim/models/turtlebot3_waffle_depth/model.sdf"
with open(path, "r") as f:
    content = f.read()

# Depth camera link + sensor
depth_link = """
    <link name="camera_depth_frame">
      <inertial>
        <pose>0.069 -0.047 0.107 0 0 0</pose>
        <inertia>
          <ixx>0.001</ixx>
          <ixy>0.000</ixy>
          <ixz>0.000</ixz>
          <iyy>0.001</iyy>
          <iyz>0.000</iyz>
          <izz>0.001</izz>
        </inertia>
        <mass>0.035</mass>
      </inertial>

      <pose>0.069 -0.047 0.107 0 0 0</pose>
      <sensor name="camera_depth" type="depth">
        <always_on>true</always_on>
        <visualize>false</visualize>
        <update_rate>30</update_rate>
        <camera>
          <horizontal_fov>1.57</horizontal_fov>
          <image>
            <width>256</width>
            <height>256</height>
            <format>R_FLOAT32</format>
          </image>
          <clip>
            <near>0.01</near>
            <far>10.0</far>
          </clip>
        </camera>
        <plugin name="camera_depth_plugin" filename="libgazebo_ros_depth_camera.so">
          <ros>
            <remapping>depth/image_raw:=/camera/depth/image_raw</remapping>
            <remapping>depth/camera_info:=/camera/depth/camera_info</remapping>
          </ros>
          <frame_name>camera_depth_frame</frame_name>
        </plugin>
      </sensor>
    </link>
"""

# Insert after camera_rgb_frame's closing </link> (before base_joint)
marker1 = '    </link>    \n\n    <joint name="base_joint"'
if marker1 in content:
    content = content.replace(marker1, "    </link>" + depth_link + "\n\n    <joint name=\"base_joint\"")
    print("Inserted depth_link")
else:
    print("ERROR: marker1 not found")
    sys.exit(1)

# Insert depth joint before </model>
depth_joint = '    <joint name="camera_depth_joint" type="fixed">\n      <parent>camera_link</parent>\n      <child>camera_depth_frame</child>\n      <pose>0.005 0.018 0.013 0 0 0</pose>\n    </joint>\n\n'
content = content.replace("</model>", depth_joint + "</model>")
print("Inserted depth_joint")

with open(path, "w") as f:
    f.write(content)

print("Done!")
