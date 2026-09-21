"""
D455 RGB + Depth → Habitat RGBD PointNav input.

RGB model input normalization (from checkpoint running_mean_and_var):
  Channel 0 (RGB_R?):   mean=0.158, std=0.115
  Channel 1 (RGB_G?):   mean=0.552, std=0.178
  Channel 2 (RGB_B?):   mean=0.522, std=0.185
  Channel 3 (Depth):    mean=0.489, std=0.203
"""

import numpy as np
import cv2

H, W = 256, 256
DEPTH_MAX = 10.0
DEPTH_MIN = 0.0

# Per-channel normalization from Habitat training
CHANNEL_MEAN = np.array([0.158, 0.552, 0.522, 0.489], dtype=np.float32)
CHANNEL_STD  = np.array([0.115, 0.178, 0.185, 0.203], dtype=np.float32)


def preprocess(color_frame, depth_frame) -> np.ndarray:
    """
    Convert D455 RGB + depth frames to RGBD model input.

    Args:
        color_frame: pyrealsense2 color frame (BGR uint8).
        depth_frame: pyrealsense2 depth frame (Z16 mm).

    Returns:
        (4, 256, 256) float32, normalized per channel.
    """
    # RGB: BGR uint8 → RGB float [0, 1]
    rgb = np.asanyarray(color_frame.get_data(), dtype=np.float32) / 255.0
    rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
    rgb = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_LINEAR)

    # Depth: Z16 mm → meters → [0, 1]
    depth_m = np.asanyarray(depth_frame.get_data(), dtype=np.float32) / 1000.0
    depth_m = np.clip(depth_m, DEPTH_MIN, DEPTH_MAX)
    depth_m = _fill_holes(depth_m)
    depth_m = depth_m / DEPTH_MAX
    depth_m = cv2.resize(depth_m, (W, H), interpolation=cv2.INTER_NEAREST)

    # Stack: (H, W, 3) + (H, W) → (H, W, 4)
    rgbd = np.dstack([rgb, depth_m])  # (256, 256, 4)

    # Per-channel normalize: (x - mean) / std
    rgbd = (rgbd - CHANNEL_MEAN) / CHANNEL_STD

    # CHW: (4, 256, 256)
    return np.transpose(rgbd, (2, 0, 1)).astype(np.float32)


def _fill_holes(depth: np.ndarray, max_hole: int = 5) -> np.ndarray:
    """Inpaint small zero-holes."""
    filled = depth.copy()
    zero_mask = (filled == 0)
    if not np.any(zero_mask):
        return filled
    kernel = np.ones((max_hole, max_hole), np.uint8)
    dilated = cv2.dilate(zero_mask.astype(np.uint8), kernel)
    eroded = cv2.erode(zero_mask.astype(np.uint8), kernel)
    small = zero_mask & ~(dilated ^ eroded)
    ys, xs = np.where(small)
    h, w = depth.shape
    for y, x in zip(ys, xs):
        y0, y1 = max(0, y - 10), min(h, y + 10)
        x0, x1 = max(0, x - 10), min(w, x + 10)
        patch = filled[y0:y1, x0:x1]
        valid = patch[patch > 0]
        if len(valid) > 3:
            filled[y, x] = np.median(valid)
    return filled
