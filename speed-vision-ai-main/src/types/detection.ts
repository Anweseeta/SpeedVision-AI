export interface DetectedVehicle {
  id: string;
  type: 'car' | 'truck' | 'motorcycle' | 'bus';
  speed: number;
  isOverspeed: boolean;
  confidence: number;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  timestamp: Date;
  lane?: number;
}

export interface SpeedLog {
  id: string;
  vehicleId: string;
  vehicleType: string;
  speed: number;
  speedLimit: number;
  isOverspeed: boolean;
  timestamp: Date;
  snapshotUrl?: string;
  lane?: number;
}

export interface SystemStats {
  totalVehicles: number;
  overspeedCount: number;
  averageSpeed: number;
  maxSpeedToday: number;
  detectionRate: number;
  uptime: string;
}

export interface CameraConfig {
  id: string;
  name: string;
  location: string;
  speedLimit: number;
  isActive: boolean;
  resolution: string;
  fps: number;
}

export interface LocationData {
  city: string;
  region: string;
  country: string;
  latitude: number;
  longitude: number;
  public_ip: string;
  is_auto_detected: boolean;
  formatted: string;
}

export type ConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';
