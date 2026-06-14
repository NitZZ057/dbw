import { NavLink, Route, Routes } from 'react-router-dom';
import type { ReactElement } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Dashboard } from './pages/Dashboard'; import { Explorer } from './pages/Explorer'; import { Provenance } from './pages/Provenance';
export function App(): ReactElement { return <><nav><strong>UnfallAtlas</strong><NavLink to="/" className={({ isActive }) => isActive ? 'active-tab' : ''}>Dashboard</NavLink><NavLink to="/explorer" className={({ isActive }) => isActive ? 'active-tab' : ''}>Explorer</NavLink><NavLink to="/provenance" className={({ isActive }) => isActive ? 'active-tab' : ''}>Provenance</NavLink></nav><ErrorBoundary><Routes><Route path="/" element={<Dashboard/>}/><Route path="/explorer" element={<Explorer/>}/><Route path="/provenance" element={<Provenance/>}/></Routes></ErrorBoundary></>; }
