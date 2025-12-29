import { useState, useEffect, useCallback } from 'react';
import { DetectedVehicle, SpeedLog, SystemStats, CameraConfig, ConnectionStatus, LocationData } from '@/types/detection';

// Simulated data for demo purposes
const vehicleTypes = ['car', 'truck', 'motorcycle', 'bus'] as const;

function generateRandomVehicle(speedLimit: number): DetectedVehicle {
  const speed = Math.floor(Math.random() * 80) + 40; // 40-120 km/h
  const type = vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)];
  
  return {
    id: `v_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    type,
    speed,
    isOverspeed: speed > speedLimit,
    confidence: 0.85 + Math.random() * 0.14,
    bbox: {
      x: 20 + Math.random() * 50,
      y: 30 + Math.random() * 30,
      width: 15 + Math.random() * 10,
      height: 20 + Math.random() * 10,
    },
    timestamp: new Date(),
  };
}

// Fetch location from FREE ipapi.co service (supports HTTPS)
async function fetchAutoLocation(): Promise<LocationData> {
  try {
    const response = await fetch('https://ipapi.co/json/');
    
    if (!response.ok) {
      throw new Error('Network error');
    }
    
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.reason || 'Location fetch failed');
    }
    
    const formatted = `${data.city || 'Unknown'}, ${data.region || ''}, ${data.country_name || ''} (Lat: ${(data.latitude || 0).toFixed(4)}, Lon: ${(data.longitude || 0).toFixed(4)})`.trim();
    
    return {
      city: data.city || 'Unknown',
      region: data.region || '',
      country: data.country_name || '',
      latitude: data.latitude || 0,
      longitude: data.longitude || 0,
      public_ip: data.ip || '',
      is_auto_detected: true,
      formatted,
    };
  } catch {
    // Return fallback location
    return {
      city: '',
      region: '',
      country: '',
      latitude: 0,
      longitude: 0,
      public_ip: '',
      is_auto_detected: false,
      formatted: 'Location not detected — enter manually',
    };
  }
}

export function useSpeedDetection() {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [isPlaying, setIsPlaying] = useState(true);
  const [vehicles, setVehicles] = useState<DetectedVehicle[]>([]);
  const [logs, setLogs] = useState<SpeedLog[]>([]);
  const [locationData, setLocationData] = useState<LocationData | null>(null);
  const [isLocationLoading, setIsLocationLoading] = useState(true);
  const [stats, setStats] = useState<SystemStats>({
    totalVehicles: 0,
    overspeedCount: 0,
    averageSpeed: 0,
    maxSpeedToday: 0,
    detectionRate: 98.5,
    uptime: '24h 15m',
  });
  const [config, setConfig] = useState<CameraConfig>({
    id: 'cam_001',
    name: 'Camera 1',
    location: 'Detecting location...',
    speedLimit: 80,
    isActive: true,
    resolution: '1920x1080',
    fps: 30,
  });

  // Auto-detect location on startup
  useEffect(() => {
    const detectLocation = async () => {
      setIsLocationLoading(true);
      const location = await fetchAutoLocation();
      setLocationData(location);
      
      // Update config with auto-detected location
      if (location.is_auto_detected) {
        setConfig(prev => ({ ...prev, location: location.formatted }));
      } else {
        setConfig(prev => ({ ...prev, location: 'Location not detected — enter manually' }));
      }
      
      setIsLocationLoading(false);
    };
    
    detectLocation();
  }, []);

  // Simulate connection
  useEffect(() => {
    const timer = setTimeout(() => {
      setConnectionStatus('connected');
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  // Simulate vehicle detection
  useEffect(() => {
    if (!isPlaying || connectionStatus !== 'connected') return;

    const interval = setInterval(() => {
      // Randomly add/remove vehicles
      if (Math.random() > 0.3) {
        const newVehicle = generateRandomVehicle(config.speedLimit);
        setVehicles(prev => {
          const updated = [...prev.filter(v => Date.now() - v.timestamp.getTime() < 3000), newVehicle];
          return updated.slice(-5); // Keep max 5 vehicles
        });

        // Add to logs
        const log: SpeedLog = {
          id: `log_${Date.now()}`,
          vehicleId: newVehicle.id,
          vehicleType: newVehicle.type,
          speed: newVehicle.speed,
          speedLimit: config.speedLimit,
          isOverspeed: newVehicle.isOverspeed,
          timestamp: newVehicle.timestamp,
          snapshotUrl: newVehicle.isOverspeed ? `/snapshots/${newVehicle.id}.jpg` : undefined,
        };

        setLogs(prev => [log, ...prev].slice(0, 50));

        // Update stats
        setStats(prev => ({
          ...prev,
          totalVehicles: prev.totalVehicles + 1,
          overspeedCount: prev.overspeedCount + (newVehicle.isOverspeed ? 1 : 0),
          averageSpeed: Math.round((prev.averageSpeed * prev.totalVehicles + newVehicle.speed) / (prev.totalVehicles + 1)),
          maxSpeedToday: Math.max(prev.maxSpeedToday, newVehicle.speed),
        }));
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [isPlaying, connectionStatus, config.speedLimit]);

  const togglePlay = useCallback(() => {
    setIsPlaying(prev => !prev);
  }, []);

  const exportCSV = useCallback(() => {
    const headers = ['Time', 'Vehicle Type', 'Speed (km/h)', 'Speed Limit', 'Status'];
    const rows = logs.map(log => [
      new Date(log.timestamp).toLocaleString(),
      log.vehicleType,
      log.speed,
      log.speedLimit,
      log.isOverspeed ? 'Overspeed' : 'Normal',
    ]);

    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `speed_log_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    URL.revokeObjectURL(url);
  }, [logs]);

  const updateConfig = useCallback((newConfig: CameraConfig) => {
    setConfig(newConfig);
    // If location changed manually, update locationData to reflect override
    if (locationData && newConfig.location !== locationData.formatted) {
      setLocationData(prev => prev ? { ...prev, is_auto_detected: false } : null);
    }
  }, [locationData]);

  const refreshLocation = useCallback(async () => {
    setIsLocationLoading(true);
    const location = await fetchAutoLocation();
    setLocationData(location);
    
    if (location.is_auto_detected) {
      setConfig(prev => ({ ...prev, location: location.formatted }));
    }
    
    setIsLocationLoading(false);
  }, []);

  const getCurrentSpeed = useCallback(() => {
    if (vehicles.length === 0) return 0;
    return vehicles[vehicles.length - 1].speed;
  }, [vehicles]);

  return {
    connectionStatus,
    isPlaying,
    vehicles,
    logs,
    stats,
    config,
    locationData,
    isLocationLoading,
    togglePlay,
    exportCSV,
    updateConfig,
    refreshLocation,
    getCurrentSpeed,
  };
}
