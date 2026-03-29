import { useEffect, useState } from 'react';
import { detectionApi } from '../api/detection';
import { alertsApi, type Alert } from '../api/alerts';
import StatCard from '../components/common/StatCard';
import EngagementTimeline from '../components/charts/EngagementTimeline';
import DetectionBreakdown from '../components/charts/DetectionBreakdown';
import AlertCard from '../components/alerts/AlertCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import type { DashboardStats } from '../api/detection';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setIsLoading(true);
    try {
      const [statsRes, timelineRes, alertsRes] = await Promise.all([
        detectionApi.getDashboardStats(),
        detectionApi.getDashboardTimeline(30),
        alertsApi.list({ page: 1 }),
      ]);
      setStats(statsRes.data);
      setTimeline(timelineRes.data.timeline || []);
      setRecentAlerts(alertsRes.data.alerts.slice(0, 5));
    } catch (err) {
      console.error('Dashboard load failed:', err);
    }
    setIsLoading(false);
  };

  if (isLoading) return <LoadingSpinner text="Loading dashboard..." />;

  return (
    <div className="page">
      <div className="page__header">
        <h2 className="page__title">Threat Overview</h2>
        <p className="page__subtitle">Real-time fake engagement monitoring and detection</p>
      </div>

      {/* Stats Row */}
      <div className="stats-grid">
        <StatCard
          icon="📊"
          label="Total Analyses"
          value={stats?.total_analyses || 0}
          color="rgba(99, 102, 241, 0.15)"
          delay={1}
        />
        <StatCard
          icon="🚨"
          label="Active Threats"
          value={stats?.active_threats || 0}
          color="rgba(244, 63, 94, 0.15)"
          delay={2}
        />
        <StatCard
          icon="🔔"
          label="Total Alerts"
          value={stats?.total_alerts || 0}
          color="rgba(245, 158, 11, 0.15)"
          delay={3}
        />
        <StatCard
          icon="🛡️"
          label="Avg. Threat Score"
          value={`${((stats?.avg_threat_score || 0) * 100).toFixed(0)}%`}
          color="rgba(16, 185, 129, 0.15)"
          delay={4}
        />
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        <EngagementTimeline data={timeline} />
        <DetectionBreakdown stats={stats || { critical_alerts: 0, high_alerts: 0, medium_alerts: 0, low_alerts: 0 }} />
      </div>

      {/* Recent Alerts */}
      <div className="chart-card animate-in">
        <div className="chart-card__header">
          <h3 className="chart-card__title">Recent Alerts</h3>
          <a href="/alerts" className="btn btn-ghost" style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}>
            View All →
          </a>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
          {recentAlerts.length > 0 ? (
            recentAlerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))
          ) : (
            <div className="loading-overlay" style={{ padding: 'var(--space-xl)' }}>
              <span style={{ fontSize: '2rem' }}>✨</span>
              <span>No alerts yet. Run an analysis to get started!</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
