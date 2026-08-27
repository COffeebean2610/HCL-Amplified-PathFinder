import client from './api';

export const projectService = {
  async getProjects() {
    const res = await client.get('/projects');
    return res.data;
  },

  async getProjectById(id) {
    const res = await client.get(`/projects/${id}`);
    return res.data;
  },

  async getRecommended() {
    const res = await client.get('/projects/recommended');
    return res.data;
  },
};
