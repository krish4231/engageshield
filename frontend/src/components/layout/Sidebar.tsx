import { NavLink } from 'react-router-dom';

export default function Sidebar() {

  const links = [
    { to: '/', icon: '📊', label: 'Dashboard' },
    { to: '/analysis', icon: '🔍', label: 'Analysis' },
    { to: '/alerts', icon: '🚨', label: 'Alerts' },
    { to: '/network', icon: '🕸️', label: 'Network' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar__logo">
        <div className="sidebar__logo-icon">🛡️</div>
        <span className="sidebar__logo-text">EngageShield</span>
      </div>
      <nav className="sidebar__nav">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `sidebar__link ${isActive ? 'active' : ''}`
            }
            end={link.to === '/'}
          >
            <span className="sidebar__link-icon">{link.icon}</span>
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>
      <div style={{ padding: 'var(--space-lg)', borderTop: '1px solid var(--border-secondary)' }}>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>
          EngageShield v1.0
        </div>
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Fake Engagement Detection
        </div>
      </div>
    </aside>
  );
}
