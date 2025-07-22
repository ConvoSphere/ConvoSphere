import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import './styles/animations.css';
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

// Service Worker Registration
const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      });

      console.log('Service Worker registered successfully:', registration);

      // Handle updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New content is available
              console.log('New content is available; please refresh.');
              
              // Show update notification
              if (confirm('A new version is available! Reload to update?')) {
                window.location.reload();
              }
            }
          });
        }
      });

      // Handle service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'CACHE_UPDATED') {
          console.log('Cache updated:', event.data.payload);
        }
      });

    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  }
};

// PWA Install Prompt
const setupPWAInstall = () => {
  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    
    // Show install button or notification
    console.log('PWA install prompt available');
    
    // You can show a custom install button here
    // showInstallButton();
  });

  window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
  });
};

// Offline/Online Status
const setupNetworkStatus = () => {
  const updateOnlineStatus = () => {
    const status = navigator.onLine ? 'online' : 'offline';
    console.log('Network status:', status);
    
    // Update UI based on network status
    document.documentElement.setAttribute('data-network', status);
    
    // Show notification
    if (status === 'offline') {
      console.log('You are now offline');
    } else {
      console.log('You are now online');
    }
  };

  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  
  // Initial check
  updateOnlineStatus();
};

// Initialize all features
const initializeApp = async () => {
  // Initialize theme
  initializeTheme();
  setupThemeListener();
  
  // Initialize PWA features
  await registerServiceWorker();
  setupPWAInstall();
  setupNetworkStatus();
  
  console.log('App initialized successfully');
};

// Initialize app
initializeApp();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
