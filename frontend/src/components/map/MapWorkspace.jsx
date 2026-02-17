import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useAuth } from '../../context/AuthContext';
import { docksAPI, carriersAPI, analyticsAPI, protocolAPI } from '../../lib/api';
import { STATUS_COLORS, formatETA, formatDistance } from '../../lib/utils';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import {
  MapPin, Truck, Anchor, Layers, ChevronLeft, ChevronRight,
  RefreshCw, Plus, AlertTriangle, Clock, Target, Zap
} from 'lucide-react';

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom icons
const createDockIcon = (status) => {
  const colors = {
    available: '#10b981',
    occupied: '#ef4444',
    maintenance: '#f59e0b',
    reserved: '#3b82f6'
  };
  return L.divIcon({
    className: 'custom-dock-icon',
    html: `<div style="width:24px;height:24px;background:${colors[status] || '#71717a'};border:2px solid white;border-radius:4px;display:flex;align-items:center;justify-content:center;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
      </svg>
    </div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
};

const createCarrierIcon = (status) => {
  const colors = {
    enroute: '#3b82f6',
    arrived: '#10b981',
    loading: '#f59e0b',
    departed: '#71717a',
    delayed: '#ef4444'
  };
  return L.divIcon({
    className: 'custom-carrier-icon',
    html: `<div style="width:28px;height:28px;background:${colors[status] || '#3b82f6'};border:2px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
        <rect x="1" y="3" width="15" height="13" rx="2" ry="2"/>
        <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
        <circle cx="5.5" cy="18.5" r="2.5"/>
        <circle cx="18.5" cy="18.5" r="2.5"/>
      </svg>
    </div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
};

// Map Controls Component
const MapControls = ({ basemap, setBasemap }) => {
  const map = useMap();
  
  return (
    <div className="absolute top-4 right-4 z-[1000] glass p-2 space-y-2">
      <div className="flex flex-col gap-1">
        {['dark', 'streets', 'satellite'].map((type) => (
          <Button
            key={type}
            data-testid={`basemap-${type}-btn`}
            variant={basemap === type ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setBasemap(type)}
            className="font-mono text-xs uppercase justify-start"
          >
            <Layers className="w-3 h-3 mr-2" />
            {type}
          </Button>
        ))}
      </div>
    </div>
  );
};

// Click Handler for coordinates
const MapClickHandler = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      if (onMapClick) {
        onMapClick(e.latlng);
      }
    }
  });
  return null;
};

export const MapWorkspace = () => {
  const { user, logout } = useAuth();
  const [docks, setDocks] = useState([]);
  const [carriers, setCarriers] = useState([]);
  const [stats, setStats] = useState(null);
  const [basemap, setBasemap] = useState('dark');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [clickedCoords, setClickedCoords] = useState(null);

  const basemapUrls = {
    dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    streets: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [docksRes, carriersRes, statsRes] = await Promise.all([
        docksAPI.list(),
        carriersAPI.list(),
        analyticsAPI.dashboard()
      ]);
      setDocks(docksRes.data);
      setCarriers(carriersRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const handleMapClick = async (latlng) => {
    try {
      const response = await protocolAPI.generate(latlng.lat, latlng.lng, 0);
      setClickedCoords({
        lat: latlng.lat,
        lng: latlng.lng,
        l1: response.data.l1,
        words: response.data.words
      });
    } catch (err) {
      console.error('Failed to generate L1:', err);
    }
  };

  // Center on Washington DC (demo data location)
  const center = [38.9072, -77.0369];

  return (
    <div data-testid="map-workspace" className="h-screen w-screen bg-[#050505] flex overflow-hidden">
      {/* Sidebar */}
      <div className={`glass-subtle flex flex-col transition-all duration-300 ${sidebarOpen ? 'w-80' : 'w-0'}`}>
        {sidebarOpen && (
          <>
            {/* Header */}
            <div className="p-4 border-b border-zinc-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-blue-500 flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="font-heading text-lg font-bold tracking-tight text-white uppercase">Coords</h1>
                  <p className="font-mono text-[10px] text-zinc-500 uppercase">Control Tower</p>
                </div>
              </div>
              
              {/* Stats Bar */}
              {stats && (
                <div className="grid grid-cols-4 gap-2">
                  <StatBadge label="Docks" value={stats.total_docks} />
                  <StatBadge label="Avail" value={stats.available_docks} color="emerald" />
                  <StatBadge label="Active" value={stats.active_carriers} color="blue" />
                  <StatBadge label="SLA" value={`${stats.sla_compliance}%`} color="amber" />
                </div>
              )}
            </div>

            <ScrollArea className="flex-1">
              {/* Docks Section */}
              <div className="p-4 border-b border-zinc-800">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-mono text-xs uppercase tracking-wider text-zinc-400">
                    <Anchor className="w-3 h-3 inline mr-2" />Docks
                  </h2>
                  <Button variant="ghost" size="sm" onClick={fetchData}>
                    <RefreshCw className="w-3 h-3" />
                  </Button>
                </div>
                <div className="space-y-2">
                  {docks.map((dock) => (
                    <DockCard
                      key={dock.dock_id}
                      dock={dock}
                      selected={selectedEntity?.dock_id === dock.dock_id}
                      onClick={() => setSelectedEntity(dock)}
                    />
                  ))}
                </div>
              </div>

              {/* Carriers Section */}
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-mono text-xs uppercase tracking-wider text-zinc-400">
                    <Truck className="w-3 h-3 inline mr-2" />Carriers
                  </h2>
                </div>
                <div className="space-y-2">
                  {carriers.map((carrier) => (
                    <CarrierCard
                      key={carrier.carrier_id}
                      carrier={carrier}
                      selected={selectedEntity?.carrier_id === carrier.carrier_id}
                      onClick={() => setSelectedEntity(carrier)}
                    />
                  ))}
                </div>
              </div>
            </ScrollArea>

            {/* User Footer */}
            <div className="p-4 border-t border-zinc-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-zinc-700 flex items-center justify-center text-xs font-mono">
                    {user?.name?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <span className="text-xs text-zinc-400 font-mono truncate max-w-[120px]">
                    {user?.email}
                  </span>
                </div>
                <Button
                  data-testid="logout-btn"
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-zinc-500 hover:text-white"
                >
                  Exit
                </Button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Sidebar Toggle */}
      <button
        data-testid="sidebar-toggle-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="absolute left-0 top-1/2 -translate-y-1/2 z-[1001] w-6 h-12 bg-zinc-900 border border-zinc-700 flex items-center justify-center hover:bg-zinc-800 transition-all"
        style={{ left: sidebarOpen ? '320px' : '0' }}
      >
        {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      {/* Map */}
      <div className="flex-1 relative">
        <MapContainer
          center={center}
          zoom={15}
          className="w-full h-full"
          zoomControl={false}
        >
          <TileLayer
            url={basemapUrls[basemap]}
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          <MapControls basemap={basemap} setBasemap={setBasemap} />
          <MapClickHandler onMapClick={handleMapClick} />
          
          {/* Dock Markers */}
          {docks.map((dock) => (
            <Marker
              key={dock.dock_id}
              position={[dock.lat, dock.lng]}
              icon={createDockIcon(dock.status)}
              eventHandlers={{
                click: () => setSelectedEntity(dock)
              }}
            >
              <Popup className="coords-popup">
                <div className="font-mono text-xs">
                  <div className="font-bold mb-1">{dock.name}</div>
                  <div className="text-zinc-400">{dock.l2_handle || dock.l1_raw}</div>
                  <Badge className={`mt-2 ${STATUS_COLORS[dock.status]?.bg}`}>
                    {dock.status}
                  </Badge>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Carrier Markers */}
          {carriers.filter(c => c.current_lat && c.current_lng).map((carrier) => (
            <Marker
              key={carrier.carrier_id}
              position={[carrier.current_lat, carrier.current_lng]}
              icon={createCarrierIcon(carrier.status)}
              eventHandlers={{
                click: () => setSelectedEntity(carrier)
              }}
            >
              <Popup>
                <div className="font-mono text-xs">
                  <div className="font-bold mb-1">{carrier.code}</div>
                  <div className="text-zinc-400">{carrier.name}</div>
                  {carrier.eta_minutes && (
                    <div className="mt-1">ETA: {formatETA(carrier.eta_minutes)}</div>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Clicked Coordinates Display */}
        {clickedCoords && (
          <div className="absolute bottom-4 left-4 z-[1000] glass p-4 max-w-md">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs uppercase text-zinc-400">Generated L1</span>
              <button
                onClick={() => setClickedCoords(null)}
                className="text-zinc-500 hover:text-white"
              >
                ×
              </button>
            </div>
            <div className="font-mono text-xs break-all text-emerald-400 mb-2">
              {clickedCoords.l1}
            </div>
            <div className="flex gap-4 text-xs text-zinc-500">
              <span>Words: {clickedCoords.words}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Stat Badge Component
const StatBadge = ({ label, value, color = 'zinc' }) => {
  const colors = {
    zinc: 'text-zinc-400',
    emerald: 'text-emerald-400',
    blue: 'text-blue-400',
    amber: 'text-amber-400',
    red: 'text-red-400'
  };
  return (
    <div className="bg-zinc-900/50 p-2 text-center">
      <div className={`font-mono text-sm font-bold ${colors[color]}`}>{value}</div>
      <div className="font-mono text-[9px] uppercase text-zinc-600">{label}</div>
    </div>
  );
};

// Dock Card Component
const DockCard = ({ dock, selected, onClick }) => (
  <button
    data-testid={`dock-card-${dock.dock_id}`}
    onClick={onClick}
    className={`w-full text-left p-3 bg-zinc-900/50 border transition-all ${
      selected ? 'border-blue-500' : 'border-zinc-800 hover:border-zinc-700'
    }`}
  >
    <div className="flex items-center justify-between mb-1">
      <span className="font-mono text-sm font-medium text-white">{dock.name}</span>
      <div className={`w-2 h-2 rounded-full ${STATUS_COLORS[dock.status]?.bg}`} />
    </div>
    {dock.l2_handle && (
      <div className="font-mono text-[10px] text-zinc-500 truncate">{dock.l2_handle}</div>
    )}
    <div className="flex items-center gap-2 mt-2">
      <Badge variant="outline" className="font-mono text-[10px] uppercase">
        {dock.status}
      </Badge>
      {dock.turnaround_avg_mins && (
        <span className="font-mono text-[10px] text-zinc-500">
          <Clock className="w-3 h-3 inline mr-1" />
          {dock.turnaround_avg_mins}m avg
        </span>
      )}
    </div>
  </button>
);

// Carrier Card Component
const CarrierCard = ({ carrier, selected, onClick }) => (
  <button
    data-testid={`carrier-card-${carrier.carrier_id}`}
    onClick={onClick}
    className={`w-full text-left p-3 bg-zinc-900/50 border transition-all ${
      selected ? 'border-blue-500' : 'border-zinc-800 hover:border-zinc-700'
    }`}
  >
    <div className="flex items-center justify-between mb-1">
      <span className="font-mono text-sm font-medium text-white">{carrier.code}</span>
      <div className={`w-2 h-2 rounded-full ${STATUS_COLORS[carrier.status]?.bg}`} />
    </div>
    <div className="font-mono text-[10px] text-zinc-500">{carrier.name}</div>
    <div className="flex items-center gap-3 mt-2">
      <Badge variant="outline" className="font-mono text-[10px] uppercase">
        {carrier.status}
      </Badge>
      {carrier.eta_minutes && (
        <span className="font-mono text-[10px] text-blue-400">
          <Target className="w-3 h-3 inline mr-1" />
          ETA {formatETA(carrier.eta_minutes)}
        </span>
      )}
      {carrier.distance_km && (
        <span className="font-mono text-[10px] text-zinc-500">
          {formatDistance(carrier.distance_km)}
        </span>
      )}
    </div>
  </button>
);

export default MapWorkspace;
