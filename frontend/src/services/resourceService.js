import client from './api';

export const resourceService = {
  async getResources(filter) {
    const res = await client.get('/resources', { params: filter });
    return res.data;
  },

  async getRecommended() {
    const res = await client.get('/resources/recommended');
    return res.data;
  },

  async getResourceById(id) {
    const res = await client.get(`/resources/${id}`);
    return res.data;
  },
};
