import { X, Save, RefreshCw, MapPin, Globe, Loader2 } from 'lucide-react';
import { CameraConfig, LocationData } from '@/types/detection';
import { useState } from 'react';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  config: CameraConfig;
  onSave: (config: CameraConfig) => void;
  locationData: LocationData | null;
  isLocationLoading: boolean;
  onRefreshLocation: () => void;
}

export function SettingsPanel({ 
  isOpen, 
  onClose, 
  config, 
  onSave, 
  locationData, 
  isLocationLoading,
  onRefreshLocation 
}: SettingsPanelProps) {
  const [localConfig, setLocalConfig] = useState(config);
  const [isLocationOverridden, setIsLocationOverridden] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    onSave(localConfig);
    onClose();
  };

  const handleLocationChange = (value: string) => {
    setLocalConfig({ ...localConfig, location: value });
    setIsLocationOverridden(true);
  };

  const handleRefreshLocation = () => {
    onRefreshLocation();
    setIsLocationOverridden(false);
  };

  // Determine if showing auto-detected badge
  const showAutoDetectedBadge = locationData?.is_auto_detected && !isLocationOverridden;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-background/80 backdrop-blur-sm" onClick={onClose} />
      
      <div className="relative w-full max-w-lg mx-4 animate-slide-in">
        <div className="stat-card border border-border p-0 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <h2 className="text-lg font-semibold">System Settings</h2>
            <button 
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-secondary transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6 space-y-6">
            {/* Camera Configuration */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                Camera Configuration
              </h3>
              
              <div className="grid gap-4">
                {/* Camera Name */}
                <div>
                  <label className="block text-sm font-medium mb-2">Camera Name</label>
                  <input
                    type="text"
                    value={localConfig.name}
                    onChange={(e) => setLocalConfig({ ...localConfig, name: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-lg bg-secondary border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                  />
                </div>

                {/* Location with Auto-Detection */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="flex items-center gap-2 text-sm font-medium">
                      <MapPin className="w-4 h-4 text-primary" />
                      Location
                    </label>
                    
                    {/* Auto-detected badge or refresh button */}
                    <div className="flex items-center gap-2">
                      {isLocationLoading ? (
                        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Detecting...
                        </span>
                      ) : showAutoDetectedBadge ? (
                        <span className="flex items-center gap-1.5 px-2 py-0.5 text-xs font-medium bg-primary/10 text-primary rounded-full border border-primary/20">
                          <Globe className="w-3 h-3" />
                          Auto-detected
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">
                          Manual override
                        </span>
                      )}
                      
                      <button
                        onClick={handleRefreshLocation}
                        disabled={isLocationLoading}
                        className="p-1.5 rounded-md hover:bg-secondary transition-colors disabled:opacity-50"
                        title="Refresh auto-location"
                      >
                        <RefreshCw className={`w-3.5 h-3.5 ${isLocationLoading ? 'animate-spin' : ''}`} />
                      </button>
                    </div>
                  </div>
                  
                  <input
                    type="text"
                    value={localConfig.location}
                    onChange={(e) => handleLocationChange(e.target.value)}
                    placeholder="Location not detected — enter manually"
                    className="w-full px-4 py-2.5 rounded-lg bg-secondary border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                  />
                  
                  {/* Location details (when auto-detected) */}
                  {locationData?.is_auto_detected && !isLocationOverridden && (
                    <div className="mt-2 p-3 rounded-lg bg-primary/5 border border-primary/10">
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-muted-foreground">City:</span>{' '}
                          <span className="font-medium">{locationData.city}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Region:</span>{' '}
                          <span className="font-medium">{locationData.region}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Country:</span>{' '}
                          <span className="font-medium">{locationData.country}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Public IP:</span>{' '}
                          <span className="font-mono font-medium">{locationData.public_ip}</span>
                        </div>
                        <div className="col-span-2">
                          <span className="text-muted-foreground">Coordinates:</span>{' '}
                          <span className="font-mono font-medium">
                            {locationData.latitude.toFixed(4)}, {locationData.longitude.toFixed(4)}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Resolution & FPS */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Resolution</label>
                    <select
                      value={localConfig.resolution}
                      onChange={(e) => setLocalConfig({ ...localConfig, resolution: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-lg bg-secondary border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    >
                      <option value="1920x1080">1920×1080 (FHD)</option>
                      <option value="1280x720">1280×720 (HD)</option>
                      <option value="2560x1440">2560×1440 (QHD)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">FPS</label>
                    <select
                      value={localConfig.fps}
                      onChange={(e) => setLocalConfig({ ...localConfig, fps: Number(e.target.value) })}
                      className="w-full px-4 py-2.5 rounded-lg bg-secondary border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    >
                      <option value={30}>30 FPS</option>
                      <option value={25}>25 FPS</option>
                      <option value={15}>15 FPS</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Speed Detection */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                Speed Detection
              </h3>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Speed Limit (km/h)
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min={20}
                    max={150}
                    step={5}
                    value={localConfig.speedLimit}
                    onChange={(e) => setLocalConfig({ ...localConfig, speedLimit: Number(e.target.value) })}
                    className="flex-1 h-2 rounded-full bg-secondary appearance-none cursor-pointer accent-primary"
                  />
                  <div className="w-20 px-4 py-2 rounded-lg bg-secondary border border-border text-center font-mono font-bold">
                    {localConfig.speedLimit}
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 pt-4 border-t border-border">
              <button
                onClick={handleSave}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium"
              >
                <Save className="w-4 h-4" />
                Save Settings
              </button>
              <button
                onClick={() => {
                  setLocalConfig(config);
                  setIsLocationOverridden(false);
                }}
                className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Reset
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
