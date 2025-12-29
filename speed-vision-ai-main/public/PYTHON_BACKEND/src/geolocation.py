"""
SpeedWatch Pro - Geolocation Module
====================================
Auto-detect location using FREE IP geolocation (ip-api.com).
Falls back gracefully if internet is unavailable.
"""

import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LocationData:
    """Represents auto-detected location data."""
    city: str
    region: str
    country: str
    latitude: float
    longitude: float
    public_ip: str
    is_auto_detected: bool
    formatted: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "public_ip": self.public_ip,
            "is_auto_detected": self.is_auto_detected,
            "formatted": self.formatted
        }


def fetch_location() -> Optional[LocationData]:
    """
    Fetch location using FREE ip-api.com service.
    
    Returns:
        LocationData if successful, None if failed.
    
    Note:
        ip-api.com is free for non-commercial use (45 requests/minute).
        No API key required!
    """
    try:
        # ip-api.com - FREE, no API key needed!
        response = requests.get(
            "http://ip-api.com/json/",
            params={
                "fields": "status,message,country,regionName,city,lat,lon,query"
            },
            timeout=5  # 5 second timeout
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if data.get("status") != "success":
            return None
        
        # Format the location string
        formatted = f"{data.get('city', 'Unknown')}, {data.get('regionName', '')}, {data.get('country', '')} (Lat: {data.get('lat', 0):.4f}, Lon: {data.get('lon', 0):.4f})"
        
        return LocationData(
            city=data.get("city", "Unknown"),
            region=data.get("regionName", ""),
            country=data.get("country", ""),
            latitude=data.get("lat", 0.0),
            longitude=data.get("lon", 0.0),
            public_ip=data.get("query", ""),
            is_auto_detected=True,
            formatted=formatted.strip()
        )
    
    except requests.exceptions.RequestException:
        # Network error - return None for fallback
        return None
    except Exception:
        # Any other error - return None for fallback
        return None


def get_fallback_location() -> LocationData:
    """
    Return fallback location when auto-detection fails.
    
    Returns:
        LocationData with fallback values.
    """
    return LocationData(
        city="",
        region="",
        country="",
        latitude=0.0,
        longitude=0.0,
        public_ip="",
        is_auto_detected=False,
        formatted="Location not detected — enter manually"
    )


def get_location() -> LocationData:
    """
    Get location with automatic fallback.
    
    Returns:
        LocationData - either auto-detected or fallback.
    """
    location = fetch_location()
    return location if location else get_fallback_location()


# ============================================
# Quick Test
# ============================================
if __name__ == "__main__":
    print("🌍 Testing Geolocation Module...")
    location = get_location()
    
    if location.is_auto_detected:
        print(f"✅ Auto-detected location:")
        print(f"   City: {location.city}")
        print(f"   Region: {location.region}")
        print(f"   Country: {location.country}")
        print(f"   Coordinates: ({location.latitude}, {location.longitude})")
        print(f"   Public IP: {location.public_ip}")
        print(f"   Formatted: {location.formatted}")
    else:
        print(f"❌ Could not detect location")
        print(f"   Fallback: {location.formatted}")
