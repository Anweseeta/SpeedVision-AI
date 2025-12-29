"""
SpeedWatch Pro - Vehicle Detector
=================================
YOLOv8-based vehicle detection module.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Import settings
import sys
sys.path.append('..')
from config.settings import (
    MODEL_PATH, CONFIDENCE_THRESHOLD, IOU_THRESHOLD,
    VEHICLE_CLASSES, CLASS_NAMES
)


@dataclass
class Detection:
    """Represents a single vehicle detection."""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    class_id: int
    class_name: str
    center: Tuple[int, int]


class VehicleDetector:
    """
    Detects vehicles in video frames using YOLOv8.
    
    Attributes:
        model: YOLOv8 model instance
        confidence: Detection confidence threshold
        classes: List of vehicle class IDs to detect
    """
    
    def __init__(
        self,
        model_path: str = MODEL_PATH,
        confidence: float = CONFIDENCE_THRESHOLD,
        iou: float = IOU_THRESHOLD,
        classes: List[int] = VEHICLE_CLASSES
    ):
        """
        Initialize the vehicle detector.
        
        Args:
            model_path: Path to YOLO weights file
            confidence: Minimum confidence threshold
            iou: IOU threshold for NMS
            classes: List of class IDs to detect
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            print(f"✓ Loaded YOLO model: {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
        
        self.confidence = confidence
        self.iou = iou
        self.classes = classes
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect vehicles in a frame.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            List of Detection objects
        """
        detections = []
        
        # Run inference
        results = self.model(
            frame,
            conf=self.confidence,
            iou=self.iou,
            classes=self.classes,
            verbose=False
        )[0]
        
        # Process results
        if results.boxes is not None:
            boxes = results.boxes.xyxy.cpu().numpy()
            confidences = results.boxes.conf.cpu().numpy()
            class_ids = results.boxes.cls.cpu().numpy().astype(int)
            
            for box, conf, cls_id in zip(boxes, confidences, class_ids):
                x1, y1, x2, y2 = map(int, box)
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                
                detection = Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=float(conf),
                    class_id=int(cls_id),
                    class_name=CLASS_NAMES.get(int(cls_id), "vehicle"),
                    center=center
                )
                detections.append(detection)
        
        return detections
    
    def get_centroids(self, detections: List[Detection]) -> np.ndarray:
        """
        Extract centroids from detections for tracking.
        
        Args:
            detections: List of Detection objects
            
        Returns:
            Numpy array of shape (N, 2) with centroid coordinates
        """
        if not detections:
            return np.empty((0, 2))
        
        return np.array([d.center for d in detections])


# Convenience function for standalone testing
def test_detector():
    """Test the detector with a sample image."""
    import cv2
    
    print("Testing Vehicle Detector...")
    
    # Create detector
    detector = VehicleDetector()
    
    # Create a test image (or load one)
    # For testing, we'll just create a blank frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Run detection
    detections = detector.detect(frame)
    
    print(f"Found {len(detections)} vehicles")
    for det in detections:
        print(f"  - {det.class_name}: {det.confidence:.2f} at {det.center}")


if __name__ == "__main__":
    test_detector()
