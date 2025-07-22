import api from './api';

export async function login(username: string, password: string) {
  const response = await api.post('/auth/login', { username, password });
  const { token } = response.data;
  localStorage.setItem('token', token);
  return token;
}

export async function register(username: string, password: string, email: string) {
  const response = await api.post('/auth/register', { username, password, email });
  const { token } = response.data;
  localStorage.setItem('token', token);
  return token;
}

export async function ssoLogin(provider: string) {
  // Redirect to backend SSO login endpoint
  window.location.href = `/api/v1/auth/sso/login/${provider}`;
}

export async function ssoLink(provider: string) {
  // Call backend SSO link endpoint
  const response = await api.post(`/auth/sso/link/${provider}`);
  return response.data;
}

export function logout() {
  localStorage.removeItem('token');
} 