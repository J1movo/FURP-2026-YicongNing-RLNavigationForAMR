"""
Orbbec Astra S → Habitat PointNav observation format.

Preprocesses raw ROS Image messages (RGB + depth) into the tensor format
expected by PointNavResNetPolicy:

    RGB:   640×480 rgb8 → resize 256×256 → uint8 [0,255]
    Depth: 640×480 16UC1 mm → clip(0,10)m → /10.0 → 256×256 float32 [0,1]

Training config (from ckpt.49.pth, HM3D):
    Resolution:      256 × 256
    RGB:             uint8 [0,255], RunningMeanAndVar normalisation inside model
    Depth:           min_depth=0.0, max_depth=10.0, normalize_depth=true
    HFOV:            90° (training) vs ~57.6° (Astra S) — notable gap

Important:
    Do NOT divide RGB by 255 — the model's internal RunningMeanAndVar layer
    was trained on raw uint8 values and the checkpoint bundles its stats.
    Depth MUST divide by exactly 10.0 to match HabitatSimDepthSensor.
"""

import numpy as np
import cv2


# ---------------------------------------------------------------------------
# Config (match training exactly)
# ---------------------------------------------------------------------------

H = 256
W = 256
MAX_DEPTH = 10.0   # metres (Habitat PointNav default)
MIN_DEPTH = 0.0    # training used min_depth=0.0, not 0.5


def preprocess_rgb(rgb_msg) -> np.ndarray:
    """
    ROS sensor_msgs/Image (rgb8, 640×480) → model RGB tensor.

    Args:
        rgb_msg: sensor_msgs/Image with encoding='rgb8'.

    Returns:
        numpy (256, 256, 3), uint8, range [0, 255].
    """
    # ROS Image → numpy: flat uint8 array → (H, W, 3)
    data = np.frombuffer(rgb_msg.data, dtype=np.uint8)
    if rgb_msg.encoding == "rgb8":
        img = data.reshape(rgb_msg.height, rgb_msg.width, 3)
    elif rgb_msg.encoding == "bgr8":
        img = data.reshape(rgb_msg.height, rgb_msg.width, 3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif rgb_msg.encoding == "mono8":
        # IR grayscale → replicate to 3 channels
        img = data.reshape(rgb_msg.height, rgb_msg.width)
        img = np.stack([img, img, img], axis=-1)
    else:
        raise ValueError(f"Unsupported RGB encoding: {rgb_msg.encoding}")

    # Resize to training resolution (INTER_LINEAR for RGB)
    rgb_resized = cv2.resize(img, (W, H), interpolation=cv2.INTER_LINEAR)

    # Keep as uint8 — RunningMeanAndVar inside model handles normalization
    return rgb_resized


def preprocess_depth(depth_msg) -> np.ndarray:
    """
    ROS sensor_msgs/Image (16UC1 mm or 32FC1 m) → model depth tensor.

    Reproduces HabitatSimDepthSensor.get_observation() exactly:
        normalized = clip(depth_meters, MIN_DEPTH, MAX_DEPTH) / MAX_DEPTH

    Args:
        depth_msg: sensor_msgs/Image, typically 16UC1 in mm.

    Returns:
        numpy (256, 256), float32, range [0.0, 1.0].
    """
    data = np.frombuffer(depth_msg.data, dtype=_depth_dtype(depth_msg))

    if depth_msg.encoding == "16UC1":
        depth_m = data.reshape(depth_msg.height, depth_msg.width).astype(np.float32) / 1000.0
    elif depth_msg.encoding == "32FC1":
        depth_m = data.reshape(depth_msg.height, depth_msg.width).astype(np.float32)
    else:
        raise ValueError(f"Unsupported depth encoding: {depth_msg.encoding}")

    # Clip to training range
    depth_m = np.clip(depth_m, MIN_DEPTH, MAX_DEPTH)

    # Fill small holes (reflective / dark surfaces produce zeros)
    depth_m = _fill_holes(depth_m)

    # Normalize: depth / max_depth (match Habitat)
    depth_norm = depth_m / MAX_DEPTH

    # Resize to training resolution (INTER_NEAREST to avoid interpolating depth edges)
    depth_resized = cv2.resize(depth_norm, (W, H), interpolation=cv2.INTER_NEAREST)

    return depth_resized.astype(np.float32)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _depth_dtype(msg) -> np.dtype:
    """Map sensor_msgs/Image encoding string to numpy dtype."""
    mapping = {
        "16UC1": np.uint16,
        "32FC1": np.float32,
        "mono16": np.uint16,
    }
    if msg.encoding in mapping:
        return mapping[msg.encoding]
    raise ValueError(f"Unsupported depth encoding: {msg.encoding}")


def _fill_holes(depth: np.ndarray, max_hole: int = 5, radius: int = 10) -> np.ndarray:
    """
    Inpaint isolated zero-holes with the median of surrounding valid pixels.

    Structured-light cameras (like Astra) produce zero pixels on reflective,
    dark, or far surfaces.
    """
    filled = depth.copy()
    zero_mask = filled == 0
    if not np.any(zero_mask):
        return filled

    # Identify small isolated holes (not large missing regions)
    kernel = np.ones((max_hole, max_hole), np.uint8)
    dilated = cv2.dilate(zero_mask.astype(np.uint8), kernel)
    eroded = cv2.erode(zero_mask.astype(np.uint8), kernel)
    small_holes_mask = zero_mask & ~(dilated ^ eroded)

    ys, xs = np.where(small_holes_mask)
    h, w = depth.shape
    for y, x in zip(ys, xs):
        y0, y1 = max(0, y - radius), min(h, y + radius)
        x0, x1 = max(0, x - radius), min(w, x + radius)
        patch = filled[y0:y1, x0:x1]
        valid = patch[patch > 0]
        if len(valid) > 3:
            filled[y, x] = np.median(valid)

    return filled


def preprocess_rgb_from_array(img: np.ndarray) -> np.ndarray:
    """
    Same as preprocess_rgb() but from a numpy array (H, W, 3) uint8.
    Useful for offline testing.
    """
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    return cv2.resize(img, (W, H), interpolation=cv2.INTER_LINEAR)


def preprocess_depth_from_array(depth_mm: np.ndarray) -> np.ndarray:
    """
    Same as preprocess_depth() but from a numpy array (uint16 mm).
    Useful for offline testing.
    """
    depth_m = depth_mm.astype(np.float32) / 1000.0
    depth_m = np.clip(depth_m, MIN_DEPTH, MAX_DEPTH)
    depth_m = _fill_holes(depth_m)
    depth_norm = depth_m / MAX_DEPTH
    return cv2.resize(depth_norm, (W, H), interpolation=cv2.INTER_NEAREST).astype(np.float32)
