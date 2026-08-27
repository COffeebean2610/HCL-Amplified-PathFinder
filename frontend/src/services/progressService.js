import client from './api';

export const progressService = {
  async getProgress() {
    const res = await client.get('/progress');
    return res.data;
  },
};
