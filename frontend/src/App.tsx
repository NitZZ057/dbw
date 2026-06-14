import { NavLink, Route, Routes } from 'react-router-dom';
import type { ReactElement } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Dashboard } from './pages/Dashboard'; import { Explorer } from './pages/Explorer'; import { Provenance } from './pages/Provenance';
import { Requirements } from "./pages/Requirements";
export function App(): ReactElement { return <><nav><strong>UnfallAtlas</strong><NavLink to="/">Dashboard</NavLink><NavLink to="/explorer">Explorer</NavLink><NavLink to="/provenance">Provenance</NavLink><NavLink to="/requirements">
  Requirements
</NavLink></nav><ErrorBoundary><Routes><Route path="/" element={<Dashboard/>}/><Route path="/explorer" element={<Explorer/>}/><Route path="/provenance" element={<Provenance/>}/><Route
  path="/requirements"
  element={<Requirements />}
/></Routes></ErrorBoundary></>; }
