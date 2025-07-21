import axios from 'axios';

const api = axios.create({
  baseURL: '/api', // ggf. anpassen
  withCredentials: true,
});

// Token-Handling (Beispiel)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default api; 