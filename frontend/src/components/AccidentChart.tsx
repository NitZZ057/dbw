import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { ReactElement } from 'react';
import { Row } from '../types/api';
export function AccidentChart({ data }: {data: Row[]}): ReactElement {
  return <ResponsiveContainer width="100%" height={360}><BarChart data={data}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="region_name"/><YAxis/><Tooltip/><Bar dataKey="accident_count" fill="#ef6c35"/></BarChart></ResponsiveContainer>;
}
