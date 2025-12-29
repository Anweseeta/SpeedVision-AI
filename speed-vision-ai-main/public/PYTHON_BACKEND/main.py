#!/usr/bin/env python3
"""
SpeedWatch Pro - Main Entry Point
==================================
Vehicle Speed Detection System using Computer Vision

Usage:
    python main.py --source VIDEO_PATH [--api] [--limit SPEED_LIMIT]

Examples:
    python main.py --source test_video.mp4
    python main.py --source 0  # Webcam
    python main.py --source test_video.mp4 --api --limit 60
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SpeedWatch Pro - Vehicle Speed Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a video file:
    python main.py --source traffic_video.mp4

  Use webcam:
    python main.py --source 0

  Run with API server for web dashboard:
    python main.py --source traffic_video.mp4 --api

  Custom speed limit:
    python main.py --source video.mp4 --limit 60
        """
    )
    
    parser.add_argument(
        "--source", "-s",
        type=str,
        default="0",
        help="Video source: file path or camera index (default: 0 for webcam)"
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run API server for web dashboard integration"
    )
    
    parser.add_argument(
        "--limit", "-l",
        type=float,
        default=80,
        help="Speed limit in km/h (default: 80)"
    )
    
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Disable preview window"
    )
    
    parser.add_argument(
        "--calibrate",
        type=float,
        default=None,
        help="Pixels per meter calibration value"
    )
    
    args = parser.parse_args()
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██████╗ ███████╗███████╗██████╗                ║
║   ██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗               ║
║   ███████╗██████╔╝█████╗  █████╗  ██║  ██║               ║
║   ╚════██║██╔═══╝ ██╔══╝  ██╔══╝  ██║  ██║               ║
║   ███████║██║     ███████╗███████╗██████╔╝               ║
║   ╚══════╝╚═╝     ╚══════╝╚══════╝╚═════╝                ║
║                                                           ║
║   ██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗            ║
║   ██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║            ║
║   ██║ █╗ ██║███████║   ██║   ██║     ███████║            ║
║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║            ║
║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║            ║
║    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝            ║
║                                                           ║
║            Vehicle Speed Detection System                 ║
║                    Version 1.0.0                          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if args.api:
        # Run API server mode
        print("Starting in API Server mode...")
        print("Web dashboard can connect to this server.\n")
        
        from src.api_server import run_server
        run_server()
    
    else:
        # Run standalone mode
        print("Starting in Standalone mode...\n")
        
        try:
            from src.video_processor import VideoProcessor
            
            processor = VideoProcessor(
                source=args.source,
                speed_limit=args.limit,
                show_preview=not args.no_preview
            )
            
            if args.calibrate:
                processor.speed_calc.update_calibration(args.calibrate)
                print(f"Calibration set to: {args.calibrate} pixels/meter")
            
            # Run processing loop
            for frame, detections in processor.run():
                pass  # Frame display is handled internally
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
        
        except Exception as e:
            print(f"\nError: {e}")
            print("\nTroubleshooting:")
            print("  1. Make sure you've installed requirements: pip install -r requirements.txt")
            print("  2. Download YOLO model: python models/download_models.py")
            print("  3. Check that your video file exists")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
