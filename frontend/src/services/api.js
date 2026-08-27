import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const isDevelopment = import.meta.env.DEV;

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

const requestLabel = (config) => `${(config.method || 'get').toUpperCase()} ${config.baseURL || ''}${config.url || ''}`;

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('rm_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;

  config.metadata = { startedAt: performance.now(), label: requestLabel(config) };
  if (isDevelopment) console.info('[RouteMaster API] →', config.metadata.label);
  return config;
});

client.interceptors.response.use(
  (response) => {
    if (isDevelopment) {
      const duration = Math.round(performance.now() - (response.config.metadata?.startedAt || performance.now()));
      console.info('[RouteMaster API] ←', response.status, response.config.metadata?.label || requestLabel(response.config), `${duration}ms`);
    }
    return response;
  },
  (err) => {
    const config = err.config || {};
    const duration = config.metadata?.startedAt
      ? `${Math.round(performance.now() - config.metadata.startedAt)}ms`
      : 'unknown duration';

    if (isDevelopment) {
      console.error(
        '[RouteMaster API] ×',
        err.code === 'ECONNABORTED' ? 'timeout' : 'error',
        config.metadata?.label || requestLabel(config),
        duration,
        err.message,
      );
    }

    if (err?.response?.status === 401) {
      localStorage.removeItem('rm_token');
      localStorage.removeItem('rm_user');
      const path = window.location.pathname;
      if (path !== '/login' && path !== '/register' && path !== '/') {
        window.location.href = '/login';
      }
    }

    const message =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      err?.message ||
      'Something went wrong';
    return Promise.reject(new Error(message));
  },
);

export default client;
