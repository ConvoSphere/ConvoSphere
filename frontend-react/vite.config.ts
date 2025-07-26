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
        manualChunks: {
          // Vendor chunks - Core libraries
          "vendor-react": ["react", "react-dom"],
          "vendor-router": ["react-router-dom"],
          "vendor-antd": ["antd", "@ant-design/icons"],
          "vendor-utils": ["axios", "dayjs", "zustand"],
          "vendor-i18n": ["i18next", "react-i18next"],
          "vendor-charts": ["recharts"],

          // Feature chunks - Page-specific code
          "feature-chat": [
            "./src/pages/Chat.tsx",
            "./src/components/VirtualizedChat.tsx",
          ],
          "feature-admin": [
            "./src/pages/Admin.tsx",
            "./src/pages/SystemStatus.tsx",
          ],
          "feature-assistants": ["./src/pages/Assistants.tsx"],
          "feature-tools": [
            "./src/pages/Tools.tsx",
            "./src/pages/McpTools.tsx",
          ],
          "feature-auth": ["./src/pages/Login.tsx", "./src/pages/Register.tsx"],
          "feature-user": [
            "./src/pages/Profile.tsx",
            "./src/pages/Conversations.tsx",
          ],

          // Shared chunks - Reusable components and utilities
          "shared-components": [
            "./src/components/Layout.tsx",
            "./src/components/Sidebar.tsx",
            "./src/components/HeaderBar.tsx",
            "./src/components/ThemeSwitcher.tsx",
            "./src/components/LanguageSwitcher.tsx",
            "./src/components/LogoutButton.tsx",
          ],
          "shared-stores": [
            "./src/store/authStore.ts",
            "./src/store/themeStore.ts",
          ],
          "shared-styles": [
            "./src/styles/theme.ts",
            "./src/index.css",
            "./src/App.css",
            "./src/styles/animations.css",
          ],
          "shared-utils": [
            "./src/services/chat.ts",
            "./src/config/",
            "./src/i18n/",
          ],
        },
        // Optimize chunk naming for better caching
        chunkFileNames: () => {
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
