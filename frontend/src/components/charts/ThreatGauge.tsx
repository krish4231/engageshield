interface Props {
  score: number;
  level: string;
}

const LEVEL_COLORS: Record<string, string> = {
  critical: '#f43f5e',
  high: '#f59e0b',
  medium: '#6366f1',
  low: '#10b981',
};

export default function ThreatGauge({ score, level }: Props) {
  const color = LEVEL_COLORS[level] || LEVEL_COLORS.medium;
  const pct = Math.round(score * 100);
  const circumference = 2 * Math.PI * 56;
  const offset = circumference - (score * circumference);

  return (
    <div className="threat-gauge">
      <div className="threat-gauge__circle">
        <svg width="140" height="140" viewBox="0 0 140 140" style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx="70" cy="70" r="56"
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="10"
          />
          <circle
            cx="70" cy="70" r="56"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease-out', filter: `drop-shadow(0 0 6px ${color}50)` }}
          />
        </svg>
        <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <span className="threat-gauge__value" style={{ color }}>{pct}%</span>
        </div>
      </div>
      <span className="threat-gauge__label" style={{ color }}>{level.toUpperCase()}</span>
    </div>
  );
}
