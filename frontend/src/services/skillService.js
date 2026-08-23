import client from './api';
import { mockSkills } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const skillService = {
  async getSkills() {
    try {
      const res = await client.get('/skills');
      return res.data;
    } catch {
      await delay(300);
      return mockSkills;
    }
  },

  async getSkillGaps() {
    try {
      const res = await client.get('/skills/gaps');
      return res.data;
    } catch {
      await delay(300);
      return null;
    }
  },
};
