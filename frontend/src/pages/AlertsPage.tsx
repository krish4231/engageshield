import { useEffect, useState } from 'react';
import { alertsApi, type Alert } from '../api/alerts';
import AlertCard from '../components/alerts/AlertCard';
import Badge from '../components/common/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [severity, setSeverity] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    loadAlerts();
  }, [page, severity]);

  const loadAlerts = async () => {
    setIsLoading(true);
    try {
      const res = await alertsApi.list({
        page,
        severity: severity || undefined,
      });
      setAlerts(res.data.alerts);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
    setIsLoading(false);
  };

  const handleResolve = async (id: string) => {
    try {
      await alertsApi.update(id, { is_resolved: true });
      loadAlerts();
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    }
  };

  return (
    <div className="page">
      <div className="page__header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 className="page__title">Alert Center</h2>
          <p className="page__subtitle">{total} total alerts</p>
        </div>
        <div className="flex gap-sm">
          {['', 'critical', 'high', 'medium', 'low'].map((s) => (
            <button
              key={s}
              className={`btn ${severity === s ? 'btn-primary' : 'btn-ghost'}`}
              style={{ fontSize: '0.75rem', padding: '0.4rem 0.7rem' }}
              onClick={() => { setSeverity(s); setPage(1); }}
            >
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner text="Loading alerts..." />
      ) : alerts.length === 0 ? (
        <div className="chart-card" style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
          <span style={{ fontSize: '3rem' }}>🎉</span>
          <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-md)' }}>No alerts found</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
          {alerts.map((alert) => (
            <div key={alert.id}>
              <AlertCard
                alert={alert}
                onClick={() => setExpandedId(expandedId === alert.id ? null : alert.id)}
              />
              {expandedId === alert.id && (
                <div className="chart-card animate-in" style={{
                  marginTop: '2px',
                  borderTopLeftRadius: 0,
                  borderTopRightRadius: 0,
                  borderTop: 'none',
                }}>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
                    {alert.description}
                  </p>
                  <div className="flex gap-md items-center">
                    <Badge severity={alert.severity} />
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                      Category: {alert.category.replace(/_/g, ' ')}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                      Score: {(alert.threat_score * 100).toFixed(0)}%
                    </span>
                    {!alert.is_resolved && (
                      <button
                        className="btn btn-ghost"
                        style={{ marginLeft: 'auto', fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                        onClick={(e) => { e.stopPropagation(); handleResolve(alert.id); }}
                      >
                        ✅ Resolve
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 20 && (
        <div className="flex items-center justify-between mt-lg">
          <button
            className="btn btn-ghost"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            ← Previous
          </button>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Page {page} of {Math.ceil(total / 20)}
          </span>
          <button
            className="btn btn-ghost"
            disabled={page * 20 >= total}
            onClick={() => setPage(page + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
