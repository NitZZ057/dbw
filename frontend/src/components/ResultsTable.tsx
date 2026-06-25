import { Row } from '../types/api';
import type { ReactElement } from 'react';
export function ResultsTable({ rows }: { rows: Row[] }): ReactElement {
  const keys = rows.length ? Object.keys(rows[0]) : [];
  const renderCell = (val: unknown): string => {
    if (val === null || val === undefined) return '—';
    if (typeof val === 'object') return JSON.stringify(val);
    return String(val);
  };
  return <div className="table-wrap"><table><thead><tr>{keys.map(k => <th key={k}>{k}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{keys.map(k => <td key={k}>{renderCell(row[k])}</td>)}</tr>)}</tbody></table></div>;
}
