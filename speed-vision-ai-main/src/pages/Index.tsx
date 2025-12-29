import { useState } from 'react';
import { Car, AlertTriangle, TrendingUp, Gauge, Clock, Activity } from 'lucide-react';
import { Header } from '@/components/dashboard/Header';
import { StatCard } from '@/components/dashboard/StatCard';
import { VideoFeed } from '@/components/dashboard/VideoFeed';
import { SpeedGauge } from '@/components/dashboard/SpeedGauge';
import { SpeedLogTable } from '@/components/dashboard/SpeedLogTable';
import { SettingsPanel } from '@/components/dashboard/SettingsPanel';
import LocationMap from '@/components/dashboard/LocationMap';
import { useSpeedDetection } from '@/hooks/useSpeedDetection';

const Index = () => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const {
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
  } = useSpeedDetection();

  return (
    <div className="min-h-screen bg-background">
      <Header 
        connectionStatus={connectionStatus} 
        onSettingsClick={() => setIsSettingsOpen(true)} 
      />

      <main className="p-6 space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Vehicles"
            value={stats.totalVehicles.toLocaleString()}
            subtitle="today"
            icon={Car}
            trend={{ value: 12, isPositive: true }}
            variant="primary"
          />
          <StatCard
            title="Overspeed Alerts"
            value={stats.overspeedCount}
            subtitle="violations"
            icon={AlertTriangle}
            trend={{ value: 8, isPositive: false }}
            variant="danger"
          />
          <StatCard
            title="Average Speed"
            value={stats.averageSpeed}
            subtitle="km/h"
            icon={TrendingUp}
            variant="default"
          />
          <StatCard
            title="Max Speed Today"
            value={stats.maxSpeedToday}
            subtitle="km/h"
            icon={Gauge}
            variant={stats.maxSpeedToday > config.speedLimit ? 'warning' : 'default'}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Feed - Takes 2 columns */}
          <div className="lg:col-span-2">
            <VideoFeed
              vehicles={vehicles}
              speedLimit={config.speedLimit}
              isPlaying={isPlaying}
              onTogglePlay={togglePlay}
            />
          </div>

          {/* Speed Gauge & Map */}
          <div className="lg:col-span-1 space-y-6">
            <SpeedGauge
              currentSpeed={getCurrentSpeed()}
              maxSpeed={150}
              speedLimit={config.speedLimit}
            />
            <LocationMap
              locationData={locationData}
              isLoading={isLocationLoading}
              cameraName={config.name}
            />
          </div>
        </div>

        {/* Additional Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="stat-card border border-border flex items-center gap-4">
            <div className="p-3 rounded-xl bg-primary/20">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Detection Rate</p>
              <p className="text-2xl font-bold">{stats.detectionRate}%</p>
            </div>
          </div>
          <div className="stat-card border border-border flex items-center gap-4">
            <div className="p-3 rounded-xl bg-accent/20">
              <Clock className="w-6 h-6 text-accent" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">System Uptime</p>
              <p className="text-2xl font-bold">{stats.uptime}</p>
            </div>
          </div>
          <div className="stat-card border border-border flex items-center gap-4">
            <div className="p-3 rounded-xl bg-warning/20">
              <Gauge className="w-6 h-6 text-warning" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Speed Limit</p>
              <p className="text-2xl font-bold">{config.speedLimit} km/h</p>
            </div>
          </div>
        </div>

        {/* Detection Log */}
        <SpeedLogTable logs={logs} onExportCSV={exportCSV} />
      </main>

      {/* Settings Panel */}
      <SettingsPanel
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        config={config}
        onSave={updateConfig}
        locationData={locationData}
        isLocationLoading={isLocationLoading}
        onRefreshLocation={refreshLocation}
      />
    </div>
  );
};

export default Index;
