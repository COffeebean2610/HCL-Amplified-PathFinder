import client from './api';
import { mockProfile, mockCareerRecommendations } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const profileService = {
  async getProfile() {
    try {
      const res = await client.get('/api/profile');
      return res.data;
    } catch {
      await delay(400);
      return mockProfile;
    }
  },

  async updateProfile(data) {
    try {
      const res = await client.put('/api/profile', data);
      return res.data;
    } catch {
      await delay(600);
      return { ...mockProfile, ...data };
    }
  },

  async getCareerRecommendation(profileData) {
    try {
      const res = await client.post('/api/career-recommendation', profileData);
      return res.data;
    } catch {
      await delay(1200);
      return mockCareerRecommendations;
    }
  },
};
