import api from './api';

export interface UserProfileUpdate {
  username?: string;
  email?: string;
  language?: string;
}

export async function getProfile() {
  const response = await api.get('/users/me');
  return response.data;
}

export async function updateProfile(data: UserProfileUpdate) {
  const response = await api.put('/users/me/profile', data);
  return response.data;
} 