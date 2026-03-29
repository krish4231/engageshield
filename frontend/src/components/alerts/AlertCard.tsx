import Badge from '../common/Badge';
import type { Alert } from '../../api/alerts';

interface Props {
  alert: Alert;
  onClick?: () => void;
}

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const secondsAgo = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (secondsAgo < 60) return `${secondsAgo}s ago`;
  if (secondsAgo < 3600) return `${Math.floor(secondsAgo / 60)}m ago`;
  if (secondsAgo < 86400) return `${Math.floor(secondsAgo / 3600)}h ago`;
  return `${Math.floor(secondsAgo / 86400)}d ago`;
}

export default function AlertCard({ alert, onClick }: Props) {
  return (
    <div className="alert-card" onClick={onClick} id={`alert-${alert.id}`}>
      <div className={`alert-card__indicator ${alert.severity}`} />
      <div className="alert-card__content">
        <div className="flex items-center justify-between">
          <span className="alert-card__title">{alert.title}</span>
          <Badge severity={alert.severity} />
        </div>
        <p className="alert-card__description">
          {alert.description.length > 150
            ? alert.description.slice(0, 150) + '...'
            : alert.description}
        </p>
        <div className="alert-card__meta">
          <span>Score: {(alert.threat_score * 100).toFixed(0)}%</span>
          <span>•</span>
          <span>{alert.category.replace(/_/g, ' ')}</span>
          <span>•</span>
          <span>{timeAgo(alert.created_at)}</span>
        </div>
      </div>
    </div>
  );
}
