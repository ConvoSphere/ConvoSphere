// Get API URL from environment variable or use default
const apiUrl =
  process.env.VITE_API_URL || import.meta?.env?.VITE_API_URL || "/api";
const wsUrl =
  process.env.VITE_WS_URL ||
  import.meta?.env?.VITE_WS_URL ||
  "ws://localhost:8000";

export const config = {
  apiUrl,
  wsUrl,
  isDevelopment:
    process.env.NODE_ENV === "development" || import.meta?.env?.DEV,
  isProduction: process.env.NODE_ENV === "production" || import.meta?.env?.PROD,
  enableDebug:
    process.env.VITE_ENABLE_DEBUG === "true" ||
    import.meta?.env?.VITE_ENABLE_DEBUG === "true",
  wsEndpoints: {
    chat: "/api/v1/chat/ws/",
    notifications: "/api/v1/ws/notifications",
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
  },
};

export default config;
