import { useState } from 'react';
import { detectionApi } from '../api/detection';
import NetworkGraph from '../components/network/NetworkGraph';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function NetworkPage() {
  const [analysisId, setAnalysisId] = useState('');
  const [graphData, setGraphData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadGraph = async () => {
    if (!analysisId.trim()) return;
    setIsLoading(true);
    setError('');
    try {
      const res = await detectionApi.getNetworkGraph(analysisId.trim());
      setGraphData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load network graph. Run an analysis first.');
    }
    setIsLoading(false);
  };

  return (
    <div className="page">
      <div className="page__header">
        <h2 className="page__title">Network Visualization</h2>
        <p className="page__subtitle">
          Explore engagement networks to identify coordinated fake activity clusters
        </p>
      </div>

      <div className="chart-card" style={{ marginBottom: 'var(--space-lg)' }}>
        <div className="flex gap-md items-center">
          <input
            id="network-analysis-id"
            type="text"
            className="input-field"
            placeholder="Enter Analysis ID (from a completed analysis)"
            value={analysisId}
            onChange={(e) => setAnalysisId(e.target.value)}
            style={{ flex: 1 }}
          />
          <button
            id="load-graph-btn"
            className="btn btn-primary"
            onClick={loadGraph}
            disabled={isLoading}
          >
            {isLoading ? '⏳ Loading...' : '🕸️ Load Graph'}
          </button>
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: 'var(--space-sm)' }}>
          💡 Run an analysis from the Analysis page first, then paste the Analysis ID here
        </p>
      </div>

      {isLoading && <LoadingSpinner text="Building network graph..." />}

      {error && (
        <div className="chart-card" style={{ borderColor: 'rgba(244, 63, 94, 0.3)' }}>
          <p style={{ color: '#fb7185' }}>❌ {error}</p>
        </div>
      )}

      {graphData && (
        <div className="animate-in">
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 'var(--space-lg)' }}>
            <div className="stat-card">
              <span className="stat-card__label">Nodes (Users)</span>
              <span className="stat-card__value">{graphData.node_count || graphData.nodes?.length || 0}</span>
            </div>
            <div className="stat-card">
              <span className="stat-card__label">Edges (Interactions)</span>
              <span className="stat-card__value">{graphData.edge_count || graphData.edges?.length || 0}</span>
            </div>
            <div className="stat-card">
              <span className="stat-card__label">Suspicious Nodes</span>
              <span className="stat-card__value" style={{ color: 'var(--accent-rose)' }}>
                {graphData.nodes?.filter((n: any) => (n.suspicion_score || 0) >= 0.5).length || 0}
              </span>
            </div>
          </div>
          <NetworkGraph graphData={graphData} />
        </div>
      )}

      {!graphData && !isLoading && !error && (
        <div className="chart-card" style={{ textAlign: 'center', padding: '4rem' }}>
          <span style={{ fontSize: '4rem' }}>🕸️</span>
          <h3 style={{ color: 'var(--text-primary)', marginTop: 'var(--space-lg)', marginBottom: 'var(--space-sm)' }}>
            Network Visualization
          </h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto' }}>
            Run a threat analysis first, then load the network graph to visualize
            user interactions, detect clusters, and identify coordinated behavior.
          </p>
        </div>
      )}
    </div>
  );
}
