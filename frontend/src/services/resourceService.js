import client from './api';
import { mockResources } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const resourceService = {
  async getResources(filter) {
    try {
      const res = await client.get('/resources', { params: filter });
      return res.data;
    } catch {
      await delay(300);
      return mockResources;
    }
  },

  async getRecommended() {
    try {
      const res = await client.get('/resources/recommended');
      return res.data;
    } catch {
      await delay(300);
      return mockResources.filter((r) => r.is_current || r.relevance >= 85);
    }
  },

  async getResourceById(id) {
    try {
      const res = await client.get(`/resources/${id}`);
      return res.data;
    } catch {
      await delay(200);
      return mockResources.find((r) => r.id === id) || mockResources[0];
    }
  },
};
