import client from './api';

export const routeService = {
  async getRoutes() {
    const res = await client.get('/routes');
    return res.data;
  },

  async getRouteById(routeId) {
    const res = await client.get(`/routes/${routeId}`);
    return res.data;
  },

  async generateRoute(goalData) {
    const res = await client.post('/routes/generate', goalData);
    return res.data;
  },

  async createRoute(goalData) {
    return this.generateRoute(goalData);
  },

  async pauseRoute(routeId) {
    const res = await client.patch(`/routes/${routeId}/pause`);
    return res.data;
  },

  async resumeRoute(routeId) {
    const res = await client.patch(`/routes/${routeId}/resume`);
    return res.data;
  },
};
