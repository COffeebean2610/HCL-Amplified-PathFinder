import client from './api';
import { mockProfile, mockCareerRecommendations } from '../data/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const profileService = {
  async getProfile() {
    try {
      const res = await client.get('/users/me');
      return res.data;
    } catch {
      await delay(300);
      return mockProfile;
    }
  },

  async updateProfile(data) {
    try {
      const res = await client.put('/users/me', data);
      return res.data;
    } catch {
      await delay(400);
      return { ...mockProfile, ...data };
    }
  },

  async getCareerRecommendation(profileData) {
    try {
      const res = await client.post('/recommendations/career', profileData);
      return res.data;
    } catch {
      await delay(800);
      return mockCareerRecommendations;
    }
  },
};
