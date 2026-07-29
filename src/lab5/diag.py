import math
import pyrealsense2 as rs
import numpy as np
import cv2, sys
sys.path.insert(0, '.')
from d455_preprocess import preprocess
from pointnav_inference import PointNavAgent

pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipe.start(cfg)
agent = PointNavAgent('model_depth_only.pt')

for i in range(5):
    frames = pipe.wait_for_frames()
    df = frames.get_depth_frame()
    dm = np.asanyarray(df.get_data(), dtype=np.float32) / 1000.0
    v = dm[dm > 0]
    c = df.get_distance(320, 240)
    print(f'Frame {i}: min={v.min():.2f}m max={v.max():.2f}m '
          f'mean={v.mean():.2f}m center={c:.2f}m')
    agent.reset()
    di = preprocess(df)
    # Goal: [dist/5.0, sin(θ), cos(θ)]  (Week 4 verified format)
    # 2m straight ahead → dist/5=0.4, θ=0 → [0.4, 0.0, 1.0]
    a = agent.act(di, (0.4, 0.0, 1.0))
    print(f'  Action: {agent.ACTION_NAMES[a]}')
    if i == 0:
        cv2.imwrite('/tmp/depth_raw.png',
                    (dm / 10 * 255).astype(np.uint8))
        cv2.imwrite('/tmp/depth_preproc.png',
                    (di[0] * 255).astype(np.uint8))
        print('  Saved images')

print('Done')
