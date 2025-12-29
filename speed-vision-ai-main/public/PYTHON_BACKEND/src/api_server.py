"""
SpeedWatch Pro - API Server
===========================
FastAPI server for the web dashboard integration.
Includes auto-location feature using FREE IP geolocation.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

# Import settings
import sys
sys.path.append('..')
from config.settings import API_HOST, API_PORT, CORS_ORIGINS, SPEED_LIMIT

# Import geolocation module
from src.geolocation import get_location, LocationData


# Create FastAPI app
app = FastAPI(
    title="SpeedWatch Pro API",
    description="Vehicle Speed Detection System API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-detect location on startup
auto_location: Optional[LocationData] = None

# Global state (would be replaced with proper state management in production)
state = {
    "processor": None,
    "is_running": False,
    "stats": {
        "total_vehicles": 0,
        "overspeed_count": 0,
        "average_speed": 0,
        "max_speed_today": 0,
        "detection_rate": 98.5,
        "uptime": "0h 0m"
    },
    "recent_logs": [],
    "active_detections": [],
    "config": {
        "speed_limit": SPEED_LIMIT,
        "camera_name": "Camera 1",
        "location": "Highway A1",
        "resolution": "1920x1080",
        "fps": 30
    },
    "location_data": None  # Will be populated on startup
}


# WebSocket connections
active_connections: List[WebSocket] = []


async def broadcast_update(data: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients."""
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except:
            pass


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "SpeedWatch Pro API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/status")
async def get_status():
    """Get system status."""
    return {
        "is_running": state["is_running"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Get detection statistics."""
    return state["stats"]


@app.get("/logs")
async def get_logs(limit: int = 50):
    """Get recent speed logs."""
    return state["recent_logs"][:limit]


@app.get("/config")
async def get_config():
    """Get current configuration including location data."""
    return {
        **state["config"],
        "location_data": state["location_data"]
    }


@app.get("/location")
async def get_location_endpoint():
    """
    Get auto-detected location data.
    Uses FREE ip-api.com service.
    """
    if state["location_data"]:
        return state["location_data"]
    
    # Try to fetch fresh location
    location = get_location()
    state["location_data"] = location.to_dict()
    return state["location_data"]


@app.post("/location/refresh")
async def refresh_location():
    """Refresh auto-detected location."""
    location = get_location()
    state["location_data"] = location.to_dict()
    
    # Update config location if auto-detected
    if location.is_auto_detected:
        state["config"]["location"] = location.formatted
    
    await broadcast_update({
        "type": "location_update",
        "data": state["location_data"]
    })
    
    return state["location_data"]


@app.post("/config")
async def update_config(config: Dict[str, Any]):
    """Update configuration."""
    state["config"].update(config)
    
    # Update processor if running
    if state["processor"] and "speed_limit" in config:
        state["processor"].update_speed_limit(config["speed_limit"])
    
    await broadcast_update({
        "type": "config_update",
        "data": state["config"]
    })
    
    return {"status": "ok", "config": state["config"]}


@app.get("/detections")
async def get_active_detections():
    """Get currently active vehicle detections."""
    return state["active_detections"]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "data": {
                "stats": state["stats"],
                "config": state["config"],
                "is_running": state["is_running"]
            }
        })
        
        # Keep connection alive and receive commands
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif message.get("type") == "update_config":
                    state["config"].update(message.get("data", {}))
                    await broadcast_update({
                        "type": "config_update",
                        "data": state["config"]
                    })
            
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})
    
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.remove(websocket)


# Simulated data for demo (when not connected to video processor)
async def simulate_detections():
    """Simulate vehicle detections for demo mode."""
    import random
    
    vehicle_types = ["car", "truck", "motorcycle", "bus"]
    
    while True:
        if state["is_running"]:
            # Generate random detection
            speed = random.randint(40, 120)
            is_overspeed = speed > state["config"]["speed_limit"]
            
            detection = {
                "id": f"v_{datetime.now().timestamp()}",
                "type": random.choice(vehicle_types),
                "speed": speed,
                "is_overspeed": is_overspeed,
                "confidence": round(random.uniform(0.85, 0.99), 2),
                "bbox": {
                    "x": random.randint(20, 60),
                    "y": random.randint(30, 60),
                    "width": random.randint(10, 20),
                    "height": random.randint(15, 25)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Update stats
            state["stats"]["total_vehicles"] += 1
            if is_overspeed:
                state["stats"]["overspeed_count"] += 1
            
            # Update average speed
            total = state["stats"]["total_vehicles"]
            avg = state["stats"]["average_speed"]
            state["stats"]["average_speed"] = round(
                (avg * (total - 1) + speed) / total, 1
            )
            
            # Update max speed
            if speed > state["stats"]["max_speed_today"]:
                state["stats"]["max_speed_today"] = speed
            
            # Add to logs
            log_entry = {
                "id": detection["id"],
                "vehicle_id": detection["id"],
                "vehicle_type": detection["type"],
                "speed": speed,
                "speed_limit": state["config"]["speed_limit"],
                "is_overspeed": is_overspeed,
                "timestamp": detection["timestamp"]
            }
            state["recent_logs"].insert(0, log_entry)
            state["recent_logs"] = state["recent_logs"][:100]
            
            # Update active detections
            state["active_detections"] = [detection]
            
            # Broadcast to WebSocket clients
            await broadcast_update({
                "type": "detection",
                "data": detection
            })
            
            await broadcast_update({
                "type": "stats_update",
                "data": state["stats"]
            })
        
        await asyncio.sleep(random.uniform(1.0, 3.0))


@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup."""
    global auto_location
    
    # Auto-detect location on startup
    print("🌍 Auto-detecting location...")
    auto_location = get_location()
    state["location_data"] = auto_location.to_dict()
    
    if auto_location.is_auto_detected:
        print(f"✅ Location detected: {auto_location.formatted}")
        state["config"]["location"] = auto_location.formatted
    else:
        print("⚠️ Location not detected - using fallback")
    
    state["is_running"] = True
    asyncio.create_task(simulate_detections())


def run_server(host: str = API_HOST, port: int = API_PORT):
    """Run the API server."""
    print(f"\n🚀 Starting SpeedWatch Pro API Server")
    print(f"   URL: http://{host}:{port}")
    print(f"   Docs: http://{host}:{port}/docs")
    print(f"   WebSocket: ws://{host}:{port}/ws\n")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
