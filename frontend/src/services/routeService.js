import client from './api';
import { mockRoutes } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const routeService = {
  async getRoutes() {
    try {
      const res = await client.get('/routes');
      return res.data;
    } catch {
      await delay(400);
      return mockRoutes;
    }
  },

  async getRouteById(routeId) {
    try {
      const res = await client.get(`/routes/${routeId}`);
      return res.data;
    } catch {
      await delay(300);
      return mockRoutes.find((r) => r.id === routeId) || mockRoutes[0];
    }
  },

  async generateRoute(goalData) {
    try {
      const res = await client.post('/routes/generate', goalData);
      return res.data;
    } catch {
      await delay(1200);
      return {
        id: `route-${Date.now()}`,
        title: goalData.career_title || goalData.goal || 'New Learning Route',
        progress: 0,
        status: 'active',
        is_current: true,
        current_stage: 'Starting',
        stages: [],
      };
    }
  },

  async createRoute(goalData) {
    return this.generateRoute(goalData);
  },

  async pauseRoute(routeId) {
    try {
      const res = await client.patch(`/routes/${routeId}/pause`);
      return res.data;
    } catch {
      return { success: true };
    }
  },

  async resumeRoute(routeId) {
    try {
      const res = await client.patch(`/routes/${routeId}/resume`);
      return res.data;
    } catch {
      return { success: true };
    }
  },
};
