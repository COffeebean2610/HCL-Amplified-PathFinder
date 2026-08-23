import client from './api';

export const authService = {
  async register({ name, email, password, confirmPassword }) {
    const res = await client.post('/auth/register', {
      name,
      email,
      password,
      confirm_password: confirmPassword,
    });
    return res.data;
  },

  async login({ email, password }) {
    const res = await client.post('/auth/login', { email, password });
    return res.data;
  },

  async getMe() {
    const res = await client.get('/auth/me');
    return res.data;
  },

  async logout() {
    try {
      await client.post('/auth/logout');
    } catch {
      // Ignore — client-side cleanup always happens
    }
    localStorage.removeItem('rm_token');
    localStorage.removeItem('rm_user');
  },
};
