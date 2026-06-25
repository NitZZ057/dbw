import { NavLink, Route, Routes } from 'react-router-dom';
import type { ReactElement } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Dashboard } from './pages/Dashboard';
import { Explorer } from './pages/Explorer';
import { Provenance } from './pages/Provenance';

export function App(): ReactElement {
	return (
		<div className="app-layout">
			<aside className="sidebar">
				<div className="brand">
					<strong>ACCIDENT ANALYTICS</strong>
					<select className="sidebar-select" defaultValue="2023" aria-label="Select year">
						<option value="2023">2023</option>
						<option value="2022">2022</option>
						<option value="2021">2021</option>
					</select>
				</div>
				<nav className="nav-links">
					<NavLink to="/" className={({ isActive }) => isActive ? 'active-tab' : ''}>Dashboard</NavLink>
					<NavLink to="/explorer" className={({ isActive }) => isActive ? 'active-tab' : ''}>Accident Explorer</NavLink>
					<NavLink to="/provenance" className={({ isActive }) => isActive ? 'active-tab' : ''}>Metadata</NavLink>
				</nav>
				<div className="sidebar-footer">Dark Mode</div>
			</aside>

			<div className="content-wrap">
				<div className="top-banner">ACCIDENT ANALYTICS PLATFORM – FRONTEND UI & API MAPPING</div>
				<ErrorBoundary>
					<Routes>
						<Route path="/" element={<Dashboard />} />
						<Route path="/explorer" element={<Explorer />} />
						<Route path="/provenance" element={<Provenance />} />
					</Routes>
				</ErrorBoundary>
			</div>
		</div>
	);
}
