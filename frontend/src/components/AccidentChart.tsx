import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { ReactElement } from 'react';
import { Row } from '../types/api';
export function AccidentChart({ data }: { data: Row[] }): ReactElement {
  return <ResponsiveContainer width="100%" height={420}><BarChart data={data} margin={{ bottom: 60 }}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="region_name" tick={{ angle: -35, textAnchor: 'end' }} interval={0} /><YAxis /><Tooltip /><Bar dataKey="accident_count" fill="#ef6c35" /></BarChart></ResponsiveContainer>;
}
