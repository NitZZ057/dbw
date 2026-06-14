import { FormEvent, ReactElement, useState } from 'react';
export type Query = {type: string; state: string; year: string; category: string};
export function QueryPanel({ run }: {run: (query: Query) => void}): ReactElement {
  const [query, setQuery] = useState<Query>({type:'count', state:'', year:'2023', category:''});
  const submit = (event: FormEvent) => { event.preventDefault(); run(query); };
  return <form onSubmit={submit} className="panel"><label>Query<select value={query.type} onChange={e=>setQuery({...query,type:e.target.value})}><option value="count">Count accidents</option><option value="rates">Accident rate by district</option><option value="coverage">Year coverage</option><option value="pedestrian">Pedestrian accidents</option></select></label><label>State AGS<input value={query.state} onChange={e=>setQuery({...query,state:e.target.value})}/></label><label>Year<input type="number" value={query.year} onChange={e=>setQuery({...query,year:e.target.value})}/></label><label>Category<input value={query.category} onChange={e=>setQuery({...query,category:e.target.value})}/></label><button>Run query</button></form>;
}
