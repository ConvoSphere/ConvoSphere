import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";
import autoprefixer from "autoprefixer";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: "dist/stats.html",
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunks - Core libraries
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'vendor-react';
            }
            if (id.includes('react-router')) {
              return 'vendor-router';
            }
            if (id.includes('antd') || id.includes('@ant-design')) {
              return 'vendor-antd';
            }
            if (id.includes('axios') || id.includes('dayjs') || id.includes('zustand')) {
              return 'vendor-utils';
            }
            if (id.includes('i18next')) {
              return 'vendor-i18n';
            }
            if (id.includes('recharts')) {
              return 'vendor-charts';
            }
            // Default vendor chunk for other node_modules
            return 'vendor';
          }

          // Feature chunks - Page-specific code
          if (id.includes('/pages/Login.tsx') || id.includes('/pages/Register.tsx')) {
            return 'feature-auth';
          }
          if (id.includes('/pages/Chat.tsx') || id.includes('/components/VirtualizedChat.tsx')) {
            return 'feature-chat';
          }
          if (id.includes('/pages/Admin.tsx') || id.includes('/pages/SystemStatus.tsx')) {
            return 'feature-admin';
          }
          if (id.includes('/pages/Assistants.tsx')) {
            return 'feature-assistants';
          }
          if (id.includes('/pages/Tools.tsx') || id.includes('/pages/McpTools.tsx')) {
            return 'feature-tools';
          }
          if (id.includes('/pages/Profile.tsx') || id.includes('/pages/Conversations.tsx')) {
            return 'feature-user';
          }

          // Shared chunks - Reusable components and utilities
          if (id.includes('/components/Layout.tsx') || 
              id.includes('/components/Sidebar.tsx') || 
              id.includes('/components/HeaderBar.tsx') ||
              id.includes('/components/ThemeSwitcher.tsx') ||
              id.includes('/components/LanguageSwitcher.tsx') ||
              id.includes('/components/LogoutButton.tsx')) {
            return 'shared-components';
          }
          if (id.includes('/store/authStore.ts') || id.includes('/store/themeStore.ts')) {
            return 'shared-stores';
          }
          if (id.includes('/styles/theme.ts') || 
              id.includes('/index.css') || 
              id.includes('/App.css') || 
              id.includes('/styles/animations.css')) {
            return 'shared-styles';
          }
          if (id.includes('/services/chat.ts') || 
              id.includes('/config/') || 
              id.includes('/i18n/')) {
            return 'shared-utils';
          }

          // Default chunk for other files
          return 'index';
        },
        // Optimize chunk naming for better caching
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
          return `js/[name]-[hash].js`;
        },
        entryFileNames: "js/[name]-[hash].js",
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name;
          if (!name) return "assets/[name]-[hash].[ext]";

          const info = name.split(".");
          const ext = info[info.length - 1];
          if (/\.(css)$/.test(name)) {
            return `css/[name]-[hash].${ext}`;
          }
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(name)) {
            return `images/[name]-[hash].${ext}`;
          }
          return `assets/[name]-[hash].${ext}`;
        },
      },
    },
    chunkSizeWarningLimit: 1000,
    sourcemap: false,
    minify: "terser",
    target: "es2015", // Support older browsers
    cssCodeSplit: true, // Split CSS for better caching
    reportCompressedSize: true, // Report compressed sizes
    emptyOutDir: true, // Clean output directory
  },
  optimizeDeps: {
    include: [
      "react",
      "react-dom",
      "react-router-dom",
      "antd",
      "@ant-design/icons",
      "zustand",
      "axios",
      "dayjs",
      "i18next",
      "react-i18next",
    ],
    exclude: ["@ant-design/icons"], // Exclude large icon library from pre-bundling
  },
  server: {
    port: 3000,
    host: true,
    // Enable HMR with better performance
    hmr: {
      overlay: false, // Disable error overlay for better performance
    },
    // Proxy API requests to backend
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    port: 4173,
    host: true,
  },
  // Performance optimizations
  esbuild: {
    target: "es2015",
    legalComments: "none", // Remove legal comments
  },
  // CSS optimizations
  css: {
    devSourcemap: false,
    postcss: {
      plugins: [
        // Add autoprefixer for better browser support
        autoprefixer({
          overrideBrowserslist: ["> 1%", "last 2 versions", "not dead"],
        }),
      ],
    },
  },
});
