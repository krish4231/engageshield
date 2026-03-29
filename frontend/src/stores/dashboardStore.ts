import { create } from 'zustand';
import type { DashboardStats } from '../api/detection';

interface DashboardState {
  stats: DashboardStats | null;
  timeline: any[];
  isLoading: boolean;
  setStats: (stats: DashboardStats) => void;
  setTimeline: (data: any[]) => void;
  setLoading: (loading: boolean) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  stats: null,
  timeline: [],
  isLoading: false,
  setStats: (stats) => set({ stats }),
  setTimeline: (data) => set({ timeline: data }),
  setLoading: (isLoading) => set({ isLoading }),
}));
