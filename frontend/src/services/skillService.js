import client from './api';

export const skillService = {
  async getSkills() {
    const res = await client.get('/skills');
    return res.data;
  },

  async getSkillGaps() {
    const res = await client.get('/skills/gaps');
    return res.data;
  },
};
