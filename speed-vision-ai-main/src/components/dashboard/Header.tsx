import { Activity, Camera, Settings, Bell, Wifi, WifiOff } from 'lucide-react';
import { ConnectionStatus } from '@/types/detection';
import { cn } from '@/lib/utils';

interface HeaderProps {
  connectionStatus: ConnectionStatus;
  onSettingsClick: () => void;
}

export function Header({ connectionStatus, onSettingsClick }: HeaderProps) {
  const statusConfig = {
    connected: { icon: Wifi, text: 'Connected', className: 'text-primary' },
    connecting: { icon: Wifi, text: 'Connecting...', className: 'text-warning animate-pulse' },
    disconnected: { icon: WifiOff, text: 'Disconnected', className: 'text-muted-foreground' },
    error: { icon: WifiOff, text: 'Error', className: 'text-destructive' },
  };

  const status = statusConfig[connectionStatus];
  const StatusIcon = status.icon;

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/50 backdrop-blur-lg sticky top-0 z-50">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Camera className="w-6 h-6 text-primary-foreground" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-primary border-2 border-background pulse-ring" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              <span className="gradient-text">SpeedWatch</span>
              <span className="text-foreground"> Pro</span>
            </h1>
            <p className="text-xs text-muted-foreground">Vehicle Speed Detection System</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/50 border border-border">
          <Activity className="w-4 h-4 text-primary animate-pulse" />
          <span className="text-sm font-medium">Live Monitoring</span>
        </div>

        <div className={cn("flex items-center gap-2 text-sm", status.className)}>
          <StatusIcon className="w-4 h-4" />
          <span className="font-medium">{status.text}</span>
        </div>

        <button className="relative p-2 rounded-lg hover:bg-secondary transition-colors">
          <Bell className="w-5 h-5 text-muted-foreground" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-destructive" />
        </button>

        <button 
          onClick={onSettingsClick}
          className="p-2 rounded-lg hover:bg-secondary transition-colors"
        >
          <Settings className="w-5 h-5 text-muted-foreground hover:text-foreground transition-colors" />
        </button>
      </div>
    </header>
  );
}
