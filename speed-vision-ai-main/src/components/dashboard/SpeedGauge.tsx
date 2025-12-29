import { cn } from '@/lib/utils';

interface SpeedGaugeProps {
  currentSpeed: number;
  maxSpeed: number;
  speedLimit: number;
}

export function SpeedGauge({ currentSpeed, maxSpeed, speedLimit }: SpeedGaugeProps) {
  const percentage = Math.min((currentSpeed / maxSpeed) * 100, 100);
  const isOverspeed = currentSpeed > speedLimit;
  
  // Calculate the rotation for the needle (from -135 to 135 degrees)
  const rotation = -135 + (percentage / 100) * 270;

  return (
    <div className="stat-card border border-border flex flex-col items-center justify-center p-8">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-6">
        Current Speed
      </h3>
      
      <div className="relative w-48 h-48">
        {/* Gauge background */}
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          {/* Background arc */}
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="hsl(var(--secondary))"
            strokeWidth="8"
            strokeDasharray="188.5 62.8"
            strokeLinecap="round"
          />
          
          {/* Speed limit indicator */}
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="hsl(var(--warning) / 0.3)"
            strokeWidth="8"
            strokeDasharray={`${(speedLimit / maxSpeed) * 188.5} 251.3`}
            strokeLinecap="round"
          />
          
          {/* Progress arc */}
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke={isOverspeed ? "hsl(var(--destructive))" : "hsl(var(--primary))"}
            strokeWidth="8"
            strokeDasharray={`${(percentage / 100) * 188.5} 251.3`}
            strokeLinecap="round"
            className="transition-all duration-300"
            style={{
              filter: isOverspeed 
                ? 'drop-shadow(0 0 10px hsl(var(--destructive)))' 
                : 'drop-shadow(0 0 10px hsl(var(--primary)))'
            }}
          />
        </svg>

        {/* Center display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn(
            "speed-indicator transition-colors",
            isOverspeed ? "text-destructive" : "text-primary"
          )}>
            {currentSpeed}
          </span>
          <span className="text-sm text-muted-foreground font-medium">km/h</span>
        </div>

        {/* Needle */}
        <div 
          className="absolute top-1/2 left-1/2 w-1 h-20 origin-bottom transition-transform duration-300"
          style={{ transform: `translate(-50%, -100%) rotate(${rotation}deg)` }}
        >
          <div className={cn(
            "w-full h-full rounded-full",
            isOverspeed ? "bg-destructive" : "bg-primary"
          )} />
        </div>

        {/* Center dot */}
        <div className="absolute top-1/2 left-1/2 w-4 h-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-foreground" />
      </div>

      <div className="mt-6 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-primary" />
          <span className="text-xs text-muted-foreground">Normal</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-warning" />
          <span className="text-xs text-muted-foreground">Limit: {speedLimit}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-destructive" />
          <span className="text-xs text-muted-foreground">Overspeed</span>
        </div>
      </div>
    </div>
  );
}
