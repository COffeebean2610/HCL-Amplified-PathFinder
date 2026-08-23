import client from './api';
import { mockProgress } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const progressService = {
  async getProgress() {
    try {
      const res = await client.get('/progress');
      return res.data;
    } catch {
      await delay(300);
      return mockProgress;
    }
  },
};
