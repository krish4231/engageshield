import api from './client';

export interface Insight {
  id: string;
  analysis_id: string;
  engine: string;
  score: number;
  confidence: number;
  details: any;
  summary?: string;
  created_at: string;
}

export const insightsApi = {
  list: (params?: { limit?: number; engine?: string }) =>
    api.get('/api/insights', { params }),
  getByAnalysis: (analysisId: string) =>
    api.get(`/api/insights/${analysisId}`),
};
