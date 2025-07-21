import { store } from '../app/store'
import { logout } from '../features/auth/authSlice'

export interface WebSocketMessage<T = unknown> {
  type: 'message' | 'conversation_update' | 'user_typing' | 'error'
  data: T
  conversation_id?: string
  user_id?: string
}

export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  created_at: string
  conversation_id: string
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageQueue: WebSocketMessage[] = []
  private listeners: Map<string, Set<(message: WebSocketMessage) => void>> = new Map()
  private isConnecting = false

  constructor() {
    this.handleVisibilityChange = this.handleVisibilityChange.bind(this)
    document.addEventListener('visibilitychange', this.handleVisibilityChange)
  }

  private getWebSocketUrl(): string {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    const wsUrl = baseUrl.replace('http', 'ws')
    const token = store.getState().auth.accessToken
    
    if (!token) {
      throw new Error('No authentication token available')
    }
    
    return `${wsUrl}/ws/chat?token=${token}`
  }

  public connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return Promise.resolve()
    }

    this.isConnecting = true

    return new Promise((resolve, reject) => {
      try {
        const url = this.getWebSocketUrl()
        this.ws = new WebSocket(url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.flushMessageQueue()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnecting = false
          
          if (event.code === 4001) {
            // Authentication error
            store.dispatch(logout())
            return
          }
          
          this.handleReconnect()
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          reject(error)
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'User initiated disconnect')
      this.ws = null
    }
    this.messageQueue = []
    this.listeners.clear()
  }

  public sendMessage(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      this.messageQueue.push(message)
      this.connect().catch(console.error)
    }
  }

  public subscribe(eventType: string, callback: (message: WebSocketMessage) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    
    this.listeners.get(eventType)!.add(callback)
    
    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType)
      if (listeners) {
        listeners.delete(callback)
        if (listeners.size === 0) {
          this.listeners.delete(eventType)
        }
      }
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const listeners = this.listeners.get(message.type)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(message)
        } catch (error) {
          console.error('Error in WebSocket message handler:', error)
        }
      })
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      this.connect().catch(console.error)
    }, delay)
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      if (message && this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(message))
      }
    }
  }

  private handleVisibilityChange(): void {
    if (document.visibilityState === 'visible' && !this.ws) {
      this.connect().catch(console.error)
    }
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  public getConnectionState(): string {
    if (!this.ws) return 'disconnected'
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'closed'
      default: return 'unknown'
    }
  }
}

// Export singleton instance
export const websocketService = new WebSocketService() 