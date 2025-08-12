import { config } from "../config";

export interface RealtimeEvent {
  type:
    | "stats_update"
    | "system_health"
    | "activity"
    | "user_status"
    | "notification";
  data: any;
  timestamp: string;
}

export interface StatsUpdate {
  totalConversations: number;
  totalMessages: number;
  totalDocuments: number;
  totalAssistants: number;
  totalTools: number;
  activeUsers: number;
}

export interface SystemHealthUpdate {
  status: "healthy" | "warning" | "error";
  performance: {
    cpuUsage: number;
    memoryUsage: number;
    responseTime: number;
    uptime: number;
  };
  alerts: Array<{
    id: string;
    level: "info" | "warning" | "error";
    message: string;
    timestamp: string;
  }>;
}

export interface ActivityUpdate {
  id: string;
  type: "conversation" | "document" | "assistant" | "tool" | "user" | "system";
  title: string;
  description?: string;
  user: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface UserStatusUpdate {
  userId: string;
  username: string;
  status: "online" | "offline" | "away" | "busy";
  lastActivity: string;
}

export interface NotificationUpdate {
  id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
}

class RealtimeService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private eventListeners: Map<string, Set<(event: RealtimeEvent) => void>> =
    new Map();
  private isConnecting = false;
  private token: string | null = null;

  constructor() {
    this.handleMessage = this.handleMessage.bind(this);
    this.handleError = this.handleError.bind(this);
    this.handleClose = this.handleClose.bind(this);
  }

  connect(token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error("Connection already in progress"));
        return;
      }

      this.isConnecting = true;
      this.token = token;

      try {
        const wsUrl = config.wsUrl || config.apiUrl.replace("http", "ws");
        this.ws = new WebSocket(
          `${wsUrl}${config.wsEndpoints.realtime}?token=${token}`,
        );

        this.ws.onopen = () => {
          console.log("Realtime WebSocket connected");
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = this.handleMessage;
        this.ws.onerror = this.handleError;
        this.ws.onclose = this.handleClose;

        // Timeout for connection
        setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            reject(new Error("Connection timeout"));
          }
        }, 10000);
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.isConnecting = false;
    this.eventListeners.clear();
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  subscribe(
    eventType: string,
    callback: (event: RealtimeEvent) => void,
  ): () => void {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, new Set());
    }

    this.eventListeners.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      const listeners = this.eventListeners.get(eventType);
      if (listeners) {
        listeners.delete(callback);
        if (listeners.size === 0) {
          this.eventListeners.delete(eventType);
        }
      }
    };
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const realtimeEvent: RealtimeEvent = JSON.parse(event.data);

      // Emit to all listeners for this event type
      const listeners = this.eventListeners.get(realtimeEvent.type);
      if (listeners) {
        listeners.forEach((callback) => {
          try {
            callback(realtimeEvent);
          } catch (error) {
            console.error("Error in realtime event listener:", error);
          }
        });
      }

      // Also emit to general listeners
      const generalListeners = this.eventListeners.get("*");
      if (generalListeners) {
        generalListeners.forEach((callback) => {
          try {
            callback(realtimeEvent);
          } catch (error) {
            console.error("Error in general realtime event listener:", error);
          }
        });
      }
    } catch (error) {
      console.error("Error parsing realtime message:", error);
    }
  }

  private handleError(error: Event): void {
    console.error("Realtime WebSocket error:", error);
    this.isConnecting = false;
  }

  private handleClose(event: CloseEvent): void {
    console.log("Realtime WebSocket closed:", event.code, event.reason);
    this.isConnecting = false;

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    // Attempt to reconnect if not a normal closure
    if (
      event.code !== 1000 &&
      this.reconnectAttempts < this.maxReconnectAttempts
    ) {
      this.attemptReconnect();
    }
  }

  private attemptReconnect(): void {
    if (this.isConnecting || !this.token) return;

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`,
    );

    setTimeout(() => {
      if (this.token) {
        this.connect(this.token).catch((error) => {
          console.error("Reconnection failed:", error);
        });
      }
    }, delay);
  }

  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(
          JSON.stringify({ type: "ping", timestamp: new Date().toISOString() }),
        );
      }
    }, 30000); // Send ping every 30 seconds
  }

  // Convenience methods for specific event types
  onStatsUpdate(callback: (stats: StatsUpdate) => void): () => void {
    return this.subscribe("stats_update", (event) => callback(event.data));
  }

  onSystemHealth(callback: (health: SystemHealthUpdate) => void): () => void {
    return this.subscribe("system_health", (event) => callback(event.data));
  }

  onActivity(callback: (activity: ActivityUpdate) => void): () => void {
    return this.subscribe("activity", (event) => callback(event.data));
  }

  onUserStatus(callback: (status: UserStatusUpdate) => void): () => void {
    return this.subscribe("user_status", (event) => callback(event.data));
  }

  onNotification(
    callback: (notification: NotificationUpdate) => void,
  ): () => void {
    return this.subscribe("notification", (event) => callback(event.data));
  }

  onAnyEvent(callback: (event: RealtimeEvent) => void): () => void {
    return this.subscribe("*", callback);
  }
}

export const realtimeService = new RealtimeService();
export default realtimeService;
