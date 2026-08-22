import client from './api';
import { mockResources } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const resourceService = {
  async getResources(filters = {}) {
    try {
      const res = await client.get('/api/resources', { params: filters });
      return res.data;
    } catch {
      await delay(400);
      let results = [...mockResources];
      if (filters.type && filters.type !== 'all') {
        results = results.filter((r) => r.type === filters.type);
      }
      if (filters.q) {
        const q = filters.q.toLowerCase();
        results = results.filter((r) => r.title.toLowerCase().includes(q));
      }
      return results;
    }
  },

  async getResourceById(resourceId) {
    try {
      const res = await client.get(`/api/resources/${resourceId}`);
      return res.data;
    } catch {
      await delay(300);
      return mockResources.find((r) => r.id === resourceId);
    }
  },

  async getRecommendedResources() {
    try {
      const res = await client.get('/api/resources/recommended');
      return res.data;
    } catch {
      await delay(400);
      return mockResources.filter((r) => r.isCurrent || r.relevance >= 85);
    }
  },

  async saveResource(resourceId) {
    try {
      const res = await client.post(`/api/resources/${resourceId}/save`);
      return res.data;
    } catch {
      await delay(200);
      return { success: true };
    }
  },
};
