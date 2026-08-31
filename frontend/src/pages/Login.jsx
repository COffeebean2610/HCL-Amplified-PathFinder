import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Eye, EyeOff, ArrowRight, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import AuthLayout from '../components/auth/AuthLayout';
import { Button } from '../components/common/Button';

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
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-2 p-4 bg-[#A96A5F]/10 border border-[#A96A5F]/30 rounded-lg"
          >
            <AlertCircle size={14} className="text-[#A96A5F] flex-shrink-0 mt-0.5" />
            <p className="text-sm text-[#A96A5F]">{error}</p>
          </motion.div>
        )}

        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-xs font-medium text-[#AAA89F] mb-2 tracking-wide uppercase">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            className={fieldErrors.email ? 'border-[#A96A5F]' : ''}
          />
          {fieldErrors.email && (
            <p className="mt-1.5 text-xs text-[#A96A5F] flex items-center gap-1">
              <AlertCircle size={11} /> {fieldErrors.email}
            </p>
          )}
        </div>

        {/* Password */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label htmlFor="password" className="block text-xs font-medium text-[#AAA89F] tracking-wide uppercase">
              Password
            </label>
            <span className="text-xs text-[#77766F] cursor-not-allowed" title="Password recovery coming soon">
              Forgot password?
            </span>
          </div>
          <div className="relative">
            <input
              id="password"
              type={showPw ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
              autoComplete="current-password"
              className={fieldErrors.password ? 'border-[#A96A5F]' : ''}
            />
            <button
              type="button"
              onClick={() => setShowPw((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#77766F] hover:text-[#AAA89F] transition-colors cursor-pointer"
            >
              {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          </div>
          {fieldErrors.password && (
            <p className="mt-1.5 text-xs text-[#A96A5F] flex items-center gap-1">
              <AlertCircle size={11} /> {fieldErrors.password}
            </p>
          )}
        </div>

        <Button
          type="submit"
          fullWidth
          loading={loading}
          icon={!loading && <ArrowRight size={15} />}
          size="lg"
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </Button>

        <p className="text-center text-sm text-[#77766F]">
          Don't have an account?{' '}
          <Link to="/register" className="text-[#C89B5B] hover:text-[#D4AA6C] transition-colors font-medium">
            Create an account
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}
