import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, ArrowRight, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import AuthLayout from '../components/auth/AuthLayout';

function FormField({ label, id, type = 'text', value, onChange, placeholder, error, rightElement }) {
  return (
    <div className="rm-auth-field">
      <label htmlFor={id} className="rm-auth-label">
        {label}
      </label>
      <div className="rm-auth-input-wrap">
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`rm-auth-input ${error ? 'is-error' : ''}`}
          autoComplete={type === 'password' ? 'new-password' : 'off'}
        />
        {rightElement && (
          <div className="rm-auth-input-affix">{rightElement}</div>
        )}
      </div>
      {error && (
        <p className="rm-auth-field-error">
          <AlertCircle size={11} /> {error}
        </p>
      )}
    </div>
  );
}

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [showPw, setShowPw] = useState(false);
  const [showCpw, setShowCpw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState('');

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const validate = () => {
    const errs = {};
    if (!form.name.trim()) errs.name = 'Name is required';
    if (!form.email.trim()) errs.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Please enter a valid email';
    if (!form.password) errs.password = 'Password is required';
    else if (form.password.length < 8) errs.password = 'Password must be at least 8 characters';
    if (!form.confirmPassword) errs.confirmPassword = 'Please confirm your password';
    else if (form.password !== form.confirmPassword) errs.confirmPassword = 'Passwords do not match';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    setLoading(true);
    try {
      await register(form);
      // Always go to onboarding after registration
      navigate('/onboarding', { replace: true });
    } catch (err) {
      setServerError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Create your RouteMaster account"
      subtitle="Start building a learning route designed around your goals."
    >
      <form onSubmit={handleSubmit} className="rm-auth-form" noValidate>
        {serverError && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rm-auth-error"
          >
            <AlertCircle size={14} className="rm-auth-error__icon" />
            <p>{serverError}</p>
          </motion.div>
        )}

        <FormField
          label="Full Name"
          id="name"
          value={form.name}
          onChange={update('name')}
          placeholder="Abhishek Kumar"
          error={errors.name}
        />
        <FormField
          label="Email"
          id="email"
          type="email"
          value={form.email}
          onChange={update('email')}
          placeholder="you@example.com"
          error={errors.email}
        />
        <FormField
          label="Password"
          id="password"
          type={showPw ? 'text' : 'password'}
          value={form.password}
          onChange={update('password')}
          placeholder="Min. 8 characters"
          error={errors.password}
          rightElement={
            <button
              type="button"
              onClick={() => setShowPw((v) => !v)}
              className="rm-auth-visibility"
            >
              {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          }
        />
        <FormField
          label="Confirm Password"
          id="confirmPassword"
          type={showCpw ? 'text' : 'password'}
          value={form.confirmPassword}
          onChange={update('confirmPassword')}
          placeholder="Repeat password"
          error={errors.confirmPassword}
          rightElement={
            <button
              type="button"
              onClick={() => setShowCpw((v) => !v)}
              className="rm-auth-visibility"
            >
              {showCpw ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          }
        />

        <button type="submit" className="rm-btn rm-btn--primary rm-btn--full rm-auth-submit" disabled={loading}>
          {loading ? (
            <span className="rm-auth-spinner" aria-hidden="true" />
          ) : (
            <>
              Create Account <ArrowRight size={15} />
            </>
          )}
        </button>

        <p className="rm-auth-switch">
          Already have an account?{' '}
          <Link to="/login">
            Sign in
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}
