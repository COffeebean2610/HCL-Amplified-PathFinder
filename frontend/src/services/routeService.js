import client from './api';
import { mockRoutes } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const routeService = {
  async getRoutes() {
    try {
      const res = await client.get('/api/routes');
      return res.data;
    } catch {
      await delay(500);
      return mockRoutes;
    }
  },

  async getRouteById(routeId) {
    try {
      const res = await client.get(`/api/routes/${routeId}`);
      return res.data;
    } catch {
      await delay(400);
      return mockRoutes.find((r) => r.id === routeId) || mockRoutes[0];
    }
  },

  async createRoute(goalData) {
    try {
      const res = await client.post('/api/routes', goalData);
      return res.data;
    } catch {
      await delay(1500);
      return {
        id: `route-${Date.now()}`,
        title: goalData.goal || 'New Learning Route',
        progress: 0,
        status: 'active',
        isCurrent: false,
        currentStage: 'Starting',
        stages: [],
        milestones: [],
      };
    }
  },

  async pauseRoute(routeId) {
    try {
      const res = await client.patch(`/api/routes/${routeId}/pause`);
      return res.data;
    } catch {
      await delay(300);
      return { success: true };
    }
  },

  async resumeRoute(routeId) {
    try {
      const res = await client.patch(`/api/routes/${routeId}/resume`);
      return res.data;
    } catch {
      await delay(300);
      return { success: true };
    }
  },
};
