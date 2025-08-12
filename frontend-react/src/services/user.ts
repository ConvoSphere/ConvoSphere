import api from "./api";
import config from "../config";

export interface UserProfileUpdate {
  username?: string;
  email?: string;
  language?: string;
}

export async function getProfile(token?: string) {
  const headers: any = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await api.get(`${config.apiEndpoints.auth}/me`, { headers });
  return response.data;
}

export async function updateProfile(data: UserProfileUpdate) {
  const response = await api.put(
    `${config.apiEndpoints.auth}/me/profile`,
    data,
  );
  return response.data;
}

export async function getUserRoles() {
  const response = await api.get(`${config.apiEndpoints.auth}/me`);
  return response.data.role;
}

export async function getUserGroups() {
  const response = await api.get(`${config.apiEndpoints.auth}/me`);
  return response.data.groups;
}

export async function getSSOAttributes() {
  const response = await api.get(`${config.apiEndpoints.auth}/me`);
  return response.data.sso_attributes;
}
