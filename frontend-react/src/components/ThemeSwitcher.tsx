import React from 'react';
import { Switch } from 'antd';
import { useThemeStore, type ThemeMode } from '../store/themeStore';

const ThemeSwitcher: React.FC = () => {
  const mode = useThemeStore((s: { mode: ThemeMode }) => s.mode);
  const toggleMode = useThemeStore((s: { toggleMode: () => void }) => s.toggleMode);
  return (
    <Switch
      checked={mode === 'dark'}
      onChange={toggleMode}
      checkedChildren="🌙"
      unCheckedChildren="☀️"
      aria-label="Toggle dark mode"
    />
  );
};

export default ThemeSwitcher; 