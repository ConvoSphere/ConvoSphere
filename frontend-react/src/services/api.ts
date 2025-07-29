import axios from "axios";
import config from "../config";
import { refreshToken, isTokenExpired } from "./auth";

const api = axios.create({
  baseURL: config.apiUrl,
  withCredentials: true,
});

// Global state to prevent loops
let isRefreshing = false;
let refreshAttempts = 0;
const MAX_REFRESH_ATTEMPTS = 2;
let lastRefreshTime = 0;
const REFRESH_COOLDOWN = 30000; // 30 seconds cooldown
let isLoopDetected = false;

// Request interceptor - simplified to prevent loops
api.interceptors.request.use(async (config: any) => {
  // Skip all token handling for auth endpoints
  if (config.url?.includes('/auth/')) {
    return config;
  }

  // If we've detected a loop, don't add any auth headers
  if (isLoopDetected) {
    return config;
  }

  // Check if we've exceeded max refresh attempts
  if (refreshAttempts >= MAX_REFRESH_ATTEMPTS) {
    console.warn("Max refresh attempts exceeded, clearing auth state");
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("token_expiry");
    isLoopDetected = true;
    if (!window.location.pathname.includes('/login')) {
      window.location.href = "/login";
    }
    return config;
  }

  // Only add token if it exists and is not expired
  const token = localStorage.getItem("token");
  if (token && !isTokenExpired()) {
    config.headers = config.headers || {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }

  return config;
});

// Response interceptor - simplified to prevent loops
api.interceptors.response.use(
  (response: any) => response,
  async (error: any) => {
    const originalRequest = error.config;

    // If we've detected a loop, don't try to refresh
    if (isLoopDetected) {
      return Promise.reject(error);
    }

    // Only handle 401 errors and only if we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Skip auth endpoints completely
      if (originalRequest.url?.includes('/auth/')) {
        return Promise.reject(error);
      }

      const now = Date.now();
      
      // Check cooldown
      if (now - lastRefreshTime < REFRESH_COOLDOWN) {
        console.warn("Refresh cooldown active, redirecting to login");
        if (!window.location.pathname.includes('/login')) {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      // Check if already refreshing
      if (isRefreshing) {
        console.warn("Already refreshing, redirecting to login");
        if (!window.location.pathname.includes('/login')) {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      // Start refresh attempt
      isRefreshing = true;
      lastRefreshTime = now;
      refreshAttempts++;

      try {
        const newToken = await refreshToken();
        if (newToken) {
          // Reset attempts on success
          refreshAttempts = 0;
          originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
          return api(originalRequest);
        } else {
          // Refresh failed
          console.warn("Token refresh failed");
          if (!window.location.pathname.includes('/login')) {
            window.location.href = "/login";
          }
          return Promise.reject(error);
        }
      } catch (refreshError) {
        console.error("Token refresh error:", refreshError);
        if (!window.location.pathname.includes('/login')) {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Handle rate limiting
    if (error.response?.status === 429) {
      console.warn("Rate limit exceeded, redirecting to login");
      if (!window.location.pathname.includes('/login')) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
