import api from './api';

export interface UserProfileUpdate {
  username?: string;
  email?: string;
  language?: string;
}

export async function getProfile() {
  const response = await api.get('/v1/auth/me');
  return response.data;
}

export async function updateProfile(data: UserProfileUpdate) {
  const response = await api.put('/v1/auth/me/profile', data);
  return response.data;
}

export async function getUserRoles() {
  const response = await api.get('/v1/auth/me');
  return response.data.role;
}

export async function getUserGroups() {
  const response = await api.get('/v1/auth/me');
  return response.data.groups;
}

export async function getSSOAttributes() {
  const response = await api.get('/v1/auth/me');
  return response.data.sso_attributes;
} 