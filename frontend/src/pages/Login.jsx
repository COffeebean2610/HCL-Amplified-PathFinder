import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Eye, EyeOff, ArrowRight, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import AuthLayout from '../components/auth/AuthLayout';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const from = location.state?.from?.pathname || '/home';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!email.trim()) errs.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = 'Please enter a valid email';
    if (!password) errs.password = 'Password is required';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const errs = validate();
    if (Object.keys(errs).length) { setFieldErrors(errs); return; }
    setFieldErrors({});
    setLoading(true);
    try {
      const data = await login({ email, password });
      if (!data.onboarding_completed) {
        navigate('/onboarding', { replace: true });
      } else {
        navigate(from === '/login' || from === '/register' ? '/home' : from, { replace: true });
      }
    } catch (err) {
      setError(err.message || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Continue your learning journey."
    >
      <form onSubmit={handleSubmit} className="rm-auth-form" noValidate>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rm-auth-error"
          >
            <AlertCircle size={14} className="rm-auth-error__icon" />
            <p>{error}</p>
          </motion.div>
        )}

        <div className="rm-auth-field">
          <label htmlFor="email" className="rm-auth-label">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            className={`rm-auth-input ${fieldErrors.email ? 'is-error' : ''}`}
          />
          {fieldErrors.email && (
            <p className="rm-auth-field-error">
              <AlertCircle size={11} /> {fieldErrors.email}
            </p>
          )}
        </div>

        <div className="rm-auth-field">
          <div className="rm-auth-field__row">
            <label htmlFor="password" className="rm-auth-label">
              Password
            </label>
            <span className="rm-auth-muted-link" title="Password recovery coming soon">
              Forgot password?
            </span>
          </div>
          <div className="rm-auth-input-wrap">
            <input
              id="password"
              type={showPw ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
              autoComplete="current-password"
              className={`rm-auth-input ${fieldErrors.password ? 'is-error' : ''}`}
            />
            <button
              type="button"
              onClick={() => setShowPw((v) => !v)}
              className="rm-auth-visibility"
            >
              {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          </div>
          {fieldErrors.password && (
            <p className="rm-auth-field-error">
              <AlertCircle size={11} /> {fieldErrors.password}
            </p>
          )}
        </div>

        <button type="submit" className="rm-btn rm-btn--primary rm-btn--full rm-auth-submit" disabled={loading}>
          {loading ? (
            <span className="rm-auth-spinner" aria-hidden="true" />
          ) : (
            <>
              Sign In <ArrowRight size={15} />
            </>
          )}
        </button>

        <p className="rm-auth-switch">
          Don't have an account?{' '}
          <Link to="/register">
            Create an account
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}
