// Get API URL from environment variable or use default
const getEnvVar = (key: string, defaultValue: string): string => {
  // Check if we're in a test environment
  if (typeof process !== 'undefined' && process.env.NODE_ENV === 'test') {
    return process.env[key] || defaultValue;
  }
  
  // Check for Vite environment variables
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env[key] || process.env[key] || defaultValue;
  }
  
  // Fallback to process.env
  return process.env[key] || defaultValue;
};

const apiUrl = getEnvVar('VITE_API_URL', 'http://localhost:8000');
const wsUrl = getEnvVar('VITE_WS_URL', 'ws://localhost:8000');

export const config = {
  apiUrl,
  wsUrl,
  isDevelopment:
    process.env.NODE_ENV === "development" || 
    (typeof import.meta !== 'undefined' && import.meta.env?.DEV),
  isProduction: 
    process.env.NODE_ENV === "production" || 
    (typeof import.meta !== 'undefined' && import.meta.env?.PROD),
  enableDebug:
    getEnvVar('VITE_ENABLE_DEBUG', 'false') === 'true',
  wsEndpoints: {
    chat: "/api/v1/chat/ws/",
    notifications: "/api/v1/ws/notifications",
    realtime: "/api/v1/ws",
  },
  apiEndpoints: {
    auth: "/api/v1/auth",
    users: "/api/v1/users",
    conversations: "/api/v1/conversations",
    chat: "/api/v1/chat",
    tools: "/api/v1/tools",
    assistants: "/api/v1/assistants",
    knowledge: "/api/v1/knowledge",
    health: "/api/v1/health",
    statistics: "/api/v1/statistics",
    intelligence: "/api/v1/intelligence",
    domainGroups: "/api/v1/domain-groups",
    monitoring: "/api/v1/monitoring",
    search: "/api/v1/search",
    rag: "/api/v1/rag",
  },
};

export default config;
