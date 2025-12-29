# 🚗 SpeedWatch Pro - Python Backend

## Vehicle Speed Detection using Computer Vision (OpenCV + YOLO)

This is the Python backend for the SpeedWatch Pro vehicle speed detection system. It uses YOLOv8 for vehicle detection and centroid tracking for speed calculation.

---

## 📁 Folder Structure

```
PYTHON_BACKEND/
├── src/
│   ├── detector.py          # YOLOv8 vehicle detection
│   ├── tracker.py           # Centroid-based object tracking
│   ├── speed_calculator.py  # Speed calculation with calibration
│   ├── video_processor.py   # Main video processing pipeline
│   └── api_server.py        # FastAPI server for web dashboard
├── models/
│   └── download_models.py   # Script to download YOLO weights
├── config/
│   └── settings.py          # Configuration settings
├── logs/
│   └── (auto-generated)     # CSV logs and snapshots
├── requirements.txt
└── main.py                   # Entry point
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd PYTHON_BACKEND
pip install -r requirements.txt
```

### 2. Download YOLO Model

```bash
python models/download_models.py
```

### 3. Run the System

**Option A: With Video File**
```bash
python main.py --source path/to/video.mp4
```

**Option B: With Webcam**
```bash
python main.py --source 0
```

**Option C: With API Server (for Web Dashboard)**
```bash
python main.py --source path/to/video.mp4 --api
```

---

## ⚙️ Configuration

Edit `config/settings.py` to customize:

```python
# Speed limit (km/h)
SPEED_LIMIT = 80

# Calibration (pixels per meter) - adjust based on your camera
PIXELS_PER_METER = 8.8

# Detection confidence threshold
CONFIDENCE_THRESHOLD = 0.5

# Frame rate for speed calculation
FPS = 30

# Vehicle classes to detect (COCO)
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck
```

---

## 🎯 Calibration Guide

For accurate speed measurement, you need to calibrate the `PIXELS_PER_METER` value:

1. Measure a known distance in the camera's field of view (e.g., road markings)
2. Count the pixels between those points in the video
3. Calculate: `PIXELS_PER_METER = pixels / meters`

Example: If 50 meters = 440 pixels, then PIXELS_PER_METER = 8.8

---

## 📊 Output

- **Live Display**: Video feed with bounding boxes and speed labels
- **CSV Logs**: `logs/speed_log_YYYY-MM-DD.csv`
- **Snapshots**: `logs/snapshots/` (overspeed vehicles only)

---

## 🌐 API Endpoints

When running with `--api` flag:

- `GET /status` - System status
- `GET /stats` - Detection statistics
- `GET /logs` - Recent speed logs
- `GET /stream` - Video stream (MJPEG)
- `POST /config` - Update settings

---

## 🧪 Test with Sample Video

Download a sample traffic video:
```bash
# Example: Download from Pexels (free)
wget -O test_video.mp4 "https://www.pexels.com/download/video/1721294"
python main.py --source test_video.mp4
```

---

## 📝 License

MIT License - Feel free to use and modify!
