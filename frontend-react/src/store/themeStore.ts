import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { lightTheme, darkTheme, getThemeColors } from '../styles/theme';

export type ThemeMode = 'light' | 'dark';

interface ThemeState {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  toggleMode: () => void;
  getCurrentTheme: () => typeof lightTheme | typeof darkTheme;
  getCurrentColors: () => ReturnType<typeof getThemeColors>;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'light',
      setMode: (mode) => set({ mode }),
      toggleMode: () => set({ mode: get().mode === 'light' ? 'dark' : 'light' }),
      getCurrentTheme: () => get().mode === 'dark' ? darkTheme : lightTheme,
      getCurrentColors: () => getThemeColors(get().mode === 'dark'),
    }),
    {
      name: 'theme-storage',
      partialize: (state) => ({ mode: state.mode }),
    }
  )
); 