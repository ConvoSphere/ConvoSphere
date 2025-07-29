import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import autoprefixer from "autoprefixer";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Ensure React 18 compatibility
      jsxRuntime: 'automatic',
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Simple chunk splitting
          'vendor-react': ['react', 'react-dom'],
          'vendor-antd': ['antd', '@ant-design/icons'],
          'vendor-router': ['react-router-dom'],
          'vendor-utils': ['axios', 'zustand', 'dayjs'],
          'vendor-i18n': ['i18next', 'react-i18next'],
        },
        chunkFileNames: "js/[name]-[hash].js",
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
    target: "es2015",
    cssCodeSplit: true,
    reportCompressedSize: true,
    emptyOutDir: true,
  },
  optimizeDeps: {
    include: [
      "react",
      "react-dom",
      "react/jsx-runtime",
      "react/jsx-dev-runtime",
      "react-router-dom",
      "antd",
      "@ant-design/icons",
      "zustand",
      "axios",
      "dayjs",
      "i18next",
      "react-i18next",
    ],
    force: true,
  },
  server: {
    port: 3000,
    host: true,
    hmr: {
      overlay: false,
    },
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
  esbuild: {
    target: "es2015",
    legalComments: "none",
  },
  css: {
    devSourcemap: false,
    postcss: {
      plugins: [
        autoprefixer({
          overrideBrowserslist: ["> 1%", "last 2 versions", "not dead"],
        }),
      ],
    },
  },
  resolve: {
    alias: {
      'react': 'react',
      'react-dom': 'react-dom',
    },
  },
});
