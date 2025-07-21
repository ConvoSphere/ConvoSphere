import { create } from 'zustand';
import { login as apiLogin, logout as apiLogout, register as apiRegister } from '../services/auth';
import { getProfile, updateProfile } from '../services/user';

export interface UserProfile {
  id: string;
  username: string;
  email: string;
}

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  user: UserProfile | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, email: string) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  user: null,
  login: async (username, password) => {
    const token = await apiLogin(username, password);
    set({ token, isAuthenticated: true });
    await (useAuthStore.getState().fetchProfile());
  },
  register: async (username, password, email) => {
    const token = await apiRegister(username, password, email);
    set({ token, isAuthenticated: true });
    await (useAuthStore.getState().fetchProfile());
  },
  logout: () => {
    apiLogout();
    set({ token: null, isAuthenticated: false, user: null });
  },
  fetchProfile: async () => {
    const user = await getProfile();
    set({ user });
  },
  updateProfile: async (data) => {
    const user = await updateProfile(data);
    set({ user });
  },
})); 