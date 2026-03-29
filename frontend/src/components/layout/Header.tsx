import { useAuthStore } from '../../stores/authStore';
import { useAlertStore } from '../../stores/alertStore';
import { useLocation } from 'react-router-dom';

const PAGE_TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/analysis': 'Threat Analysis',
  '/alerts': 'Alert Center',
  '/network': 'Network Graph',
};

export default function Header() {
  const { user, logout } = useAuthStore();
  const unreadCount = useAlertStore((s) => s.unreadCount);
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] || 'EngageShield';

  return (
    <header className="header">
      <h1 className="header__title">{title}</h1>
      <div className="header__actions">
        <div className="header__notification">
          🔔
          {unreadCount > 0 && (
            <span className="header__notification-badge">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </div>
        <div className="header__user" onClick={logout} title="Click to logout">
          <div className="header__avatar">
            {user?.username?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            {user?.username || 'User'}
          </span>
        </div>
      </div>
    </header>
  );
}
