import { create } from "zustand";
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  isTokenExpired,
} from "../services/auth";
import { getProfile, updateProfile } from "../services/user";

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  language?: string;
  role?: string;
}

export interface UserProfileUpdate {
  username?: string;
  email?: string;
  language?: string;
}

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  user: UserProfile | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string,
    password: string,
    email: string,
  ) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: UserProfileUpdate) => Promise<void>;
  validateToken: () => boolean;
  refreshTokenIfNeeded: () => Promise<boolean>;
  initializeAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem("token"),
  isAuthenticated: !!localStorage.getItem("token"),
  user: null,
  isLoading: false,
  login: async (username, password) => {
    set({ isLoading: true });
    try {
      const token = await apiLogin(username, password);
      set({ token, isAuthenticated: true, isLoading: false });

      await get().fetchProfile();
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  register: async (username, password, email) => {
    await apiRegister(username, password, email);
    // Registration successful, but user needs to login separately
  },
  logout: () => {
    apiLogout();
    set({ token: null, isAuthenticated: false, user: null, isLoading: false });
  },
  fetchProfile: async () => {
    try {
      // Use token from store, fallback to localStorage
      let token = get().token;
      if (!token) {
        token = localStorage.getItem("token");
        if (token) {
          // Update store with token from localStorage
          set({ token, isAuthenticated: true });
        }
      }

      if (!token) {
        console.warn("No token available for profile fetch");
        return;
      }

      const user = await getProfile(token);
      set({ user });
    } catch (error) {
      console.error("Failed to fetch profile:", error);
      // Don't logout on profile fetch failure
    }
  },
  updateProfile: async (data) => {
    const user = await updateProfile(data);
    set({ user });
  },
  validateToken: () => {
    const token = localStorage.getItem("token");
    if (!token) return false;

    // Don't use isTokenExpired() here as it has a buffer
    // Just check if token exists and is not empty
    return !!token && token.length > 0;
  },
  refreshTokenIfNeeded: async () => {
    // Disable automatic token refresh to prevent loops
    console.warn("Automatic token refresh disabled to prevent loops");
    return false;
  },
  initializeAuth: async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    // Set token in store first
    set({ token, isAuthenticated: true });

    // Try to fetch profile to validate token
    try {
      await get().fetchProfile();
    } catch (error: any) {
      console.error("Failed to initialize auth:", error);
      // Only clear token if it's actually invalid (401/403)
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.warn("Token invalid, clearing auth state");
        set({ token: null, isAuthenticated: false, user: null });
      }
    }
  },
}));
