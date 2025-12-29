"""
SpeedWatch Pro - Video Processor
================================
Main video processing pipeline combining detection, tracking, and speed calculation.
"""

import cv2
import numpy as np
import os
import csv
from datetime import datetime
from typing import Optional, Generator, Dict, Any
from pathlib import Path

from .detector import VehicleDetector, Detection
from .tracker import CentroidTracker, Track
from .speed_calculator import SpeedCalculator, SpeedResult

# Import settings
import sys
sys.path.append('..')
from config.settings import (
    SPEED_LIMIT, LOG_DIR, SAVE_SNAPSHOTS,
    COLOR_NORMAL, COLOR_OVERSPEED, COLOR_WARNING, COLOR_TEXT,
    FONT, FONT_SCALE, FONT_THICKNESS, BOX_THICKNESS,
    FPS, DETECTION_ZONE_START, DETECTION_ZONE_END
)


class VideoProcessor:
    """
    Main video processing pipeline.
    
    Combines vehicle detection, tracking, and speed calculation
    into a unified processing pipeline with visualization.
    """
    
    def __init__(
        self,
        source: str = "0",
        speed_limit: float = SPEED_LIMIT,
        show_preview: bool = True
    ):
        """
        Initialize the video processor.
        
        Args:
            source: Video file path or camera index (as string)
            speed_limit: Speed limit in km/h
            show_preview: Whether to show live preview window
        """
        self.source = source
        self.speed_limit = speed_limit
        self.show_preview = show_preview
        
        # Initialize components
        self.detector = VehicleDetector()
        self.tracker = CentroidTracker()
        self.speed_calc = SpeedCalculator(speed_limit=speed_limit)
        
        # Initialize video capture
        self._init_video_capture()
        
        # Setup logging
        self._setup_logging()
        
        # Stats
        self.frame_count = 0
        self.total_vehicles = 0
        self.overspeed_count = 0
        self.is_running = False
    
    def _init_video_capture(self):
        """Initialize video capture."""
        # Handle camera index vs file path
        if self.source.isdigit():
            self.cap = cv2.VideoCapture(int(self.source))
        else:
            self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {self.source}")
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or FPS
        
        print(f"✓ Video source: {self.frame_width}x{self.frame_height} @ {self.fps:.1f} fps")
    
    def _setup_logging(self):
        """Setup logging directories and files."""
        self.log_dir = Path(LOG_DIR)
        self.log_dir.mkdir(exist_ok=True)
        
        self.snapshots_dir = self.log_dir / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)
        
        # Create daily log file
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"speed_log_{date_str}.csv"
        
        # Write header if new file
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "vehicle_id", "vehicle_type",
                    "speed_kmh", "speed_limit", "is_overspeed", "confidence"
                ])
        
        print(f"✓ Logging to: {self.log_file}")
    
    def _log_detection(
        self,
        track: Track,
        speed: float,
        frame: Optional[np.ndarray] = None
    ):
        """Log a speed detection to CSV and optionally save snapshot."""
        is_overspeed = speed > self.speed_limit
        timestamp = datetime.now().isoformat()
        
        # Write to CSV
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                track.id,
                track.class_name,
                speed,
                self.speed_limit,
                is_overspeed,
                round(track.confidence, 2)
            ])
        
        # Save snapshot for overspeed
        if is_overspeed and SAVE_SNAPSHOTS and frame is not None and track.bbox:
            self._save_snapshot(frame, track, speed)
    
    def _save_snapshot(self, frame: np.ndarray, track: Track, speed: float):
        """Save a snapshot of an overspeed vehicle."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"overspeed_{track.id}_{timestamp}_{int(speed)}kmh.jpg"
        filepath = self.snapshots_dir / filename
        
        # Crop to bounding box with some padding
        if track.bbox:
            x1, y1, x2, y2 = track.bbox
            pad = 20
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(frame.shape[1], x2 + pad)
            y2 = min(frame.shape[0], y2 + pad)
            crop = frame[y1:y2, x1:x2]
            cv2.imwrite(str(filepath), crop)
    
    def _draw_overlay(
        self,
        frame: np.ndarray,
        tracks: Dict[int, Track],
        speeds: Dict[int, float]
    ) -> np.ndarray:
        """Draw detection overlays on the frame."""
        overlay = frame.copy()
        
        # Draw detection zone
        zone_top = int(self.frame_height * DETECTION_ZONE_START)
        zone_bottom = int(self.frame_height * DETECTION_ZONE_END)
        cv2.line(overlay, (0, zone_top), (self.frame_width, zone_top), 
                 COLOR_WARNING, 1, cv2.LINE_AA)
        cv2.line(overlay, (0, zone_bottom), (self.frame_width, zone_bottom),
                 COLOR_WARNING, 1, cv2.LINE_AA)
        
        # Draw each tracked vehicle
        for track_id, track in tracks.items():
            if not track.is_valid or not track.bbox:
                continue
            
            x1, y1, x2, y2 = track.bbox
            speed = speeds.get(track_id, 0)
            is_overspeed = speed > self.speed_limit
            
            color = COLOR_OVERSPEED if is_overspeed else COLOR_NORMAL
            
            # Draw bounding box
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, BOX_THICKNESS)
            
            # Draw speed label
            label = f"{int(speed)} km/h"
            label_size, _ = cv2.getTextSize(label, FONT, FONT_SCALE, FONT_THICKNESS)
            
            # Label background
            cv2.rectangle(
                overlay,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0] + 10, y1),
                color,
                -1
            )
            
            # Label text
            cv2.putText(
                overlay, label,
                (x1 + 5, y1 - 5),
                FONT, FONT_SCALE, COLOR_TEXT, FONT_THICKNESS, cv2.LINE_AA
            )
            
            # Draw vehicle type
            type_label = f"{track.class_name.upper()}"
            cv2.putText(
                overlay, type_label,
                (x1, y2 + 20),
                FONT, 0.5, color, 1, cv2.LINE_AA
            )
            
            # Overspeed alert
            if is_overspeed:
                cv2.putText(
                    overlay, "OVERSPEED!",
                    (x1, y1 - label_size[1] - 30),
                    FONT, 0.7, COLOR_OVERSPEED, 2, cv2.LINE_AA
                )
        
        # Draw HUD
        self._draw_hud(overlay)
        
        return overlay
    
    def _draw_hud(self, frame: np.ndarray):
        """Draw heads-up display with stats."""
        # Speed limit indicator
        cv2.circle(frame, (self.frame_width - 60, 60), 40, COLOR_OVERSPEED, 3)
        cv2.putText(
            frame, str(int(self.speed_limit)),
            (self.frame_width - 80, 70),
            FONT, 1.0, COLOR_TEXT, 2, cv2.LINE_AA
        )
        
        # Stats
        stats_y = 30
        stats = [
            f"Vehicles: {self.total_vehicles}",
            f"Overspeed: {self.overspeed_count}",
            f"Frame: {self.frame_count}",
        ]
        
        for stat in stats:
            cv2.putText(
                frame, stat,
                (10, stats_y),
                FONT, 0.6, COLOR_TEXT, 1, cv2.LINE_AA
            )
            stats_y += 25
        
        # Recording indicator
        cv2.circle(frame, (10, self.frame_height - 20), 8, COLOR_OVERSPEED, -1)
        cv2.putText(
            frame, "REC",
            (25, self.frame_height - 15),
            FONT, 0.5, COLOR_TEXT, 1, cv2.LINE_AA
        )
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            frame, timestamp,
            (self.frame_width - 200, self.frame_height - 15),
            FONT, 0.5, COLOR_TEXT, 1, cv2.LINE_AA
        )
    
    def process_frame(self, frame: np.ndarray) -> tuple:
        """
        Process a single frame.
        
        Returns:
            Tuple of (annotated_frame, detections_data)
        """
        self.frame_count += 1
        timestamp = self.frame_count / self.fps
        
        # Detect vehicles
        detections = self.detector.detect(frame)
        
        # Prepare data for tracker
        centroids = self.detector.get_centroids(detections)
        bboxes = [d.bbox for d in detections]
        class_names = [d.class_name for d in detections]
        confidences = [d.confidence for d in detections]
        
        # Update tracker
        tracks = self.tracker.update(
            centroids, bboxes, class_names, confidences, timestamp
        )
        
        # Calculate speeds
        speeds = {}
        new_vehicles = set()
        
        for track_id, track in tracks.items():
            if track.is_valid:
                result = self.speed_calc.calculate_speed(
                    track.positions, track.timestamps
                )
                if result:
                    speeds[track_id] = result.speed_kmh
                    track.speed = result.speed_kmh
                    
                    # Log new detections
                    if track_id not in self._logged_tracks:
                        self._logged_tracks.add(track_id)
                        self.total_vehicles += 1
                        if result.is_overspeed:
                            self.overspeed_count += 1
                        self._log_detection(track, result.speed_kmh, frame)
        
        # Draw overlays
        annotated = self._draw_overlay(frame, tracks, speeds)
        
        # Prepare detection data for API
        detections_data = []
        for track_id, track in tracks.items():
            if track.is_valid and track.bbox:
                detections_data.append({
                    "id": track_id,
                    "type": track.class_name,
                    "speed": speeds.get(track_id, 0),
                    "is_overspeed": speeds.get(track_id, 0) > self.speed_limit,
                    "confidence": track.confidence,
                    "bbox": {
                        "x": track.bbox[0] / self.frame_width * 100,
                        "y": track.bbox[1] / self.frame_height * 100,
                        "width": (track.bbox[2] - track.bbox[0]) / self.frame_width * 100,
                        "height": (track.bbox[3] - track.bbox[1]) / self.frame_height * 100,
                    }
                })
        
        return annotated, detections_data
    
    def run(self) -> Generator[tuple, None, None]:
        """
        Run the video processing loop.
        
        Yields:
            Tuple of (frame, detections_data) for each processed frame
        """
        self.is_running = True
        self._logged_tracks = set()
        
        print("\n" + "=" * 50)
        print("SpeedWatch Pro - Running")
        print("=" * 50)
        print(f"Speed Limit: {self.speed_limit} km/h")
        print(f"Preview: {'Enabled' if self.show_preview else 'Disabled'}")
        print("Press 'q' to quit, 's' to save snapshot")
        print("=" * 50 + "\n")
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                if not ret:
                    # Loop video for demo
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                annotated, detections = self.process_frame(frame)
                
                yield annotated, detections
                
                if self.show_preview:
                    cv2.imshow("SpeedWatch Pro", annotated)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        cv2.imwrite(f"snapshot_{self.frame_count}.jpg", annotated)
                        print(f"Saved snapshot_{self.frame_count}.jpg")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop processing and cleanup."""
        self.is_running = False
        self.cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 50)
        print("Session Summary")
        print("=" * 50)
        print(f"Total Frames: {self.frame_count}")
        print(f"Total Vehicles: {self.total_vehicles}")
        print(f"Overspeed Detections: {self.overspeed_count}")
        print(f"Log File: {self.log_file}")
        print("=" * 50)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return {
            "total_vehicles": self.total_vehicles,
            "overspeed_count": self.overspeed_count,
            "frame_count": self.frame_count,
            "speed_limit": self.speed_limit,
            "is_running": self.is_running
        }
    
    def update_speed_limit(self, limit: float):
        """Update the speed limit."""
        self.speed_limit = limit
        self.speed_calc.update_speed_limit(limit)
