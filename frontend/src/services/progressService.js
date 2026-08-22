import client from './api';
import { mockProgress } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const progressService = {
  async getProgress() {
    try {
      const res = await client.get('/api/progress');
      return res.data;
    } catch {
      await delay(400);
      return mockProgress;
    }
  },
};
