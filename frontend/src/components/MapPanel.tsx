import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { ReactElement } from 'react';
import api from '../api/client';

type Pt = { lat: number; lng: number; id: number; region?: string; year?: number; month?: number };

export function MapPanel(): ReactElement {
  const [points, setPoints] = useState<Pt[]>([]);

  useEffect(() => {
    let mounted = true;
    void api.get('/accidents?page_size=500').then((res) => {
      if (!mounted) return;
      const rows = res.data.data as Array<Record<string, any>>;
      const pts = rows
        .filter((r) => r.lat != null && r.lon != null)
        .map((r) => ({ lat: Number(r.lat), lng: Number(r.lon), id: Number(r.accident_id), region: r.region_name, year: r.year, month: r.month }));
      setPoints(pts);
    }).catch(() => {
      // keep sample fallback if API fails
      setPoints([
        { lat: 52.52, lng: 13.405, id: 1, region: 'Berlin', year: 2023 },
        { lat: 48.1351, lng: 11.582, id: 2, region: 'Munich', year: 2023 },
        { lat: 53.5511, lng: 9.9937, id: 3, region: 'Hamburg', year: 2023 }
      ]);
    });
    return () => { mounted = false; };
  }, []);

  return (
    <div className="map-card">
      <div className="panel-header">
        <h2>Regional accident map</h2>
        <span className="api-tag">GET /accidents</span>
      </div>
      <MapContainer center={[51.1657, 10.4515]} zoom={6} style={{ height: 260, borderRadius: 12 }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {points.map((p) => (
          <CircleMarker
            key={p.id}
            center={[p.lat, p.lng]}
            radius={3.5}
            pathOptions={{ color: '#ef4444', fillOpacity: 0.8 }}
          >
            <Tooltip direction="top" offset={[0, -6]} opacity={0.95}>
              <div style={{ fontWeight: 700 }}>{p.region ?? 'Unknown'}</div>
              <div>Accident ID: {p.id}</div>
              <div>{p.year}/{p.month ?? ''}</div>
            </Tooltip>
            <Popup>
              <strong>{p.region ?? 'Unknown'}</strong>
              <div>Accident ID: {p.id}</div>
              <div>Date: {p.year}/{p.month ?? ''}</div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="map-legend">
        <div><span className="legend-dot high"></span>High</div>
        <div><span className="legend-dot medium"></span>Medium</div>
        <div><span className="legend-dot low"></span>Low</div>
      </div>
    </div>
  );
}
