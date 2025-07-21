import api from './api';

export async function getProfile() {
  const response = await api.get('/users/me');
  return response.data;
}

export async function updateProfile(data: { username?: string; email?: string; }) {
  const response = await api.put('/users/me', data);
  return response.data;
} 