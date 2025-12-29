import { useState, useEffect } from 'react';
import { Play, Pause, Maximize2, Camera, AlertTriangle } from 'lucide-react';
import { DetectedVehicle } from '@/types/detection';
import { cn } from '@/lib/utils';

interface VideoFeedProps {
  vehicles: DetectedVehicle[];
  speedLimit: number;
  isPlaying: boolean;
  onTogglePlay: () => void;
}

export function VideoFeed({ vehicles, speedLimit, isPlaying, onTogglePlay }: VideoFeedProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const hasOverspeed = vehicles.some(v => v.isOverspeed);

  return (
    <div className={cn(
      "relative rounded-2xl overflow-hidden border transition-all duration-300",
      hasOverspeed ? "border-destructive shadow-[0_0_50px_hsl(0_84%_60%_/_0.2)]" : "border-border"
    )}>
      {/* Video Container with simulated feed */}
      <div className="relative aspect-video bg-gradient-to-br from-secondary to-background">
        {/* Simulated video feed background */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0wIDBoNDBMNDAgNDBIMHoiIGZpbGw9IiMxMTExMTEiLz48cGF0aCBkPSJNMjAgMjBsMjAgMjBIMFoiIGZpbGw9IiMxODE4MTgiLz48L2c+PC9zdmc+')] opacity-50" />
        
        {/* Road visualization */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-full h-full relative">
            {/* Road markings */}
            <div className="absolute top-1/2 left-0 right-0 h-px bg-warning/30" />
            <div className="absolute top-1/2 left-0 right-0 flex justify-center gap-8">
              {[...Array(10)].map((_, i) => (
                <div 
                  key={i} 
                  className="w-16 h-1 bg-warning/50 rounded"
                  style={{ animationDelay: `${i * 0.1}s` }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Vehicle Detection Overlays */}
        {vehicles.map((vehicle) => (
          <div
            key={vehicle.id}
            className={cn("video-overlay-box", vehicle.isOverspeed ? "overspeed" : "normal")}
            style={{
              left: `${vehicle.bbox.x}%`,
              top: `${vehicle.bbox.y}%`,
              width: `${vehicle.bbox.width}%`,
              height: `${vehicle.bbox.height}%`,
            }}
          >
            <div className={cn("speed-badge", vehicle.isOverspeed ? "overspeed" : "normal")}>
              <span className="font-mono">{vehicle.speed}</span>
              <span className="text-xs ml-1">km/h</span>
              {vehicle.isOverspeed && <AlertTriangle className="w-3 h-3 ml-1 inline" />}
            </div>
            <div className="absolute bottom-1 left-1 text-[10px] font-mono text-foreground/80 bg-background/60 px-1 rounded">
              {vehicle.type.toUpperCase()} • {(vehicle.confidence * 100).toFixed(0)}%
            </div>
          </div>
        ))}

        {/* Overspeed Alert Overlay */}
        {hasOverspeed && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 rounded-full bg-destructive/90 text-destructive-foreground blink-alert">
              <AlertTriangle className="w-5 h-5" />
              <span className="font-bold uppercase tracking-wider">Overspeed Detected!</span>
            </div>
          </div>
        )}

        {/* Top overlay info */}
        <div className="absolute top-4 left-4 flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-background/80 backdrop-blur-sm border border-border">
            <div className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
            <span className="text-xs font-mono font-medium">REC</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-background/80 backdrop-blur-sm border border-border">
            <span className="text-xs font-mono">{currentTime.toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Speed limit indicator */}
        <div className="absolute top-4 right-4 flex flex-col items-center">
          <div className="w-16 h-16 rounded-full border-4 border-destructive bg-background/90 flex items-center justify-center">
            <span className="text-xl font-bold text-destructive">{speedLimit}</span>
          </div>
          <span className="text-[10px] text-muted-foreground mt-1 uppercase">Speed Limit</span>
        </div>

        {/* Bottom controls */}
        <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={onTogglePlay}
              className="p-3 rounded-full bg-background/80 backdrop-blur-sm border border-border hover:bg-primary hover:border-primary hover:text-primary-foreground transition-all"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            </button>
            <button className="p-3 rounded-full bg-background/80 backdrop-blur-sm border border-border hover:bg-secondary transition-colors">
              <Maximize2 className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-background/80 backdrop-blur-sm border border-border">
            <Camera className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Camera 1 - Highway A1</span>
            <span className="text-xs text-muted-foreground">1920×1080 @ 30fps</span>
          </div>
        </div>
      </div>
    </div>
  );
}
