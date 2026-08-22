import client from './api';
import { mockProjects } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const projectService = {
  async getProjects() {
    try {
      const res = await client.get('/api/projects');
      return res.data;
    } catch {
      await delay(400);
      return mockProjects;
    }
  },

  async getProjectById(projectId) {
    try {
      const res = await client.get(`/api/projects/${projectId}`);
      return res.data;
    } catch {
      await delay(300);
      return mockProjects.find((p) => p.id === projectId);
    }
  },

  async startProject(projectId) {
    try {
      const res = await client.post(`/api/projects/${projectId}/start`);
      return res.data;
    } catch {
      await delay(300);
      return { success: true };
    }
  },
};
