import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  MapPin, ArrowRight, Layers, Anchor, Truck, Beaker,
  Shield, Zap, Globe2, ChevronRight
} from 'lucide-react';

export const Landing = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/map');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] overflow-hidden">
      {/* Hero Section */}
      <div className="relative min-h-screen flex flex-col">
        {/* Background Image */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1720759043544-4d43459f3388?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MDV8MHwxfHNlYXJjaHw0fHxmdXR1cmlzdGljJTIwbG9naXN0aWNzJTIwd2FyZWhvdXNlJTIwZGFyayUyMG1vZGV8ZW58MHx8fHwxNzcxMzQ4NzAwfDA&ixlib=rb-4.1.0&q=85)'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050505]/80 to-[#050505]" />
        
        {/* Scanner Effect */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 via-transparent to-transparent h-1/3 animate-scan" />
        </div>

        {/* Nav */}
        <nav className="relative z-10 flex items-center justify-between p-6 lg:px-12">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-500 flex items-center justify-center">
              <MapPin className="w-6 h-6 text-white" />
            </div>
            <span className="font-heading text-2xl font-bold tracking-tight text-white uppercase">
              Coords
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/protocol" className="font-mono text-xs uppercase tracking-wider text-zinc-400 hover:text-white transition-colors">
              Protocol Lab
            </Link>
            <Button
              data-testid="nav-login-btn"
              onClick={handleGetStarted}
              variant="outline"
              className="font-mono uppercase text-xs tracking-wider border-zinc-700 hover:border-zinc-500"
            >
              {isAuthenticated ? 'Open Workspace' : 'Initialize'}
            </Button>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 flex-1 flex items-center px-6 lg:px-12">
          <div className="max-w-4xl">
            <Badge className="mb-6 bg-blue-500/10 text-blue-400 border-blue-500/30 font-mono text-xs uppercase">
              Phase 9 • Active Logistics Coordination
            </Badge>
            <h1 className="font-heading text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight text-white uppercase leading-[0.9] mb-6">
              Unified Spatial OS
              <br />
              <span className="text-zinc-500">for Enterprise Logistics</span>
            </h1>
            <p className="text-xl md:text-2xl text-zinc-400 max-w-2xl mb-8 leading-relaxed">
              Bridge immutable physical locations with human-friendly operational workflows.
              Open protocol. Enterprise runtime.
            </p>
            <div className="flex flex-wrap gap-4">
              <Button
                data-testid="hero-cta-btn"
                onClick={handleGetStarted}
                size="lg"
                className="bg-blue-500 hover:bg-blue-600 font-mono uppercase tracking-wider text-sm px-8"
              >
                Initialize Workspace
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button
                data-testid="protocol-lab-btn"
                onClick={() => navigate('/protocol')}
                variant="outline"
                size="lg"
                className="font-mono uppercase tracking-wider text-sm px-8 border-zinc-700"
              >
                <Beaker className="w-4 h-4 mr-2" />
                Protocol Lab
              </Button>
            </div>
          </div>
        </div>

        {/* Protocol Ticker */}
        <div className="relative z-10 border-t border-zinc-900 py-4 overflow-hidden">
          <div className="animate-marquee whitespace-nowrap font-mono text-xs text-zinc-600">
            coords:l1:v1:38.897700,-77.036500,0.00*a7b3c912 • @acme/warehouse/dock-1 • 
            coords:l1:v1:37.774900,-122.419400,15.25*1c86401e • @bridgeflow/terminal-a • 
            coords:l1:v1:48.856600,2.352200,35.40*ae6c07e1 • CC0 Protocol • MIT Runtime • 
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="py-24 px-6 lg:px-12">
        <div className="max-w-6xl mx-auto">
          <h2 className="font-heading text-3xl md:text-4xl font-bold tracking-tight text-white uppercase mb-4">
            Enterprise Runtime Features
          </h2>
          <p className="font-mono text-sm text-zinc-500 uppercase tracking-wider mb-12">
            Phase 9 • Active Logistics Coordination
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Layers className="w-6 h-6" />}
              title="Map Workspace"
              description="Interactive Leaflet map with dark basemap, real-time dock and carrier visualization."
            />
            <FeatureCard
              icon={<Anchor className="w-6 h-6" />}
              title="Dock Management"
              description="Live dock state tracking: available, occupied, maintenance, reserved. Assignment workflows."
            />
            <FeatureCard
              icon={<Truck className="w-6 h-6" />}
              title="Carrier Routing"
              description="Route planning with ETA and distance calculations. Waypoint resolution via L2 handles."
            />
            <FeatureCard
              icon={<Beaker className="w-6 h-6" />}
              title="Protocol Lab"
              description="Validate and generate L1 URIs. FNV-1a checksum verification against spec test vectors."
            />
            <FeatureCard
              icon={<Shield className="w-6 h-6" />}
              title="RBAC & Multi-tenancy"
              description="Role-based access control. Tenant-scoped data isolation. Enterprise security."
            />
            <FeatureCard
              icon={<Zap className="w-6 h-6" />}
              title="SLA Monitoring"
              description="Compliance analytics. Arrival alerts. Turnaround time tracking."
            />
          </div>
        </div>
      </section>

      {/* Protocol Section */}
      <section className="py-24 px-6 lg:px-12 bg-zinc-950/50 border-y border-zinc-900">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-emerald-500/10 text-emerald-400 border-emerald-500/30 font-mono text-xs uppercase">
                CC0 Public Domain
              </Badge>
              <h2 className="font-heading text-3xl md:text-4xl font-bold tracking-tight text-white uppercase mb-4">
                Open Protocol Foundation
              </h2>
              <p className="text-zinc-400 mb-6">
                L1 immutable spatial identifiers with FNV-1a checksums. L2 human-friendly handles.
                Anyone can implement. No vendor lock-in.
              </p>
              <div className="space-y-3">
                <ProtocolLine label="L1 Format" value="coords:l1:v1:<lat>,<lng>,<alt>*<checksum>" />
                <ProtocolLine label="L2 Handle" value="@<tenant>/<path>" />
                <ProtocolLine label="Checksum" value="FNV-1a 32-bit, lowercase hex" />
              </div>
            </div>
            <div className="terminal p-6">
              <div className="font-mono text-xs text-zinc-500 mb-2">// Example L1 URI</div>
              <code className="font-mono text-sm text-emerald-400 block break-all">
                coords:l1:v1:37.774900,-122.419400,15.25*1c86401e
              </code>
              <div className="font-mono text-xs text-zinc-500 mt-4 mb-2">// Canonical payload (for checksum)</div>
              <code className="font-mono text-sm text-blue-400 block">
                v1|37.774900|-122.419400|15.25
              </code>
              <div className="font-mono text-xs text-zinc-500 mt-4 mb-2">// L2 Handle</div>
              <code className="font-mono text-sm text-amber-400 block">
                @acme/warehouse/dock-1
              </code>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 lg:px-12">
        <div className="max-w-2xl mx-auto text-center">
          <Globe2 className="w-12 h-12 text-blue-500 mx-auto mb-6" />
          <h2 className="font-heading text-3xl md:text-4xl font-bold tracking-tight text-white uppercase mb-4">
            Ready to Coordinate?
          </h2>
          <p className="text-zinc-400 mb-8">
            Initialize your workspace and start coordinating logistics with precision spatial primitives.
          </p>
          <Button
            data-testid="footer-cta-btn"
            onClick={handleGetStarted}
            size="lg"
            className="bg-blue-500 hover:bg-blue-600 font-mono uppercase tracking-wider text-sm px-12"
          >
            Initialize Workspace
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-900 py-8 px-6 lg:px-12">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 bg-blue-500 flex items-center justify-center">
              <MapPin className="w-4 h-4 text-white" />
            </div>
            <span className="font-mono text-xs text-zinc-500">
              Coords • Unified Spatial OS • Phase 9
            </span>
          </div>
          <div className="flex items-center gap-6">
            <a href="https://github.com/coordsapp/spec" target="_blank" rel="noopener noreferrer" className="font-mono text-xs text-zinc-500 hover:text-white">
              Spec (CC0)
            </a>
            <a href="https://github.com/coordsapp/core" target="_blank" rel="noopener noreferrer" className="font-mono text-xs text-zinc-500 hover:text-white">
              Core (MIT)
            </a>
          </div>
        </div>
      </footer>

      {/* Marquee Animation Style */}
      <style>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
      `}</style>
    </div>
  );
};

const FeatureCard = ({ icon, title, description }) => (
  <div className="bg-zinc-900/50 border border-zinc-800 p-6 hover:border-zinc-700 transition-colors">
    <div className="text-blue-500 mb-4">{icon}</div>
    <h3 className="font-heading text-lg font-bold tracking-tight text-white uppercase mb-2">{title}</h3>
    <p className="text-sm text-zinc-400">{description}</p>
  </div>
);

const ProtocolLine = ({ label, value }) => (
  <div className="flex items-start gap-2">
    <span className="font-mono text-xs uppercase text-zinc-500 w-24 shrink-0">{label}</span>
    <code className="font-mono text-xs text-zinc-300">{value}</code>
  </div>
);

export default Landing;
