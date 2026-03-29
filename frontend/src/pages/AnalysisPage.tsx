import { useState, type FormEvent } from 'react';
import { detectionApi, type AnalyzeResponse } from '../api/detection';
import ThreatGauge from '../components/charts/ThreatGauge';
import Badge from '../components/common/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function AnalysisPage() {
  const [target, setTarget] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (e: FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return;
    setIsAnalyzing(true);
    setError('');
    setResult(null);

    try {
      const res = await detectionApi.analyze({ target_identifier: target.trim() });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed');
    }
    setIsAnalyzing(false);
  };

  return (
    <div className="page">
      <div className="page__header">
        <h2 className="page__title">Threat Analysis</h2>
        <p className="page__subtitle">Analyze accounts for fake engagement patterns</p>
      </div>

      {/* Analysis Form */}
      <div className="chart-card animate-in" style={{ marginBottom: 'var(--space-xl)' }}>
        <form onSubmit={handleAnalyze} className="flex gap-md items-center">
          <input
            id="analysis-target"
            type="text"
            className="input-field"
            placeholder="Enter target identifier (e.g., target_0001)"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            style={{ flex: 1 }}
          />
          <button
            id="analyze-btn"
            type="submit"
            className="btn btn-primary"
            disabled={isAnalyzing}
          >
            {isAnalyzing ? '⏳ Analyzing...' : '🔍 Analyze'}
          </button>
        </form>

        {/* Quick suggestions */}
        <div className="flex gap-sm mt-md" style={{ flexWrap: 'wrap' }}>
          {['target_0001', 'target_0010', 'target_0025'].map((t) => (
            <button
              key={t}
              className="btn btn-ghost"
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
              onClick={() => setTarget(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {isAnalyzing && <LoadingSpinner text="Running 4 detection engines..." />}

      {error && (
        <div className="chart-card" style={{ borderColor: 'rgba(244, 63, 94, 0.3)' }}>
          <p style={{ color: '#fb7185' }}>❌ {error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="animate-in">
          {/* Threat Overview */}
          <div className="stats-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr auto' }}>
            <div className="stat-card">
              <span className="stat-card__label">Status</span>
              <span className="stat-card__value" style={{ fontSize: '1.25rem' }}>
                <Badge severity={result.threat_level}>{result.threat_level}</Badge>
              </span>
            </div>
            <div className="stat-card">
              <span className="stat-card__label">Engagements</span>
              <span className="stat-card__value">{result.total_engagements}</span>
            </div>
            <div className="stat-card">
              <span className="stat-card__label">Unique Accounts</span>
              <span className="stat-card__value">{result.unique_accounts}</span>
            </div>
            <div className="stat-card" style={{ alignItems: 'center', justifyContent: 'center' }}>
              <ThreatGauge score={result.threat_score} level={result.threat_level} />
            </div>
          </div>

          {/* Engine Results */}
          <div className="two-col-grid" style={{ marginTop: 'var(--space-lg)' }}>
            {/* ML Result */}
            <div className="chart-card">
              <div className="chart-card__header">
                <h3 className="chart-card__title">🤖 ML Classification</h3>
                <Badge severity={
                  (result.ml_result?.score || 0) >= 0.7 ? 'critical' :
                  (result.ml_result?.score || 0) >= 0.4 ? 'high' : 'low'
                }>
                  {((result.ml_result?.score || 0) * 100).toFixed(0)}%
                </Badge>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
                Method: {result.ml_result?.method || 'N/A'} | Label: {result.ml_result?.label || 'N/A'}
              </p>
              {result.ml_result?.reasons?.length > 0 && (
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {result.ml_result.reasons.slice(0, 5).map((r: string, i: number) => (
                    <li key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', paddingLeft: '1rem', borderLeft: '2px solid var(--accent-primary)' }}>
                      {r}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Behavioral Result */}
            <div className="chart-card">
              <div className="chart-card__header">
                <h3 className="chart-card__title">📈 Behavioral Analysis</h3>
                <Badge severity={
                  (result.behavioral_result?.score || 0) >= 0.7 ? 'critical' :
                  (result.behavioral_result?.score || 0) >= 0.4 ? 'high' : 'low'
                }>
                  {((result.behavioral_result?.score || 0) * 100).toFixed(0)}%
                </Badge>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
                Bot-like: {result.behavioral_result?.is_bot_like ? '⚠️ Yes' : '✅ No'}
              </p>
              {result.behavioral_result?.anomalies?.length > 0 && (
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {result.behavioral_result.anomalies.slice(0, 5).map((a: any, i: number) => (
                    <li key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', paddingLeft: '1rem', borderLeft: '2px solid var(--accent-amber)' }}>
                      {a.description}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Graph Result */}
            <div className="chart-card">
              <div className="chart-card__header">
                <h3 className="chart-card__title">🕸️ Graph Analysis</h3>
                <Badge severity={
                  (result.graph_result?.score || 0) >= 0.7 ? 'critical' :
                  (result.graph_result?.score || 0) >= 0.4 ? 'high' : 'low'
                }>
                  {((result.graph_result?.score || 0) * 100).toFixed(0)}%
                </Badge>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Nodes: {result.graph_result?.graph_stats?.nodes || 0} | 
                Edges: {result.graph_result?.graph_stats?.edges || 0} | 
                Clusters: {result.graph_result?.clusters?.length || 0}
              </p>
            </div>

            {/* AI Insight */}
            <div className="insight-card">
              <div className="insight-card__header">
                <h3 className="chart-card__title">💡 AI Insight</h3>
                <Badge severity={result.insight?.severity || 'low'}>
                  {result.insight?.severity || 'low'}
                </Badge>
              </div>
              <p className="insight-card__text">
                {result.insight?.primary_insight || 'No insight generated'}
              </p>
              {result.insight?.recommendations && (
                <div style={{ marginTop: 'var(--space-md)' }}>
                  <h4 style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: 'var(--space-sm)', color: 'var(--text-primary)' }}>
                    Recommendations:
                  </h4>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {result.insight.recommendations.map((r: string, i: number) => (
                      <li key={i} style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)', paddingLeft: '1rem', borderLeft: '2px solid var(--accent-cyan)' }}>
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
