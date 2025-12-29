"""
SpeedWatch Pro - Model Downloader
=================================
Downloads the YOLOv8 model weights for vehicle detection.
"""

import os
from pathlib import Path

def download_yolo_model():
    """Download YOLOv8 nano model for vehicle detection."""
    try:
        from ultralytics import YOLO
        
        print("=" * 50)
        print("SpeedWatch Pro - Model Downloader")
        print("=" * 50)
        
        # Create models directory
        models_dir = Path(__file__).parent
        models_dir.mkdir(exist_ok=True)
        
        model_path = models_dir / "yolov8n.pt"
        
        if model_path.exists():
            print(f"✓ Model already exists at: {model_path}")
            print("  Delete the file and run again to re-download.")
        else:
            print("Downloading YOLOv8n model...")
            print("This may take a few minutes on first run.\n")
            
            # Download by loading the model (ultralytics handles caching)
            model = YOLO("yolov8n.pt")
            
            # The model is automatically downloaded to the ultralytics cache
            # We'll create a reference in our models folder
            print(f"\n✓ Model downloaded successfully!")
            print(f"  Model is cached by ultralytics and ready to use.")
        
        print("\n" + "=" * 50)
        print("Model Options:")
        print("  - yolov8n.pt (default) - Nano: Fastest, good for real-time")
        print("  - yolov8s.pt - Small: Better accuracy, still fast")
        print("  - yolov8m.pt - Medium: Good balance")
        print("  - yolov8l.pt - Large: High accuracy")
        print("  - yolov8x.pt - XLarge: Best accuracy, slower")
        print("=" * 50)
        print("\nTo use a different model, edit config/settings.py")
        print("and change MODEL_PATH to your preferred model.\n")
        
    except ImportError:
        print("ERROR: ultralytics package not installed!")
        print("Run: pip install ultralytics")
        return False
    
    except Exception as e:
        print(f"ERROR downloading model: {e}")
        return False
    
    return True


if __name__ == "__main__":
    download_yolo_model()
