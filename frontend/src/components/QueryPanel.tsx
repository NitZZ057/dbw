import { FormEvent, ReactElement, useEffect, useState } from 'react';
import api from '../api/client';
export type Query = {type: string; state: string; year: string; category: string; top_n: string};
export function QueryPanel({ run }: {run: (query: Query) => void}): ReactElement {
  const [query, setQuery] = useState<Query>({type:'count', state:'', year:'2023', category:'', top_n:'10'});
  const [states, setStates] = useState<{region_name: string; ags: string; name: string}[]>([]);

  useEffect(() => {
    void (async () => {
      try {
        const response = await api.get('/regions?level=state');
        console.log('GET /regions?level=state response', response.data);
        const stateList = Array.isArray(response.data.data) ? response.data.data : [];
        setStates(stateList);
      } catch (error) {
        console.error('Failed to load state regions', error);
        setStates([]);
      }
    })();
  }, []);

  const submit = (event: FormEvent) => { event.preventDefault(); run(query); };

  return <form onSubmit={submit} className="panel"><label>Query<select value={query.type} onChange={e=>setQuery({...query,type:e.target.value})}><option value="count">Count accidents</option><option value="rates">Accident rate per 100k (cross-source)</option><option value="coverage">Year coverage</option><option value="pedestrian">Pedestrian accidents</option></select></label><label>State AGS<select value={query.state} onChange={e=>setQuery({...query,state:e.target.value})}><option value="">All states</option>{states.map(state => <option key={state.ags} value={state.ags}>{state.name}</option>)}</select></label><label>Year<input type="number" value={query.year} onChange={e=>setQuery({...query,year:e.target.value})}/></label>{query.type !== 'rates' ? <label>Category<input value={query.category} onChange={e=>setQuery({...query,category:e.target.value})}/></label> : <label>Top N<input type="number" value={query.top_n} min="1" onChange={e=>setQuery({...query,top_n:e.target.value})}/></label>}<button type="submit" className="run-button">Run query</button></form>;
}
