"""
SpeedWatch Pro - Speed Calculator
=================================
Calculates vehicle speed from tracked positions.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Import settings
import sys
sys.path.append('..')
from config.settings import (
    PIXELS_PER_METER, FPS, SPEED_LIMIT, MIN_DISTANCE_THRESHOLD
)


@dataclass
class SpeedResult:
    """Represents a speed calculation result."""
    speed_kmh: float
    speed_mph: float
    is_overspeed: bool
    distance_pixels: float
    time_seconds: float


class SpeedCalculator:
    """
    Calculates vehicle speed from position history.
    
    Uses the displacement between positions and the time
    between frames to calculate speed in km/h.
    
    Attributes:
        pixels_per_meter: Calibration factor
        fps: Video frame rate
        speed_limit: Speed limit for overspeed detection
    """
    
    def __init__(
        self,
        pixels_per_meter: float = PIXELS_PER_METER,
        fps: float = FPS,
        speed_limit: float = SPEED_LIMIT
    ):
        """
        Initialize the speed calculator.
        
        Args:
            pixels_per_meter: Pixels per real-world meter
            fps: Video frame rate
            speed_limit: Speed limit in km/h
        """
        self.pixels_per_meter = pixels_per_meter
        self.fps = fps
        self.speed_limit = speed_limit
    
    def calculate_speed(
        self,
        positions: List[Tuple[int, int]],
        timestamps: Optional[List[float]] = None
    ) -> Optional[SpeedResult]:
        """
        Calculate speed from position history.
        
        Uses a sliding window approach for smoother speed estimation.
        
        Args:
            positions: List of (x, y) positions
            timestamps: Optional list of timestamps
            
        Returns:
            SpeedResult or None if not enough data
        """
        if len(positions) < 2:
            return None
        
        # Use last N positions for smoothing
        n_positions = min(10, len(positions))
        recent_positions = positions[-n_positions:]
        
        # Calculate total displacement
        total_distance = 0.0
        for i in range(1, len(recent_positions)):
            p1 = recent_positions[i - 1]
            p2 = recent_positions[i]
            distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            total_distance += distance
        
        # Check minimum distance threshold
        if total_distance < MIN_DISTANCE_THRESHOLD:
            return None
        
        # Calculate time elapsed
        if timestamps and len(timestamps) >= n_positions:
            recent_timestamps = timestamps[-n_positions:]
            time_elapsed = recent_timestamps[-1] - recent_timestamps[0]
        else:
            time_elapsed = (n_positions - 1) / self.fps
        
        if time_elapsed <= 0:
            return None
        
        # Convert to meters
        distance_meters = total_distance / self.pixels_per_meter
        
        # Calculate speed in m/s, then convert to km/h
        speed_ms = distance_meters / time_elapsed
        speed_kmh = speed_ms * 3.6
        speed_mph = speed_kmh * 0.621371
        
        return SpeedResult(
            speed_kmh=round(speed_kmh, 1),
            speed_mph=round(speed_mph, 1),
            is_overspeed=speed_kmh > self.speed_limit,
            distance_pixels=total_distance,
            time_seconds=time_elapsed
        )
    
    def calculate_instantaneous_speed(
        self,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        dt: float
    ) -> float:
        """
        Calculate instantaneous speed between two points.
        
        Args:
            p1: First position (x, y)
            p2: Second position (x, y)
            dt: Time difference in seconds
            
        Returns:
            Speed in km/h
        """
        if dt <= 0:
            return 0.0
        
        distance_pixels = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        distance_meters = distance_pixels / self.pixels_per_meter
        speed_ms = distance_meters / dt
        speed_kmh = speed_ms * 3.6
        
        return round(speed_kmh, 1)
    
    def update_calibration(self, pixels_per_meter: float):
        """Update the calibration factor."""
        self.pixels_per_meter = pixels_per_meter
    
    def update_speed_limit(self, speed_limit: float):
        """Update the speed limit."""
        self.speed_limit = speed_limit


# Convenience function for testing
def test_calculator():
    """Test the speed calculator with synthetic data."""
    print("Testing Speed Calculator...")
    
    calculator = SpeedCalculator(
        pixels_per_meter=8.8,
        fps=30,
        speed_limit=80
    )
    
    # Simulate a vehicle moving at ~60 km/h
    # 60 km/h = 16.67 m/s
    # At 8.8 pixels/meter and 30 fps:
    # displacement per frame = 16.67 / 30 * 8.8 ≈ 4.9 pixels
    
    positions = [(100 + i * 5, 200) for i in range(30)]
    timestamps = [i / 30.0 for i in range(30)]
    
    result = calculator.calculate_speed(positions, timestamps)
    
    if result:
        print(f"Speed: {result.speed_kmh} km/h ({result.speed_mph} mph)")
        print(f"Overspeed: {result.is_overspeed}")
        print(f"Distance: {result.distance_pixels:.1f} px over {result.time_seconds:.2f}s")
    else:
        print("Not enough data")


if __name__ == "__main__":
    test_calculator()
