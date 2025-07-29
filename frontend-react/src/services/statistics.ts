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
    try {
      const response = await fetch(`${this.baseUrl}${config.apiEndpoints.statistics}/overview`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching overview stats:", error);
      // Fallback to mock data for development
      return this.getMockOverviewStats();
    }
  }

  async getSystemHealth(token: string): Promise<SystemStats> {
    try {
      const response = await fetch(`${this.baseUrl}${config.apiEndpoints.statistics}/system-health`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching system health:", error);
      return this.getMockSystemStats();
    }
  }

  async getRecentActivity(token: string, limit: number = 10): Promise<ActivityItem[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}${config.apiEndpoints.statistics}/recent-activity?limit=${limit}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching recent activity:", error);
      return this.getMockRecentActivity();
    }
  }

  async getUserStats(token: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}${config.apiEndpoints.statistics}/user`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching user stats:", error);
      return this.getMockUserStats();
    }
  }

  // Mock data for development/fallback
  private getMockOverviewStats(): OverviewStats {
    return {
      systemStats: this.getMockSystemStats(),
      recentActivity: this.getMockRecentActivity(),
      userStats: this.getMockUserStats(),
    };
  }

  private getMockSystemStats(): SystemStats {
    return {
      totalConversations: 156,
      totalMessages: 2847,
      totalDocuments: 89,
      totalAssistants: 12,
      totalTools: 8,
      activeUsers: 23,
      systemHealth: "healthy",
      performance: {
        cpuUsage: 23,
        memoryUsage: 67,
        responseTime: 145,
        uptime: 99.9,
      },
    };
  }

  private getMockRecentActivity(): ActivityItem[] {
    return [
      {
        id: "1",
        type: "conversation",
        title: "Neue Konversation gestartet",
        description: "Chat mit Customer Support Bot",
        timestamp: new Date().toISOString(),
        user: "Max Mustermann",
        metadata: { assistantId: "assistant_1", messageCount: 5 },
      },
      {
        id: "2",
        type: "document",
        title: "Dokument hochgeladen",
        description: "Projektplan.pdf wurde erfolgreich verarbeitet",
        timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        user: "Anna Schmidt",
        metadata: { fileSize: "2.3MB", pages: 15 },
      },
      {
        id: "3",
        type: "assistant",
        title: "Assistent erstellt",
        description: 'Neuer Assistent "Support Bot" wurde konfiguriert',
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        user: "Admin",
        metadata: { model: "gpt-4", tools: ["web_search", "file_reader"] },
      },
      {
        id: "4",
        type: "tool",
        title: "Tool aktiviert",
        description: 'API Connector wurde erfolgreich aktiviert',
        timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
        user: "Admin",
        metadata: { toolType: "api_connector", endpoints: 3 },
      },
      {
        id: "5",
        type: "user",
        title: "Neuer Benutzer registriert",
        description: "Sarah Weber hat sich erfolgreich angemeldet",
        timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
        user: "System",
        metadata: { role: "user", email: "sarah.weber@example.com" },
      },
    ];
  }

  private getMockUserStats() {
    return {
      conversationsThisWeek: 12,
      messagesThisWeek: 89,
      documentsUploaded: 5,
      favoriteAssistant: "Customer Support Bot",
      lastActive: new Date().toISOString(),
      totalUsage: {
        conversations: 45,
        messages: 234,
        documents: 12,
      },
    };
  }
}

export const statisticsService = new StatisticsService();
export default statisticsService;