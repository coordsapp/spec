import { useState } from 'react';
import { protocolAPI } from '../../lib/api';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import {
  CheckCircle2, XCircle, Copy, ArrowRight, Beaker, Hash,
  MapPin, ChevronDown, ChevronUp
} from 'lucide-react';

export const ProtocolLab = () => {
  const [mode, setMode] = useState('validate'); // validate | generate
  const [l1Input, setL1Input] = useState('');
  const [coords, setCoords] = useState({ lat: '', lng: '', alt: '0' });
  const [result, setResult] = useState(null);
  const [testVectors, setTestVectors] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showVectors, setShowVectors] = useState(false);

  const handleValidate = async () => {
    if (!l1Input.trim()) return;
    setLoading(true);
    try {
      const response = await protocolAPI.validate(l1Input.trim());
      setResult({ type: 'validate', data: response.data });
    } catch (err) {
      setResult({ type: 'error', message: err.response?.data?.detail || 'Validation failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    const lat = parseFloat(coords.lat);
    const lng = parseFloat(coords.lng);
    const alt = parseFloat(coords.alt) || 0;
    
    if (isNaN(lat) || isNaN(lng)) {
      setResult({ type: 'error', message: 'Invalid coordinates' });
      return;
    }
    
    setLoading(true);
    try {
      const response = await protocolAPI.generate(lat, lng, alt);
      setResult({ type: 'generate', data: response.data });
    } catch (err) {
      setResult({ type: 'error', message: err.response?.data?.detail || 'Generation failed' });
    } finally {
      setLoading(false);
    }
  };

  const loadTestVectors = async () => {
    try {
      const response = await protocolAPI.testVectors();
      setTestVectors(response.data);
      setShowVectors(true);
    } catch (err) {
      console.error('Failed to load test vectors:', err);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div data-testid="protocol-lab" className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Beaker className="w-6 h-6 text-emerald-500" />
            <h1 className="font-heading text-3xl font-bold tracking-tight text-white uppercase">
              Protocol Lab
            </h1>
          </div>
          <p className="font-mono text-sm text-zinc-500">
            Coords v1 L1 URI validation and generation &mdash; spec-compliant
          </p>
        </div>

        {/* Mode Tabs */}
        <div className="flex gap-2 mb-6">
          <Button
            data-testid="mode-validate-btn"
            variant={mode === 'validate' ? 'default' : 'outline'}
            onClick={() => { setMode('validate'); setResult(null); }}
            className="font-mono uppercase text-xs"
          >
            <CheckCircle2 className="w-4 h-4 mr-2" />
            Validate L1
          </Button>
          <Button
            data-testid="mode-generate-btn"
            variant={mode === 'generate' ? 'default' : 'outline'}
            onClick={() => { setMode('generate'); setResult(null); }}
            className="font-mono uppercase text-xs"
          >
            <Hash className="w-4 h-4 mr-2" />
            Generate L1
          </Button>
          <Button
            data-testid="test-vectors-btn"
            variant="ghost"
            onClick={loadTestVectors}
            className="font-mono uppercase text-xs ml-auto"
          >
            Test Vectors
          </Button>
        </div>

        {/* Main Panel */}
        <div className="terminal p-6 mb-6">
          {mode === 'validate' ? (
            <div>
              <Label className="font-mono text-xs uppercase text-emerald-500 mb-2 block">
                L1 URI Input
              </Label>
              <div className="flex gap-2">
                <Input
                  data-testid="l1-validate-input"
                  value={l1Input}
                  onChange={(e) => setL1Input(e.target.value)}
                  placeholder="coords:l1:v1:37.774900,-122.419400,15.25*1c86401e"
                  className="flex-1 bg-black border-zinc-800 font-mono text-sm text-emerald-400 placeholder:text-zinc-700"
                />
                <Button
                  data-testid="validate-btn"
                  onClick={handleValidate}
                  disabled={loading}
                  className="bg-emerald-600 hover:bg-emerald-700 font-mono uppercase text-xs"
                >
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
              <p className="font-mono text-[10px] text-zinc-600 mt-2">
                Format: coords:l1:v1:&lt;lat&gt;,&lt;lng&gt;,&lt;alt&gt;*&lt;checksum&gt;
              </p>
            </div>
          ) : (
            <div>
              <Label className="font-mono text-xs uppercase text-blue-500 mb-2 block">
                Coordinate Input
              </Label>
              <div className="grid grid-cols-4 gap-2">
                <div>
                  <Label className="font-mono text-[10px] text-zinc-500">Latitude</Label>
                  <Input
                    data-testid="lat-input"
                    value={coords.lat}
                    onChange={(e) => setCoords({ ...coords, lat: e.target.value })}
                    placeholder="37.774900"
                    className="bg-black border-zinc-800 font-mono text-sm"
                  />
                </div>
                <div>
                  <Label className="font-mono text-[10px] text-zinc-500">Longitude</Label>
                  <Input
                    data-testid="lng-input"
                    value={coords.lng}
                    onChange={(e) => setCoords({ ...coords, lng: e.target.value })}
                    placeholder="-122.419400"
                    className="bg-black border-zinc-800 font-mono text-sm"
                  />
                </div>
                <div>
                  <Label className="font-mono text-[10px] text-zinc-500">Altitude (m)</Label>
                  <Input
                    data-testid="alt-input"
                    value={coords.alt}
                    onChange={(e) => setCoords({ ...coords, alt: e.target.value })}
                    placeholder="0.00"
                    className="bg-black border-zinc-800 font-mono text-sm"
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    data-testid="generate-btn"
                    onClick={handleGenerate}
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 font-mono uppercase text-xs"
                  >
                    Generate
                  </Button>
                </div>
              </div>
              <p className="font-mono text-[10px] text-zinc-600 mt-2">
                Precision: lat/lng = 6 decimals, alt = 2 decimals (required per spec)
              </p>
            </div>
          )}
        </div>

        {/* Result Panel */}
        {result && (
          <div className={`terminal p-6 mb-6 border-l-4 ${
            result.type === 'error' ? 'border-red-500' :
            result.type === 'validate' && result.data.valid && result.data.checksum_valid ? 'border-emerald-500' :
            result.type === 'validate' && result.data.valid && !result.data.checksum_valid ? 'border-amber-500' :
            result.type === 'validate' && !result.data.valid ? 'border-red-500' :
            'border-blue-500'
          }`}>
            {result.type === 'error' ? (
              <div className="flex items-center gap-2 text-red-400">
                <XCircle className="w-5 h-5" />
                <span className="font-mono text-sm">{result.message}</span>
              </div>
            ) : result.type === 'validate' ? (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  {result.data.valid ? (
                    result.data.checksum_valid ? (
                      <><CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      <span className="font-mono text-sm text-emerald-400">VALID - Checksum verified</span></>
                    ) : (
                      <><XCircle className="w-5 h-5 text-amber-500" />
                      <span className="font-mono text-sm text-amber-400">PARSED - Checksum mismatch</span></>
                    )
                  ) : (
                    <><XCircle className="w-5 h-5 text-red-500" />
                    <span className="font-mono text-sm text-red-400">INVALID - {result.data.error}</span></>
                  )}
                </div>
                {result.data.valid && (
                  <div className="grid grid-cols-2 gap-4">
                    <ResultRow label="Latitude" value={result.data.lat} />
                    <ResultRow label="Longitude" value={result.data.lng} />
                    <ResultRow label="Altitude" value={result.data.altitude} />
                    <ResultRow label="Checksum" value={result.data.checksum} highlight={result.data.checksum_valid} />
                  </div>
                )}
              </div>
            ) : result.type === 'generate' ? (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle2 className="w-5 h-5 text-blue-500" />
                  <span className="font-mono text-sm text-blue-400">L1 Generated</span>
                </div>
                <div className="bg-black p-3 mb-4 flex items-center justify-between">
                  <code className="font-mono text-sm text-emerald-400 break-all">
                    {result.data.l1}
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(result.data.l1)}
                    className="ml-2 shrink-0"
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <ResultRow label="Canonical Payload" value={result.data.canonical_payload} />
                  <ResultRow label="Checksum" value={result.data.checksum} />
                  <ResultRow label="3-Word Code" value={result.data.words} />
                </div>
              </div>
            ) : null}
          </div>
        )}

        {/* Test Vectors Panel */}
        {showVectors && testVectors && (
          <div className="terminal p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Badge variant={testVectors.spec_compliant ? 'default' : 'destructive'}
                  className={testVectors.spec_compliant ? 'bg-emerald-600' : ''}>
                  {testVectors.spec_compliant ? 'SPEC COMPLIANT' : 'NON-COMPLIANT'}
                </Badge>
                <span className="font-mono text-xs text-zinc-500">
                  {testVectors.vectors.length} test vectors
                </span>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowVectors(false)}>
                {showVectors ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>
            </div>
            <ScrollArea className="h-64">
              <div className="space-y-3">
                {testVectors.vectors.map((v, i) => (
                  <div key={i} className={`p-3 border ${
                    v.checksum_pass && v.uri_pass ? 'border-emerald-800 bg-emerald-950/20' : 'border-red-800 bg-red-950/20'
                  }`}>
                    <div className="flex items-center gap-2 mb-2">
                      {v.checksum_pass && v.uri_pass ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                      <span className="font-mono text-xs">{v.input}</span>
                    </div>
                    <code className="font-mono text-[10px] text-zinc-500 block break-all">
                      {v.expected_uri}
                    </code>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* Spec Reference */}
        <div className="mt-8 text-center">
          <p className="font-mono text-xs text-zinc-600">
            Spec: <a href="https://github.com/coordsapp/spec" className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">
              github.com/coordsapp/spec
            </a> (CC0 Public Domain)
          </p>
        </div>
      </div>
    </div>
  );
};

const ResultRow = ({ label, value, highlight }) => (
  <div>
    <span className="font-mono text-[10px] uppercase text-zinc-500 block">{label}</span>
    <span className={`font-mono text-sm ${highlight ? 'text-emerald-400' : highlight === false ? 'text-red-400' : 'text-white'}`}>
      {value ?? '-'}
    </span>
  </div>
);

export default ProtocolLab;
