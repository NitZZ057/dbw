import { ReactElement, useEffect, useState } from 'react';
import api from '../api/client';
import { ResultsTable } from '../components/ResultsTable';
import { Row } from '../types/api';
export function Provenance(): ReactElement { const [rows,setRows]=useState<Row[]>([]); useEffect(()=>{void api.get('/metadata/sources').then(r=>setRows(r.data.data));},[]); return <main><h1>Data provenance</h1><p>Every answer retains its source, license, retrieval time, and checksum.</p><ResultsTable rows={rows}/></main>; }
