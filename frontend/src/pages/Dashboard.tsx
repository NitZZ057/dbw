import { ReactElement, useEffect, useState } from 'react';
import api from '../api/client';
import { AccidentChart } from '../components/AccidentChart';
import { Row } from '../types/api';
export function Dashboard(): ReactElement {
  const [coverage,setCoverage]=useState<Row[]>([]); const [chart,setChart]=useState<Row[]>([]);
  useEffect(()=>{ void Promise.all([api.get('/time/coverage'),api.get('/aggregates/accidents?level=state&year=2023')]).then(([a,b])=>{setCoverage(a.data.data);setChart(b.data.data);}); },[]);
  const years=coverage.flatMap(r=>[Number(r.earliest_year),Number(r.latest_year)]);
  return <main><h1>Road safety, made queryable.</h1><div className="stats"><article><b>{chart.reduce((n,r)=>n+Number(r.accident_count),0)}</b>Total accidents</article><article><b>{coverage.length}</b>States covered</article><article><b>{years.length?Math.min(...years):'—'}</b>Earliest year</article><article><b>{years.length?Math.max(...years):'—'}</b>Latest year</article></div><section><h2>Accidents by state · 2023</h2><AccidentChart data={chart}/></section></main>;
}
