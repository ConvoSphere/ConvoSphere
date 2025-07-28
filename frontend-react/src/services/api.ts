import axios from "axios";
import config from "../config";
import { refreshToken, isTokenExpired } from "./auth";

const api = axios.create({
  baseURL: config.apiUrl,
  withCredentials: true,
});

// Request interceptor for token handling
api.interceptors.request.use(async (config) => {
  // Check if token is expired and refresh if needed
  if (isTokenExpired()) {
    const newToken = await refreshToken();
    if (!newToken) {
      // Redirect to login if refresh fails
      window.location.href = "/login";
      return Promise.reject(new Error("Authentication required"));
    }
  }

  const token = localStorage.getItem("token");
  if (token) {
    config.headers = config.headers || {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for handling 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If we get a 401 and haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newToken = await refreshToken();
        if (newToken) {
          // Retry the original request with new token
          originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
          return api(originalRequest);
        } else {
          // Refresh failed, redirect to login
          window.location.href = "/login";
          return Promise.reject(error);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
