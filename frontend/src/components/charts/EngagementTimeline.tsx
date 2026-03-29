import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface Props {
  data: Array<{ date: string; engagements: number; threats: number; threat_score: number }>;
}

export default function EngagementTimeline({ data }: Props) {
  return (
    <div className="chart-card animate-in">
      <div className="chart-card__header">
        <h3 className="chart-card__title">Engagement & Threat Timeline</h3>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="grad-engagements" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="grad-threats" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#f43f5e" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickFormatter={(v) => v.slice(5)}
            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 11 }}
            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
          />
          <Tooltip
            contentStyle={{
              background: '#1a2035',
              border: '1px solid rgba(99,102,241,0.2)',
              borderRadius: '10px',
              color: '#f1f5f9',
              fontSize: '0.8rem',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '0.8rem', color: '#94a3b8' }} />
          <Area type="monotone" dataKey="engagements" name="Engagements" stroke="#6366f1" fill="url(#grad-engagements)" strokeWidth={2} />
          <Area type="monotone" dataKey="threats" name="Threats" stroke="#f43f5e" fill="url(#grad-threats)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
