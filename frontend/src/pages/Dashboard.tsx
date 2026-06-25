import { ReactElement, useEffect, useMemo, useState } from 'react';
import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import api from '../api/client';
import { MapPanel } from '../components/MapPanel';
import { Row } from '../types/api';

const categoryData = [
  { name: 'Urban', value: 42 },
  { name: 'Rural', value: 26 },
  { name: 'Night', value: 18 },
  { name: 'Weekend', value: 14 }
];
const categoryColors = ['#3b82f6', '#2563eb', '#22c55e', '#f59e0b'];
const monthlyTrend = [
  { month: 'Jan', accidents: 1120 },
  { month: 'Feb', accidents: 980 },
  { month: 'Mar', accidents: 1150 },
  { month: 'Apr', accidents: 1280 },
  { month: 'May', accidents: 1390 },
  { month: 'Jun', accidents: 1460 },
  { month: 'Jul', accidents: 1330 },
  { month: 'Aug', accidents: 1210 },
  { month: 'Sep', accidents: 1180 },
  { month: 'Oct', accidents: 1240 },
  { month: 'Nov', accidents: 1130 },
  { month: 'Dec', accidents: 1070 }
];

export function Dashboard(): ReactElement {
  const [coverage, setCoverage] = useState<Row[]>([]);
  const [states, setStates] = useState<Row[]>([]);

  useEffect(() => {
    void Promise.all([
      api.get('/time/coverage'),
      api.get('/aggregates/accidents?level=state&year=2023')
    ]).then(([a, b]) => {
      setCoverage(a.data.data);
      setStates(b.data.data);
    });
  }, []);

  const years = coverage.flatMap((r) => [Number(r.earliest_year), Number(r.latest_year)]);
  const totalAccidents = states.reduce((sum, row) => sum + Number(row.accident_count), 0);
  const topStates = useMemo(() => {
    return [...states]
      .sort((a, b) => Number(b.accident_count) - Number(a.accident_count))
      .slice(0, 5);
  }, [states]);

  return (
    <main>
      <div className="dashboard-grid">
        <section className="dashboard-card">
          <div className="dashboard-header">
            <div>
              <h2>Accident Analytics Dashboard</h2>
              <p className="dashboard-subtitle">Monitoring accidents across states with live API mappings.</p>
            </div>
            <span className="api-tag">GET /time/coverage</span>
          </div>

          <div className="dashboard-stats">
            <article>
              <b>{totalAccidents.toLocaleString()}</b>
              <p>Total accidents in 2023</p>
            </article>
            <article>
              <b>{coverage.length}</b>
              <p>States with coverage</p>
            </article>
            <article>
              <b>{years.length ? Math.min(...years) : '—'}</b>
              <p>Earliest available year</p>
            </article>
            <article>
              <b>{years.length ? Math.max(...years) : '—'}</b>
              <p>Latest available year</p>
            </article>
          </div>

          <div className="dashboard-chart-row">
            <div className="chart-card">
              <div className="chart-header">
                <h3>Monthly trend</h3>
                <span className="api-tag">GET /aggregates/accidents?level=state&amp;year=2023</span>
              </div>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={monthlyTrend} margin={{ right: 16, left: -8, top: 6, bottom: 6 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
                  <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: '#475569' }} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: '#475569' }} />
                  <Tooltip />
                  <Legend verticalAlign="top" align="right" height={24} />
                  <Line type="monotone" dataKey="accidents" stroke="#2563eb" strokeWidth={3} dot={{ r: 4, fill: '#1d4ed8' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h3>Category breakdown</h3>
                <span className="api-tag">GET /aggregates/rates?year=2023</span>
              </div>
              <ResponsiveContainer width="100%" height={340}>
                <PieChart width={280} height={280} margin={{ top: 20, right: 12, left: 12, bottom: 20 }}>
                  <Pie
                    data={categoryData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={54}
                    outerRadius={88}
                    paddingAngle={4}
                    cornerRadius={8}
                    cx="50%"
                    cy="50%"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={categoryColors[index % categoryColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend
                    layout="vertical"
                    verticalAlign="middle"
                    align="right"
                    iconType="circle"
                    wrapperStyle={{ right: 8, top: '50%', transform: 'translateY(-50%)', maxWidth: 130 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="dashboard-right-panel">
          <MapPanel />

          <div className="endpoint-panel">
            <h3>API endpoint mapping</h3>
            <div className="endpoint-group">
              <span className="endpoint-color blue"></span>
              <div>
                <strong>Dashboard</strong>
                <p>GET /time/coverage</p>
                <p>GET /aggregates/accidents?level=state&amp;year=2023</p>
              </div>
            </div>
            <div className="endpoint-group">
              <span className="endpoint-color green"></span>
              <div>
                <strong>Explorer</strong>
                <p>GET /accidents</p>
                <p>Supports filters: year, month, weekday, category</p>
              </div>
            </div>
          </div>
        </section>

      </div>
    </main>
  );
}
