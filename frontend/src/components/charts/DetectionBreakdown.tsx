import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface Props {
  stats: {
    critical_alerts: number;
    high_alerts: number;
    medium_alerts: number;
    low_alerts: number;
  };
}

const COLORS = ['#f43f5e', '#f59e0b', '#6366f1', '#10b981'];

export default function DetectionBreakdown({ stats }: Props) {
  const data = [
    { name: 'Critical', value: stats.critical_alerts || 0 },
    { name: 'High', value: stats.high_alerts || 0 },
    { name: 'Medium', value: stats.medium_alerts || 0 },
    { name: 'Low', value: stats.low_alerts || 0 },
  ].filter((d) => d.value > 0);

  if (data.length === 0) {
    data.push({ name: 'No Data', value: 1 });
  }

  return (
    <div className="chart-card animate-in">
      <div className="chart-card__header">
        <h3 className="chart-card__title">Alert Breakdown</h3>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={65}
            outerRadius={100}
            paddingAngle={4}
            dataKey="value"
            stroke="none"
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: '#1a2035',
              border: '1px solid rgba(99,102,241,0.2)',
              borderRadius: '10px',
              color: '#f1f5f9',
              fontSize: '0.8rem',
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '0.8rem', color: '#94a3b8' }}
            formatter={(value) => <span style={{ color: '#94a3b8' }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
