import api from './client';

export interface Alert {
  id: string;
  analysis_id?: string;
  title: string;
  description: string;
  severity: string;
  category: string;
  target_identifier?: string;
  threat_score: number;
  evidence: any;
  is_read: boolean;
  is_resolved: boolean;
  created_at: string;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  page: number;
  page_size: number;
}

export const alertsApi = {
  list: (params?: { page?: number; severity?: string; category?: string }) =>
    api.get<AlertListResponse>('/api/alerts', { params }),
  update: (id: string, data: { is_read?: boolean; is_resolved?: boolean }) =>
    api.patch<Alert>(`/api/alerts/${id}`, data),
};
