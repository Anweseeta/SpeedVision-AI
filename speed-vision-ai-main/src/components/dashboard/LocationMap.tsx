import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Navigation, Maximize2 } from 'lucide-react';
import { LocationData } from '@/types/detection';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

// Fix for default marker icons in Leaflet with Vite
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom camera marker icon
const cameraIcon = new L.DivIcon({
  className: 'custom-camera-marker',
  html: `
    <div class="relative">
      <div class="absolute -inset-2 bg-primary/30 rounded-full animate-ping"></div>
      <div class="relative w-8 h-8 bg-primary rounded-full flex items-center justify-center shadow-lg border-2 border-white">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
          <circle cx="12" cy="13" r="3"/>
        </svg>
      </div>
    </div>
  `,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16],
});

// Example locations for quick selection
const EXAMPLE_LOCATIONS = [
  { name: 'New York, USA', lat: 40.7128, lon: -74.0060, city: 'New York', region: 'NY', country: 'United States' },
  { name: 'London, UK', lat: 51.5074, lon: -0.1278, city: 'London', region: 'England', country: 'United Kingdom' },
  { name: 'Tokyo, Japan', lat: 35.6762, lon: 139.6503, city: 'Tokyo', region: 'Kanto', country: 'Japan' },
  { name: 'Sydney, Australia', lat: -33.8688, lon: 151.2093, city: 'Sydney', region: 'NSW', country: 'Australia' },
  { name: 'Dubai, UAE', lat: 25.2048, lon: 55.2708, city: 'Dubai', region: 'Dubai', country: 'UAE' },
  { name: 'Singapore', lat: 1.3521, lon: 103.8198, city: 'Singapore', region: 'Central', country: 'Singapore' },
];

interface LocationMapProps {
  locationData: LocationData | null;
  isLoading: boolean;
  cameraName?: string;
}

// Component to handle map center changes
const MapUpdater: React.FC<{ center: [number, number] }> = ({ center }) => {
  const map = useMap();
  
  useEffect(() => {
    map.flyTo(center, 13, { duration: 1.5 });
  }, [center, map]);
  
  return null;
};

const LocationMap: React.FC<LocationMapProps> = ({ 
  locationData, 
  isLoading,
  cameraName = "Camera 1"
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedExample, setSelectedExample] = useState<typeof EXAMPLE_LOCATIONS[0] | null>(null);

  // Get current display location (example or auto-detected)
  const currentLocation = selectedExample 
    ? { latitude: selectedExample.lat, longitude: selectedExample.lon, city: selectedExample.city, region: selectedExample.region, country: selectedExample.country }
    : locationData;

  const handleSelectExample = (loc: typeof EXAMPLE_LOCATIONS[0]) => {
    setSelectedExample(loc);
  };

  if (isLoading) {
    return (
      <Card className="bg-card/50 backdrop-blur-sm border-border/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary" />
            Camera Location Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] bg-muted/30 rounded-lg flex items-center justify-center">
            <div className="flex flex-col items-center gap-2 text-muted-foreground">
              <Navigation className="h-8 w-8 animate-pulse" />
              <span className="text-sm">Detecting location...</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!currentLocation?.latitude || !currentLocation?.longitude) {
    return (
      <Card className="bg-card/50 backdrop-blur-sm border-border/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary" />
            Camera Location Map
          </CardTitle>
          <div className="mt-3">
            <p className="text-xs text-muted-foreground mb-2">Quick locations:</p>
            <div className="flex flex-wrap gap-1.5">
              {EXAMPLE_LOCATIONS.map((loc) => (
                <Button
                  key={loc.name}
                  variant={selectedExample?.name === loc.name ? "default" : "outline"}
                  size="sm"
                  className="text-xs h-7 px-2"
                  onClick={() => handleSelectExample(loc)}
                >
                  {loc.city}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] bg-muted/30 rounded-lg flex items-center justify-center border border-dashed border-border/50">
            <div className="flex flex-col items-center gap-2 text-muted-foreground">
              <MapPin className="h-8 w-8" />
              <span className="text-sm">Select a location above or wait for auto-detection</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const center: [number, number] = [currentLocation.latitude, currentLocation.longitude];

  return (
    <Card className={`bg-card/50 backdrop-blur-sm border-border/50 ${isFullscreen ? 'fixed inset-4 z-50' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary" />
            Camera Location Map
          </CardTitle>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setIsFullscreen(!isFullscreen)}>
            <Maximize2 className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          {currentLocation.city}, {currentLocation.region}, {currentLocation.country}
        </p>
        
        {/* Example Locations */}
        <div className="mt-3">
          <p className="text-xs text-muted-foreground mb-2">Quick locations:</p>
          <div className="flex flex-wrap gap-1.5">
            {EXAMPLE_LOCATIONS.map((loc) => (
              <Button
                key={loc.name}
                variant={selectedExample?.name === loc.name ? "default" : "outline"}
                size="sm"
                className="text-xs h-7 px-2"
                onClick={() => handleSelectExample(loc)}
              >
                {loc.city}
              </Button>
            ))}
            {selectedExample && (
              <Button
                variant="ghost"
                size="sm"
                className="text-xs h-7 px-2 text-muted-foreground"
                onClick={() => setSelectedExample(null)}
              >
                Use Auto-detected
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className={`relative rounded-lg overflow-hidden ${isFullscreen ? 'h-[calc(100%-80px)]' : 'h-[300px]'}`}>
          <MapContainer
            center={center}
            zoom={13}
            className="h-full w-full rounded-lg"
            style={{ background: 'hsl(var(--muted))' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            <Marker position={center} icon={cameraIcon}>
              <Popup className="dark-popup">
                <div className="p-1">
                  <h3 className="font-bold text-sm text-foreground">{cameraName}</h3>
                  <p className="text-xs text-muted-foreground">{currentLocation.city}, {currentLocation.region}</p>
                  <p className="text-xs text-muted-foreground font-mono">{currentLocation.latitude.toFixed(4)}, {currentLocation.longitude.toFixed(4)}</p>
                </div>
              </Popup>
            </Marker>
            <MapUpdater center={center} />
          </MapContainer>
          <div className="absolute bottom-2 left-2 bg-background/80 backdrop-blur-sm rounded px-2 py-1 text-xs font-mono z-[1000]">
            {currentLocation.latitude.toFixed(4)}, {currentLocation.longitude.toFixed(4)}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LocationMap;