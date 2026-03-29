interface StatCardProps {
  icon: string;
  label: string;
  value: string | number;
  trend?: string;
  trendDirection?: 'up' | 'down';
  color?: string;
  delay?: number;
}

export default function StatCard({ icon, label, value, trend, trendDirection, color, delay = 0 }: StatCardProps) {
  return (
    <div className={`stat-card animate-in animate-in-delay-${delay}`}>
      <div
        className="stat-card__icon"
        style={{ background: color || 'rgba(99, 102, 241, 0.15)' }}
      >
        {icon}
      </div>
      <span className="stat-card__label">{label}</span>
      <span className="stat-card__value">{value}</span>
      {trend && (
        <span className={`stat-card__trend ${trendDirection || ''}`}>
          {trendDirection === 'up' ? '↑' : trendDirection === 'down' ? '↓' : ''}
          {trend}
        </span>
      )}
    </div>
  );
}
