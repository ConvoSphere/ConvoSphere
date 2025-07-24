// Get API URL from environment variable or use default
const apiUrl = import.meta.env.VITE_API_URL || "/api";
const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export const config = {
  apiUrl,
  wsUrl,
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
  wsEndpoints: {
    chat: "/api/v1/ws/",
    notifications: "/api/v1/ws/notifications"
  },
  apiEndpoints: {
    auth: "/api/v1/auth",
    users: "/api/v1/users",
    conversations: "/api/v1/conversations",
    chat: "/api/v1/chat",
    tools: "/api/v1/tools",
    assistants: "/api/v1/assistants",
    knowledge: "/api/v1/knowledge",
    health: "/api/v1/health"
  }
};

export default config;
