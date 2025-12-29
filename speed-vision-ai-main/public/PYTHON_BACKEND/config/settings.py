"""
SpeedWatch Pro - Configuration Settings
========================================
Adjust these values to calibrate the system for your specific setup.
"""

# ======================
# SPEED DETECTION
# ======================

# Speed limit in km/h - vehicles above this will trigger alerts
SPEED_LIMIT = 80

# Pixels per meter - CRITICAL for accurate speed calculation
# Calibrate this based on your camera setup:
# 1. Measure a known distance in the camera view (e.g., 10 meters)
# 2. Count the pixels between those points
# 3. Calculate: PIXELS_PER_METER = pixels / meters
PIXELS_PER_METER = 8.8

# Minimum distance (pixels) before calculating speed
# Helps reduce noise from minor position fluctuations
MIN_DISTANCE_THRESHOLD = 20

# ======================
# VIDEO SETTINGS
# ======================

# Expected frame rate of the video/camera
FPS = 30

# Detection zone (percentage of frame height)
# Vehicles are only tracked within this zone
DETECTION_ZONE_START = 0.2  # 20% from top
DETECTION_ZONE_END = 0.8    # 80% from top

# ======================
# YOLO DETECTION
# ======================

# Path to YOLO model weights
MODEL_PATH = "models/yolov8n.pt"

# Confidence threshold for detections
CONFIDENCE_THRESHOLD = 0.5

# IOU threshold for NMS
IOU_THRESHOLD = 0.45

# COCO classes for vehicles:
# 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = [2, 3, 5, 7]

# Class names for display
CLASS_NAMES = {
    2: "car",
    3: "motorcycle", 
    5: "bus",
    7: "truck"
}

# ======================
# TRACKING SETTINGS
# ======================

# Maximum frames to keep a track alive without detection
MAX_DISAPPEARED = 30

# Maximum distance (pixels) to associate detections with tracks
MAX_DISTANCE = 100

# Minimum detections before considering a track valid
MIN_HITS = 3

# ======================
# VISUALIZATION
# ======================

# Colors (BGR format for OpenCV)
COLOR_NORMAL = (0, 255, 0)      # Green
COLOR_OVERSPEED = (0, 0, 255)   # Red
COLOR_WARNING = (0, 165, 255)   # Orange
COLOR_TEXT = (255, 255, 255)    # White

# Font settings
FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
FONT_THICKNESS = 2

# Bounding box thickness
BOX_THICKNESS = 2

# ======================
# LOGGING
# ======================

# Directory for logs and snapshots
LOG_DIR = "logs"

# Save snapshots of overspeed vehicles
SAVE_SNAPSHOTS = True

# Log format
LOG_COLUMNS = [
    "timestamp",
    "vehicle_id",
    "vehicle_type",
    "speed_kmh",
    "speed_limit",
    "is_overspeed",
    "confidence"
]

# ======================
# API SERVER
# ======================

# API server host and port
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS origins (for web dashboard)
CORS_ORIGINS = ["*"]
