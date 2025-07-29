import { create } from "zustand";
import {
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
  isTokenExpired,
  refreshToken,
} from "../services/auth";
import { getProfile, updateProfile } from "../services/user";
import type { UserProfileUpdate } from "../services/user";

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  language?: string;
  role?: string;
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
      const user = await getProfile();
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
    
    const isValid = !isTokenExpired();
    if (!isValid) {
      set({ token: null, isAuthenticated: false, user: null });
    }
    return isValid;
  },
  refreshTokenIfNeeded: async () => {
    if (isTokenExpired()) {
      try {
        const newToken = await refreshToken();
        if (newToken) {
          set({ token: newToken, isAuthenticated: true });
          return true;
        } else {
          set({ token: null, isAuthenticated: false, user: null });
          return false;
        }
      } catch (error) {
        console.error("Token refresh failed:", error);
        set({ token: null, isAuthenticated: false, user: null });
        return false;
      }
    }
    return true;
  },
  initializeAuth: async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    // Validate existing token
    const isValid = !isTokenExpired();
    if (!isValid) {
      // Try to refresh the token
      const refreshSuccess = await get().refreshTokenIfNeeded();
      if (!refreshSuccess) {
        set({ isAuthenticated: false, user: null });
        return;
      }
    }

    // Token is valid, fetch user profile
    try {
      await get().fetchProfile();
    } catch (error) {
      console.error("Failed to initialize auth:", error);
      // Don't logout on profile fetch failure, just keep the token
    }
  },
}));
