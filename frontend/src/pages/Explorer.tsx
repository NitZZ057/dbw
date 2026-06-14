import { ReactElement, useRef, useState } from 'react';
import api from '../api/client';
import { Query, QueryPanel } from '../components/QueryPanel';
import { ResultsTable } from '../components/ResultsTable';
import { SourceMetadata } from '../components/SourceMetadata';
import { Row } from '../types/api';

type Preset = { label: string; query?: Query; endpoint?: string };
export function Explorer(): ReactElement {
  const [rows,setRows]=useState<Row[]>([]);
  const [meta,setMeta]=useState({license:'',sources:[] as string[]});

  const makeRows = (path: string, data: unknown): Row[] => {
    if (path.startsWith('/accidents/count')) {
      const payload = data as { count: number; filters_applied?: Record<string, unknown> };
      return [{
        count: new Intl.NumberFormat().format(payload.count),
        filters_applied: payload.filters_applied
          ? Object.entries(payload.filters_applied)
              .map(([k, v]) => `${k}: ${v}`)
              .join(' · ')
          : '—',
      }];
    }
    if (path.startsWith('/time/earliest')) {
      const payload = data as { earliest_year: number; scope: string };
      return [{ earliest_year: payload.earliest_year, scope: payload.scope }];
    }
    if (Array.isArray(data)) {
      return data as Row[];
    }
    return [{ result: data } as Row];
  };

  const run = async (q: Query) => {
    const path = q.type === 'rates'
      ? `/aggregates/rates?year=${q.year}&level=district&top_n=${q.top_n}`
      : q.type === 'coverage'
      ? '/time/coverage'
      : `/accidents/count?year=${q.year}${q.state ? `&state_ags=${q.state}` : ''}${q.category ? `&category=${q.category}` : ''}${q.type === 'pedestrian' ? '&ist_fuss=true' : ''}`;
    const response = await api.get(path);
    const data = response.data.data;
    setRows(makeRows(path, data));
    setMeta(response.data);
  };

  const runPreset = async (preset: Preset) => {
    if (preset.query) {
      await run(preset.query);
      return;
    }
    if (preset.endpoint) {
      const response = await api.get(preset.endpoint);
      const data = response.data.data;
      setRows(makeRows(preset.endpoint, data));
      setMeta(response.data);
    }
  };

  const presets: Preset[] = [
    { label: 'Earliest accident year', endpoint: '/time/earliest' },
    { label: 'Accidents in Saxony 2023', query: { type: 'count', state: '14', year: '2023', category: '', top_n: '10' } },
    { label: 'NRW data from year', endpoint: '/time/earliest?state_ags=05' },
    { label: 'MV data from year', endpoint: '/time/earliest?state_ags=13' },
    { label: 'Pedestrian accidents Berlin 2023', query: { type: 'pedestrian', state: '11', year: '2023', category: '', top_n: '10' } },
  ];

  const presetRowRef = useRef<HTMLDivElement | null>(null);

  const scrollPresets = (left: number) => {
    presetRowRef.current?.scrollBy({ left, behavior: 'smooth' });
  };

  return <main>
    <h1>Query explorer</h1>
    <QueryPanel run={run}/>
    <section className="panel" style={{ marginTop: '2rem', overflow: 'hidden', padding: 24 }}>
      <h2>Mandatory exam questions</h2>
      <div style={{ display: 'flex', marginTop: '1rem' }}>
        <div ref={presetRowRef} className="preset-scroll-container" style={{ minWidth: 0 }}>
          {presets.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => void runPreset(preset)}
              className="preset-button"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>
    </section>
    <ResultsTable rows={rows}/>
    {meta.license&&<SourceMetadata {...meta}/>}  
  </main>;
}
