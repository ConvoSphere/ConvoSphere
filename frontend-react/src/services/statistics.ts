import { config } from "../config";

export interface SystemStats {
  totalConversations: number;
  totalMessages: number;
  totalDocuments: number;
  totalAssistants: number;
  totalTools: number;
  activeUsers: number;
  systemHealth: "healthy" | "warning" | "error";
  performance: {
    cpuUsage: number;
    memoryUsage: number;
    responseTime: number;
    uptime: number;
  };
}

export interface ActivityItem {
  id: string;
  type: "conversation" | "document" | "assistant" | "tool" | "user" | "system";
  title: string;
  description?: string;
  timestamp: string;
  user: string;
  metadata?: Record<string, any>;
}

export interface OverviewStats {
  systemStats: SystemStats;
  recentActivity: ActivityItem[];
  userStats?: {
    conversationsThisWeek: number;
    messagesThisWeek: number;
    documentsUploaded: number;
    favoriteAssistant: string;
  };
}

class StatisticsService {
  private baseUrl = config.apiUrl;

  async getOverviewStats(token: string): Promise<OverviewStats> {
    const response = await fetch(
      `${this.baseUrl}${config.apiEndpoints.statistics}/overview`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }

  async getSystemHealth(token: string): Promise<SystemStats> {
    const response = await fetch(
      `${this.baseUrl}${config.apiEndpoints.statistics}/system-health`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }

  async getRecentActivity(
    token: string,
    limit: number = 10,
  ): Promise<ActivityItem[]> {
    const response = await fetch(
      `${this.baseUrl}${config.apiEndpoints.statistics}/recent-activity?limit=${limit}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }

  async getUserStats(token: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}${config.apiEndpoints.statistics}/user`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }
}

export const statisticsService = new StatisticsService();
export default statisticsService;
