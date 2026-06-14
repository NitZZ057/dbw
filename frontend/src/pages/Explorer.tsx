import { ReactElement, useState } from 'react';
import api from '../api/client';
import { Query, QueryPanel } from '../components/QueryPanel';
import { ResultsTable } from '../components/ResultsTable';
import { SourceMetadata } from '../components/SourceMetadata';
import { Row } from '../types/api';
export function Explorer(): ReactElement {
  const [rows,setRows]=useState<Row[]>([]); const [meta,setMeta]=useState({license:'',sources:[] as string[]});
  const run=async(q:Query)=>{let path=q.type==='rates'?`/aggregates/rates?year=${q.year}&level=district`:q.type==='coverage'?'/time/coverage':`/accidents/count?year=${q.year}${q.state?`&state_ags=${q.state}`:''}${q.category?`&category=${q.category}`:''}${q.type==='pedestrian'?'&ist_fuss=true':''}`; const response=await api.get(path); setRows(Array.isArray(response.data.data)?response.data.data:[response.data.data]); setMeta(response.data);};
  return <main><h1>Query explorer</h1><QueryPanel run={run}/><ResultsTable rows={rows}/>{meta.license&&<SourceMetadata {...meta}/>}</main>;
}
