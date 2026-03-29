import api from './client';

export interface LoginData { username: string; password: string; }
export interface RegisterData { email: string; username: string; password: string; }
export interface TokenResponse { access_token: string; refresh_token: string; token_type: string; }
export interface UserProfile { id: string; email: string; username: string; is_active: boolean; is_admin: boolean; created_at: string; }

export const authApi = {
  login: (data: LoginData) => api.post<TokenResponse>('/api/auth/login', data),
  register: (data: RegisterData) => api.post<UserProfile>('/api/auth/register', data),
  getMe: () => api.get<UserProfile>('/api/auth/me'),
  refresh: (refresh_token: string) => api.post<TokenResponse>('/api/auth/refresh', { refresh_token }),
};
