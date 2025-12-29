import { Download, Image, AlertTriangle, Car, Truck, Bike } from 'lucide-react';
import { SpeedLog } from '@/types/detection';
import { cn } from '@/lib/utils';

interface SpeedLogTableProps {
  logs: SpeedLog[];
  onExportCSV: () => void;
}

const vehicleIcons: Record<string, React.ReactNode> = {
  car: <Car className="w-4 h-4" />,
  truck: <Truck className="w-4 h-4" />,
  motorcycle: <Bike className="w-4 h-4" />,
  bus: <Truck className="w-4 h-4" />,
};

export function SpeedLogTable({ logs, onExportCSV }: SpeedLogTableProps) {
  return (
    <div className="stat-card border border-border overflow-hidden p-0">
      <div className="flex items-center justify-between px-6 py-4 border-b border-border">
        <div>
          <h3 className="text-lg font-semibold">Detection Log</h3>
          <p className="text-sm text-muted-foreground">Real-time vehicle speed records</p>
        </div>
        <button
          onClick={onExportCSV}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <Download className="w-4 h-4" />
          <span className="text-sm font-medium">Export CSV</span>
        </button>
      </div>

      <div className="overflow-auto max-h-[400px]">
        <table className="w-full">
          <thead className="sticky top-0 bg-card">
            <tr className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
              <th className="px-6 py-3">Time</th>
              <th className="px-6 py-3">Vehicle</th>
              <th className="px-6 py-3">Speed</th>
              <th className="px-6 py-3">Limit</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Snapshot</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {logs.map((log, index) => (
              <tr 
                key={log.id} 
                className={cn(
                  "log-row animate-slide-in",
                  log.isOverspeed && "overspeed"
                )}
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <td className="px-6 py-4">
                  <span className="font-mono text-sm">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded bg-secondary">
                      {vehicleIcons[log.vehicleType] || <Car className="w-4 h-4" />}
                    </div>
                    <span className="capitalize text-sm font-medium">{log.vehicleType}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={cn(
                    "font-mono text-lg font-bold",
                    log.isOverspeed ? "text-destructive" : "text-primary"
                  )}>
                    {log.speed}
                    <span className="text-xs text-muted-foreground ml-1">km/h</span>
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="font-mono text-sm text-muted-foreground">
                    {log.speedLimit} km/h
                  </span>
                </td>
                <td className="px-6 py-4">
                  {log.isOverspeed ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-destructive/20 text-destructive text-xs font-medium">
                      <AlertTriangle className="w-3 h-3" />
                      Overspeed
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary/20 text-primary text-xs font-medium">
                      Normal
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {log.snapshotUrl && (
                    <button className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors">
                      <Image className="w-4 h-4 text-muted-foreground" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
