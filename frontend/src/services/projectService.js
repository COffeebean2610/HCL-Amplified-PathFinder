import client from './api';
import { mockProjects } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const projectService = {
  async getProjects() {
    try {
      const res = await client.get('/projects');
      return res.data;
    } catch {
      await delay(300);
      return mockProjects;
    }
  },

  async getProjectById(id) {
    try {
      const res = await client.get(`/projects/${id}`);
      return res.data;
    } catch {
      await delay(200);
      return mockProjects.find((p) => p.id === id) || mockProjects[0];
    }
  },

  async getRecommended() {
    try {
      const res = await client.get('/projects/recommended');
      return res.data;
    } catch {
      await delay(200);
      return mockProjects.filter((p) => p.status === 'recommended');
    }
  },
};
