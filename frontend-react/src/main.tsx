import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { useThemeStore } from './store/themeStore';
import { generateCSSVariables } from './styles/theme';

// Theme-Initialisierung
const initializeTheme = () => {
  const { mode } = useThemeStore.getState();
  const cssVariables = generateCSSVariables(mode === 'dark');
  
  // CSS-Variablen an das root-Element anhängen
  const root = document.documentElement;
  Object.entries(cssVariables).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
};

// Theme-Listener für dynamische Updates
const setupThemeListener = () => {
  useThemeStore.subscribe((state) => {
    const cssVariables = generateCSSVariables(state.mode === 'dark');
    const root = document.documentElement;
    
    Object.entries(cssVariables).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
  });
};

// Initialisierung
initializeTheme();
setupThemeListener();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
