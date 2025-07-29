import axios from "axios";
import config from "../config";
import { refreshToken, isTokenExpired } from "./auth";

const api = axios.create({
  baseURL: config.apiUrl,
  withCredentials: true,
});

// Track if we're currently refreshing to prevent loops
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

// Request interceptor for token handling
api.interceptors.request.use(async (config) => {
  // Skip token check for auth endpoints to prevent loops
  if (config.url?.includes('/auth/login') || config.url?.includes('/auth/refresh')) {
    return config;
  }

  // Check if token is expired and refresh if needed
  if (isTokenExpired()) {
    if (isRefreshing) {
      // If already refreshing, queue this request
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        config.headers = config.headers || {};
        config.headers["Authorization"] = `Bearer ${token}`;
        return config;
      }).catch((err) => {
        return Promise.reject(err);
      });
    }

    isRefreshing = true;
    
    try {
      const newToken = await refreshToken();
      if (newToken) {
        processQueue(null, newToken);
        config.headers = config.headers || {};
        config.headers["Authorization"] = `Bearer ${newToken}`;
      } else {
        processQueue(new Error("Token refresh failed"));
        // Don't redirect here, let the response interceptor handle it
      }
    } catch (error) {
      processQueue(error);
      // Don't redirect here, let the response interceptor handle it
    } finally {
      isRefreshing = false;
    }
  } else {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${token}`;
    }
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

      // Skip auth endpoints to prevent loops
      if (originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/refresh')) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers["Authorization"] = `Bearer ${token}`;
          return api(originalRequest);
        }).catch((err) => {
          return Promise.reject(err);
        });
      }

      isRefreshing = true;

      try {
        const newToken = await refreshToken();
        if (newToken) {
          processQueue(null, newToken);
          originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
          return api(originalRequest);
        } else {
          processQueue(new Error("Token refresh failed"));
          // Only redirect if we're not already on login page
          if (!window.location.pathname.includes('/login')) {
            window.location.href = "/login";
          }
          return Promise.reject(error);
        }
      } catch (refreshError) {
        processQueue(refreshError);
        // Only redirect if we're not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
