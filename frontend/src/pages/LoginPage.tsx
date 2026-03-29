import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const { login, register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await register(email, username, password);
        await login(username, password);
      } else {
        await login(username, password);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-card__logo">
          <div className="login-card__logo-icon">🛡️</div>
          <h1 className="login-card__title">EngageShield</h1>
          <p className="login-card__subtitle">
            Intelligent Fake Engagement Detection
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {isRegister && (
            <div className="login-form__group">
              <label className="login-form__label">Email</label>
              <input
                id="email-input"
                type="email"
                className="input-field"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          )}

          <div className="login-form__group">
            <label className="login-form__label">Username</label>
            <input
              id="username-input"
              type="text"
              className="input-field"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="login-form__group">
            <label className="login-form__label">Password</label>
            <input
              id="password-input"
              type="password"
              className="input-field"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <div style={{
              padding: '0.5rem 0.75rem',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(244, 63, 94, 0.1)',
              border: '1px solid rgba(244, 63, 94, 0.25)',
              color: '#fb7185',
              fontSize: '0.8rem',
            }}>
              {error}
            </div>
          )}

          <button
            id="submit-btn"
            type="submit"
            className="btn btn-primary login-form__submit"
            disabled={isLoading}
          >
            {isLoading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
          </button>

          <div className="login-form__footer">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <a
              href="#"
              onClick={(e) => { e.preventDefault(); setIsRegister(!isRegister); setError(''); }}
              style={{ color: 'var(--accent-primary-light)', fontWeight: 600 }}
            >
              {isRegister ? 'Sign In' : 'Register'}
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}
