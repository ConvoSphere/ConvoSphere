/**
 * Frontend configuration management
 * Centralizes all environment variables and provides fallbacks
 */

export const config = {
  // API Configuration
  apiUrl: import.meta.env.VITE_API_URL || '/api',
  wsUrl: import.meta.env.VITE_WS_URL || 
    (import.meta.env.DEV ? 'ws://localhost:8000' : `ws://${window.location.host}`),
  
  // Environment
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  
  // Feature flags
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
  
  // WebSocket endpoints
  wsEndpoints: {
    chat: '/api/v1/ws/chat',
    notifications: '/api/v1/ws/notifications',
  },
  
  // API endpoints
  apiEndpoints: {
    auth: '/api/v1/auth',
    users: '/api/v1/users',
    conversations: '/api/v1/conversations',
    chat: '/api/v1/chat',
    tools: '/api/v1/tools',
    assistants: '/api/v1/assistants',
    knowledge: '/api/v1/knowledge',
    health: '/api/v1/health',
  },
} as const;

export default config; 