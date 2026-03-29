import api from './client';

export interface AnalyzeRequest { target_identifier: string; analysis_type?: string; }
export interface AnalyzeResponse {
  analysis_id: string;
  target: string;
  status: string;
  threat_score: number;
  threat_level: string;
  total_engagements: number;
  unique_accounts: number;
  ml_result?: any;
  behavioral_result?: any;
  graph_result?: any;
  insight?: any;
  message?: string;
}
export interface DashboardStats {
  total_analyses: number;
  total_alerts: number;
  active_threats: number;
  avg_threat_score: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  recent_analyses: any[];
}

export const detectionApi = {
  analyze: (data: AnalyzeRequest) => api.post<AnalyzeResponse>('/api/analyze', data),
  getDetectionResults: (analysisId: string) => api.get(`/api/detect/${analysisId}`),
  getNetworkGraph: (analysisId: string) => api.get(`/api/network/${analysisId}`),
  getDashboardStats: () => api.get<DashboardStats>('/api/dashboard/stats'),
  getDashboardTimeline: (days?: number) => api.get('/api/dashboard/timeline', { params: { days: days || 30 } }),
};
