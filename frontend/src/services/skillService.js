import client from './api';
import { mockSkills, mockSkillGaps } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const skillService = {
  async getSkills() {
    try {
      const res = await client.get('/api/skills');
      return res.data;
    } catch {
      await delay(400);
      return mockSkills;
    }
  },

  async getSkillGaps() {
    try {
      const res = await client.get('/api/skills/gaps');
      return res.data;
    } catch {
      await delay(400);
      return mockSkillGaps;
    }
  },
};
