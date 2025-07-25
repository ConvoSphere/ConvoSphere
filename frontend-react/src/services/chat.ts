import config from '../config';
import { Document } from './knowledge';

export interface ChatMessage {
  id?: string;
  sender: string;
  text: string;
  timestamp?: Date;
  documents?: Document[]; // Knowledge Base documents used for this response
  messageType?: 'text' | 'knowledge' | 'error' | 'system';
  metadata?: {
    searchQuery?: string;
    contextChunks?: number;
    confidence?: number;
    processingTime?: number;
  };
}

export interface KnowledgeContext {
  enabled: boolean;
  documentIds?: string[];
  searchQuery?: string;
  maxChunks?: number;
  filters?: {
    tags?: string[];
    documentTypes?: string[];
    dateRange?: {
      start: string;
      end: string;
    };
  };
}

export interface ChatWebSocketMessage {
  type: 'message' | 'knowledge_search' | 'typing' | 'ping' | 'knowledge_update' | 'processing_job_update' | 'pong' | 'error';
  data: {
    content?: string;
    knowledgeContext?: KnowledgeContext;
    isTyping?: boolean;
    documents?: Document[];
    searchQuery?: string;
    processingJobId?: string;
    id?: string;
    role?: string;
    timestamp?: string;
    messageType?: string;
    metadata?: any;
    status?: string;
    progress?: number;
    message?: string;
  };
}

export interface WorkerMessage {
  type: string;
  data: unknown;
  id: string;
}

export interface WorkerResponse {
  type: 'success' | 'error' | 'ready';
  data: unknown;
  id: string;
  workerId: string;
  timestamp: number;
}

export interface WorkerTask {
  id: string;
  type: string;
  data: unknown;
  resolve: (value: unknown) => void;
  reject: (error: unknown) => void;
  timestamp: number;
  timeout: number;
}

type MessageHandler = (msg: ChatMessage) => void;
type KnowledgeUpdateHandler = (documents: Document[], searchQuery: string) => void;
type ProcessingJobHandler = (jobId: string, status: string, progress: number) => void;

class ChatWebSocket {
  private ws: WebSocket | null = null;
  private messageHandler: MessageHandler | null = null;
  private knowledgeUpdateHandler: KnowledgeUpdateHandler | null = null;
  private processingJobHandler: ProcessingJobHandler | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private pingInterval: NodeJS.Timeout | null = null;
  private isConnecting = false;

  private isChatWebSocketMessage(data: unknown): data is ChatWebSocketMessage {
    return typeof data === 'object' && data !== null && 'type' in data && 'data' in data;
  }

  connect(token: string, conversationId: string, onMessage: MessageHandler, onKnowledgeUpdate?: KnowledgeUpdateHandler, onProcessingJob?: ProcessingJobHandler) {
    if (this.isConnecting) return;
    
    this.isConnecting = true;
    this.messageHandler = onMessage;
    this.knowledgeUpdateHandler = onKnowledgeUpdate || null;
    this.processingJobHandler = onProcessingJob || null;
    
    const wsUrl = `${config.wsUrl}${config.wsEndpoints.chat}${conversationId}?token=${token}`;
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.startPingInterval();
    };
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.isConnecting = false;
      this.stopPingInterval();
      
      // Attempt reconnection if not a normal closure
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.attemptReconnect(token, conversationId);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.isConnecting = false;
    };
  }

  private handleMessage(data: unknown) {
    if (!this.isChatWebSocketMessage(data)) {
      console.error('Received invalid WebSocket message:', data);
      return;
    }
    const { type, data: messageData } = data;
    
    switch (type) {
      case 'message':
        if (this.messageHandler && messageData.content) {
          const chatMessage: ChatMessage = {
            id: messageData.id || undefined,
            sender: messageData.role === 'user' ? 'You' : 'Assistant',
            text: messageData.content,
            timestamp: messageData.timestamp ? new Date(messageData.timestamp) : new Date(),
            documents: messageData.documents || [],
            messageType: (messageData.messageType as 'text' | 'knowledge' | 'error' | 'system') || 'text',
            metadata: messageData.metadata
          };
          this.messageHandler(chatMessage);
        }
        break;
        
      case 'knowledge_update':
        if (this.knowledgeUpdateHandler && messageData.documents) {
          this.knowledgeUpdateHandler(messageData.documents, messageData.searchQuery || '');
        }
        break;
        
      case 'processing_job_update':
        if (this.processingJobHandler && messageData.processingJobId && messageData.status) {
          this.processingJobHandler(
            messageData.processingJobId,
            messageData.status,
            messageData.progress || 0
          );
        }
        break;
        
      case 'pong':
        // Handle ping response
        break;
        
      case 'error':
        if (this.messageHandler) {
          const errorMessage: ChatMessage = {
            sender: 'System',
            text: (messageData as any).message || 'An error occurred',
            messageType: 'error',
            timestamp: new Date()
          };
          this.messageHandler(errorMessage);
        }
        break;
        
      default:
        console.log('Unknown message type:', type);
    }
  }

  private attemptReconnect(token: string, conversationId: string) {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
            setTimeout(() => {
          if (this.messageHandler) {
            this.connect(token, conversationId, this.messageHandler, this.knowledgeUpdateHandler || undefined, this.processingJobHandler || undefined);
          }
        }, delay);
  }

  private startPingInterval() {
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping', data: {} });
    }, 30000); // Ping every 30 seconds
  }

  private stopPingInterval() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  send(message: ChatWebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  sendMessage(text: string, knowledgeContext?: KnowledgeContext) {
    const message: ChatWebSocketMessage = {
      type: 'message',
      data: {
        content: text,
        knowledgeContext
      }
    };
    this.send(message);
  }

  sendKnowledgeSearch(searchQuery: string, filters?: any) {
    const message: ChatWebSocketMessage = {
      type: 'knowledge_search',
      data: {
        searchQuery,
        knowledgeContext: {
          enabled: true,
          searchQuery,
          filters
        }
      }
    };
    this.send(message);
  }

  sendTypingIndicator(isTyping: boolean) {
    const message: ChatWebSocketMessage = {
      type: 'typing',
      data: {
        isTyping
      }
    };
    this.send(message);
  }

  disconnect() {
    this.stopPingInterval();
    if (this.ws) {
      this.ws.close(1000, 'User disconnected');
      this.ws = null;
    }
    this.messageHandler = null;
    this.knowledgeUpdateHandler = null;
    this.processingJobHandler = null;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export const chatWebSocket = new ChatWebSocket(); 