import client from './api';

export const profileService = {
  async getProfile() {
    const res = await client.get('/users/me');
    return res.data;
  },

  async updateProfile(data) {
    const res = await client.put('/users/me', data);
    return res.data;
  },

  async getCareerRecommendation(profileData) {
    const res = await client.post(
      '/recommendations/career',
      profileData
    );

    return res.data;
  },

  async getPreferences() {
    const res = await client.get('/users/me/preferences');
    return res.data;
  },

  async updatePreferences(data) {
    const res = await client.put(
      '/users/me/preferences',
      data
    );

    return res.data;
  },
};