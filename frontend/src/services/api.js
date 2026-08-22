import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || '';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// Request interceptor — attach token if available
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('rm_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle errors uniformly
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err?.response?.data?.message || err?.message || 'Something went wrong';
    return Promise.reject(new Error(message));
  }
);

export default client;
