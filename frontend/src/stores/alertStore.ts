import { create } from 'zustand';
import type { Alert } from '../api/alerts';

interface AlertState {
  alerts: Alert[];
  unreadCount: number;
  addAlert: (alert: Alert) => void;
  setAlerts: (alerts: Alert[]) => void;
  markAsRead: (id: string) => void;
}

export const useAlertStore = create<AlertState>((set) => ({
  alerts: [],
  unreadCount: 0,

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 100),
      unreadCount: state.unreadCount + 1,
    })),

  setAlerts: (alerts) =>
    set({
      alerts,
      unreadCount: alerts.filter((a) => !a.is_read).length,
    }),

  markAsRead: (id) =>
    set((state) => ({
      alerts: state.alerts.map((a) => (a.id === id ? { ...a, is_read: true } : a)),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),
}));
