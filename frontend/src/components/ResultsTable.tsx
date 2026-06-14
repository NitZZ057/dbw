import { Row } from '../types/api';
import type { ReactElement } from 'react';
export function ResultsTable({ rows }: {rows: Row[]}): ReactElement {
  const keys = rows.length ? Object.keys(rows[0]) : [];
  return <div className="table-wrap"><table><thead><tr>{keys.map(k => <th key={k}>{k}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{keys.map(k => <td key={k}>{String(row[k] ?? '')}</td>)}</tr>)}</tbody></table></div>;
}
