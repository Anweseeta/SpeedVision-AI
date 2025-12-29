"""
SpeedWatch Pro - Object Tracker
===============================
Centroid-based multi-object tracking with optional Kalman filter.
"""

import numpy as np
from collections import OrderedDict
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from scipy.spatial import distance as dist

# Import settings
import sys
sys.path.append('..')
from config.settings import MAX_DISAPPEARED, MAX_DISTANCE, MIN_HITS


@dataclass
class Track:
    """Represents a tracked object."""
    id: int
    centroid: Tuple[int, int]
    bbox: Optional[Tuple[int, int, int, int]] = None
    class_name: str = "vehicle"
    confidence: float = 0.0
    positions: List[Tuple[int, int]] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)
    hits: int = 0
    disappeared: int = 0
    speed: float = 0.0
    is_valid: bool = False


class CentroidTracker:
    """
    Multi-object tracker using centroid-based association.
    
    This tracker maintains object identities across frames by
    minimizing the distance between centroids.
    
    Attributes:
        max_disappeared: Frames before removing a lost track
        max_distance: Maximum distance for centroid matching
        min_hits: Minimum detections before track is valid
    """
    
    def __init__(
        self,
        max_disappeared: int = MAX_DISAPPEARED,
        max_distance: int = MAX_DISTANCE,
        min_hits: int = MIN_HITS
    ):
        """
        Initialize the tracker.
        
        Args:
            max_disappeared: Max frames to keep lost tracks
            max_distance: Max centroid distance for matching
            min_hits: Min detections before track is valid
        """
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.min_hits = min_hits
        
        self.next_id = 0
        self.tracks: Dict[int, Track] = OrderedDict()
    
    def register(
        self,
        centroid: Tuple[int, int],
        bbox: Optional[Tuple[int, int, int, int]] = None,
        class_name: str = "vehicle",
        confidence: float = 0.0,
        timestamp: float = 0.0
    ) -> int:
        """
        Register a new track.
        
        Args:
            centroid: (x, y) center position
            bbox: Optional bounding box
            class_name: Vehicle type
            confidence: Detection confidence
            timestamp: Frame timestamp
            
        Returns:
            New track ID
        """
        track = Track(
            id=self.next_id,
            centroid=centroid,
            bbox=bbox,
            class_name=class_name,
            confidence=confidence,
            positions=[centroid],
            timestamps=[timestamp],
            hits=1
        )
        self.tracks[self.next_id] = track
        self.next_id += 1
        return track.id
    
    def deregister(self, track_id: int) -> Optional[Track]:
        """
        Remove a track.
        
        Args:
            track_id: ID of track to remove
            
        Returns:
            The removed Track object, or None
        """
        return self.tracks.pop(track_id, None)
    
    def update(
        self,
        centroids: np.ndarray,
        bboxes: Optional[List[Tuple[int, int, int, int]]] = None,
        class_names: Optional[List[str]] = None,
        confidences: Optional[List[float]] = None,
        timestamp: float = 0.0
    ) -> Dict[int, Track]:
        """
        Update tracks with new detections.
        
        Args:
            centroids: Numpy array of shape (N, 2)
            bboxes: Optional list of bounding boxes
            class_names: Optional list of class names
            confidences: Optional list of confidences
            timestamp: Current frame timestamp
            
        Returns:
            Dictionary of active tracks
        """
        # Handle empty detections
        if len(centroids) == 0:
            for track_id in list(self.tracks.keys()):
                self.tracks[track_id].disappeared += 1
                if self.tracks[track_id].disappeared > self.max_disappeared:
                    self.deregister(track_id)
            return self.tracks
        
        # Initialize optional lists
        if bboxes is None:
            bboxes = [None] * len(centroids)
        if class_names is None:
            class_names = ["vehicle"] * len(centroids)
        if confidences is None:
            confidences = [0.0] * len(centroids)
        
        # Register all if no existing tracks
        if len(self.tracks) == 0:
            for i, centroid in enumerate(centroids):
                self.register(
                    tuple(centroid),
                    bboxes[i],
                    class_names[i],
                    confidences[i],
                    timestamp
                )
            return self.tracks
        
        # Match existing tracks with new detections
        track_ids = list(self.tracks.keys())
        track_centroids = np.array([
            self.tracks[tid].centroid for tid in track_ids
        ])
        
        # Compute distances
        D = dist.cdist(track_centroids, centroids)
        
        # Find minimum distance assignments
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]
        
        used_rows = set()
        used_cols = set()
        
        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            
            if D[row, col] > self.max_distance:
                continue
            
            track_id = track_ids[row]
            centroid = tuple(centroids[col])
            
            # Update track
            track = self.tracks[track_id]
            track.centroid = centroid
            track.bbox = bboxes[col]
            track.class_name = class_names[col]
            track.confidence = confidences[col]
            track.positions.append(centroid)
            track.timestamps.append(timestamp)
            track.hits += 1
            track.disappeared = 0
            track.is_valid = track.hits >= self.min_hits
            
            # Keep only recent positions (for speed calculation)
            if len(track.positions) > 30:
                track.positions = track.positions[-30:]
                track.timestamps = track.timestamps[-30:]
            
            used_rows.add(row)
            used_cols.add(col)
        
        # Handle unmatched tracks (disappeared)
        for row in range(len(track_ids)):
            if row not in used_rows:
                track_id = track_ids[row]
                self.tracks[track_id].disappeared += 1
                if self.tracks[track_id].disappeared > self.max_disappeared:
                    self.deregister(track_id)
        
        # Register new detections
        for col in range(len(centroids)):
            if col not in used_cols:
                self.register(
                    tuple(centroids[col]),
                    bboxes[col],
                    class_names[col],
                    confidences[col],
                    timestamp
                )
        
        return self.tracks
    
    def get_valid_tracks(self) -> Dict[int, Track]:
        """Get only valid (confirmed) tracks."""
        return {
            tid: track 
            for tid, track in self.tracks.items() 
            if track.is_valid
        }


# Convenience function for testing
def test_tracker():
    """Test the tracker with synthetic data."""
    print("Testing Centroid Tracker...")
    
    tracker = CentroidTracker()
    
    # Simulate frames with moving objects
    for frame_num in range(10):
        # Simulate detections moving across the frame
        centroids = np.array([
            [100 + frame_num * 10, 200],
            [300 + frame_num * 15, 150],
        ])
        
        tracks = tracker.update(centroids, timestamp=frame_num / 30.0)
        
        print(f"Frame {frame_num}: {len(tracks)} tracks")
        for tid, track in tracks.items():
            status = "valid" if track.is_valid else "pending"
            print(f"  Track {tid}: {track.centroid} ({status})")


if __name__ == "__main__":
    test_tracker()
