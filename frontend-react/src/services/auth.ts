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

export function logout() {
  localStorage.removeItem('token');
} 