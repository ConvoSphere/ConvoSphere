import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

const ANALYZE = process.env.ANALYZE === '1' || process.env.ANALYZE === 'true'
const ENABLE_SOURCEMAP = ANALYZE || process.env.SOURCEMAP === '1' || process.env.SOURCEMAP === 'true'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    ...(ANALYZE ? [
      // Bundle analyzer only when explicitly enabled
      visualizer({
        filename: 'dist/stats.html',
        open: false,
        gzipSize: true,
        brotliSize: true,
      }),
    ] : []),
  ],
  build: {
    // Enable source maps only when needed
    sourcemap: ENABLE_SOURCEMAP,
    // Optimize chunk splitting (review periodically)
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'antd-vendor': ['antd', '@ant-design/icons'],
          'router-vendor': ['react-router-dom'],
          'utils-vendor': ['axios', 'zustand', 'i18next', 'react-i18next'],
          'charts-vendor': ['recharts', 'chart.js', 'react-chartjs-2'],
          'formats-vendor': ['date-fns', 'dayjs'],
          'pdf-vendor': ['jspdf', 'html2pdf.js', 'html2canvas'],
          'excel-vendor': ['xlsx', 'pptxgenjs'],
        },
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId
            ? chunkInfo.facadeModuleId.split('/').pop()?.replace('.tsx', '').replace('.ts', '')
            : 'chunk'
          return `js/${facadeModuleId}-[hash].js`
        },
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || []
          const ext = info[info.length - 1]
          if (/\.(css)$/.test(assetInfo.name || '')) {
            return `css/[name]-[hash].${ext}`
          }
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name || '')) {
            return `images/[name]-[hash].${ext}`
          }
          if (/\.(woff2?|ttf|otf|eot)$/.test(assetInfo.name || '')) {
            return `fonts/[name]-[hash].${ext}`
          }
          return `assets/[name]-[hash].${ext}`
        },
      },
    },
    chunkSizeWarningLimit: 1000,
    cssCodeSplit: true,
    assetsInlineLimit: 0,
    // Use esbuild for faster minification with console/debugger drop in production
    minify: 'esbuild',
    terserOptions: undefined,
    target: 'es2018',
  },
  esbuild: {
    drop: mode === 'production' ? ['console', 'debugger'] : [],
  },
  server: {
    port: 8080,
    host: true,
    hmr: {
      overlay: true,
    },
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'antd',
      '@ant-design/icons',
      'react-router-dom',
      'axios',
      'zustand',
      'i18next',
      'react-i18next',
    ],
    exclude: ['@vite/client', '@vite/env'],
  },
  css: {
    devSourcemap: true,
    postcss: {},
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
      },
    },
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
}))
