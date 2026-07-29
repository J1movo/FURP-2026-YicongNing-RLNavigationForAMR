"""RGBD model diagnostic — test on Orange Pi with D455."""
import math, sys
import pyrealsense2 as rs
import numpy as np
import cv2
sys.path.insert(0, '.')
from d455_preprocess_rgbd import preprocess
from pointnav_inference import PointNavAgent

pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipe.start(cfg)
align = rs.align(rs.stream.color)

agent = PointNavAgent('model_rgbd.pt')

for i in range(10):
    frames = pipe.wait_for_frames()
    aligned = align.process(frames)
    color = aligned.get_color_frame()
    depth = aligned.get_depth_frame()
    if not color or not depth:
        print(f'Frame {i}: no frame')
        continue

    rgbd = preprocess(color, depth)
    dm = np.asanyarray(depth.get_data(), dtype=np.float32) / 1000.0
    v = dm[dm > 0]
    c = depth.get_distance(320, 240)
    print(f'Frame {i}: min={v.min():.2f}m max={v.max():.2f}m '
          f'mean={v.mean():.2f}m center={c:.2f}m')

    agent.reset()
    a = agent.act(rgbd, (1.0, 0.0, 0.0))
    print(f'  Action: {agent.ACTION_NAMES[a]}')

    if i == 0:
        cv2.imwrite('/tmp/rgb_raw.png', np.asanyarray(color.get_data()))
        cv2.imwrite('/tmp/rgbd_ch0.png',
                    (rgbd[0] * 10 + 5).clip(0, 255).astype(np.uint8))

print('Done')
