import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vendor-react': ['react', 'react-dom'],
          'vendor-router': ['react-router-dom'],
          'vendor-antd': ['antd', '@ant-design/icons'],
          'vendor-utils': ['axios', 'dayjs', 'zustand'],
          'vendor-i18n': ['i18next', 'react-i18next'],
          'vendor-charts': ['recharts'],
          
          // Feature chunks
          'feature-chat': ['./src/pages/Chat.tsx', './src/components/VirtualizedChat.tsx'],
          'feature-admin': ['./src/pages/Admin.tsx', './src/pages/SystemStatus.tsx'],
          'feature-assistants': ['./src/pages/Assistants.tsx'],
          'feature-tools': ['./src/pages/Tools.tsx', './src/pages/McpTools.tsx'],
          
          // Shared chunks
          'shared-components': [
            './src/components/Layout.tsx',
            './src/components/Sidebar.tsx',
            './src/components/HeaderBar.tsx',
            './src/components/IconSystem.tsx',
          ],
          'shared-stores': [
            './src/store/authStore.ts',
            './src/store/themeStore.ts',
          ],
          'shared-styles': [
            './src/styles/theme.ts',
            './src/index.css',
            './src/App.css',
          ],
        },
      },
    },
    chunkSizeWarningLimit: 1000, // Erhöhe Limit für größere Chunks
    sourcemap: false, // Deaktiviere Source Maps für Production
    minify: 'terser', // Verwende Terser für bessere Minifizierung
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'antd',
      '@ant-design/icons',
      'zustand',
      'axios',
      'dayjs',
      'i18next',
      'react-i18next',
    ],
  },
  server: {
    port: 3000,
    host: true,
  },
  preview: {
    port: 4173,
    host: true,
  },
});
