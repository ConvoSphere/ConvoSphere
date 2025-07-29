// Jest environment setup
process.env.NODE_ENV = 'test';
process.env.VITE_API_URL = 'http://localhost:8000';
process.env.VITE_WS_URL = 'ws://localhost:8000';
process.env.VITE_ENABLE_DEBUG = 'false';

// Mock import.meta for tests
global.import = {
  meta: {
    env: {
      VITE_API_URL: 'http://localhost:8000',
      VITE_WS_URL: 'ws://localhost:8000',
      VITE_ENABLE_DEBUG: 'false',
      DEV: false,
      PROD: false
    }
  }
};