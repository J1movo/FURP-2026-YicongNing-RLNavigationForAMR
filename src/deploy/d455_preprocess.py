"""
D455 depth → Habitat PointNav input format.

Training config (depth-only PointNav, Gibson):
    Resolution:  256 × 256
    Depth range: [0.0, 10.0] m
    Normalisation: depth / 10.0

Intrinsics note:
    Habitat training used hfov=90°.  The D455 has hfov=87°.
    The 3° difference is small enough that the model should tolerate it.
"""

import numpy as np
import cv2

H = 256
W = 256
MAX_DEPTH = 10.0   # metres (Habitat PointNav default)
MIN_DEPTH = 0.5    # clip floor — camera at 0.22m on TB3 Burger, floor visible at ~0.4m
CROP_BOTTOM_PX = 180  # discard bottom 180 rows of raw 480-row image (ground region)


def preprocess(depth_frame) -> np.ndarray:
    """
    Convert a pyrealsense2 depth frame to model input.

    Camera is mounted horizontally at ~0.22m (TB3 Burger top plate).  At this
    height the bottom ~40 % of the D455 FOV (58 °V, half = 29 ° downward) sees
    the floor at ~0.4 m.  We crop the bottom and clip near-range values.

    Args:
        depth_frame: pyrealsense2 depth frame (uint16 mm, 640×480).

    Returns:
        (1, 256, 256) float32, range [0, 1].
    """
    # mm → metres
    depth_m = np.asanyarray(depth_frame.get_data(), dtype=np.float32) / 1000.0

    # crop bottom rows (ground region at low camera height)
    if CROP_BOTTOM_PX > 0:
        depth_m = depth_m[:-CROP_BOTTOM_PX, :]

    # clip to training range
    depth_m = np.clip(depth_m, MIN_DEPTH, MAX_DEPTH)

    # fill small holes (reflective / dark / far surfaces produce zeros)
    depth_m = _fill_holes(depth_m)

    # normalise (Habitat: normalize_depth=True → depth / max_depth)
    depth_norm = depth_m / MAX_DEPTH

    # resize to training resolution
    depth_resized = cv2.resize(depth_norm, (W, H), interpolation=cv2.INTER_NEAREST)

    return np.expand_dims(depth_resized, axis=0).astype(np.float32)


def preprocess_from_array(depth_mm: np.ndarray) -> np.ndarray:
    """
    Same as preprocess(), but from a numpy array (uint16 mm) rather than
    a pyrealsense2 frame.  Useful for offline testing.
    """
    depth_m = depth_mm.astype(np.float32) / 1000.0
    if CROP_BOTTOM_PX > 0:
        depth_m = depth_m[:-CROP_BOTTOM_PX, :]
    depth_m = np.clip(depth_m, MIN_DEPTH, MAX_DEPTH)
    depth_m = _fill_holes(depth_m)
    depth_norm = depth_m / MAX_DEPTH
    depth_resized = cv2.resize(depth_norm, (W, H), interpolation=cv2.INTER_NEAREST)
    return np.expand_dims(depth_resized, axis=0).astype(np.float32)


# ---------------------------------------------------------------------------
# helper
# ---------------------------------------------------------------------------

def _fill_holes(depth: np.ndarray, max_hole: int = 5) -> np.ndarray:
    """
    Inpaint isolated zero-holes with the median of surrounding valid pixels.
    """
    filled = depth.copy()
    zero_mask = filled == 0
    if not np.any(zero_mask):
        return filled

    # identify small isolated holes
    kernel = np.ones((max_hole, max_hole), np.uint8)
    dilated = cv2.dilate(zero_mask.astype(np.uint8), kernel)
    eroded = cv2.erode(zero_mask.astype(np.uint8), kernel)
    small_holes_mask = (zero_mask & ~(dilated ^ eroded))

    ys, xs = np.where(small_holes_mask)
    h, w = depth.shape
    radius = 10
    for y, x in zip(ys, xs):
        y0, y1 = max(0, y - radius), min(h, y + radius)
        x0, x1 = max(0, x - radius), min(w, x + radius)
        patch = filled[y0:y1, x0:x1]
        valid = patch[patch > 0]
        if len(valid) > 3:
            filled[y, x] = np.median(valid)

    return filled
