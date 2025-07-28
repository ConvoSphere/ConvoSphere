/**
 * Offline Service for handling offline functionality and data synchronization.
 * 
 * This service provides:
 * - Offline detection
 * - Data caching
 * - Queue management for offline actions
 * - Synchronization when back online
 */

import React from "react";
import { useAuthStore } from "../store/authStore";

export interface OfflineAction {
  id: string;
  type: string;
  endpoint: string;
  method: string;
  data: any;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
}

export interface CachedData {
  key: string;
  data: any;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

class OfflineService {
  private isOnline: boolean = navigator.onLine;
  private actionQueue: OfflineAction[] = [];
  private cache: Map<string, CachedData> = new Map();
  private syncInProgress: boolean = false;
  private listeners: Set<(online: boolean) => void> = new Set();

  constructor() {
    this.initialize();
  }

  private initialize() {
    // Listen for online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());

    // Load cached data and action queue from localStorage
    this.loadFromStorage();

    // Start periodic sync check
    setInterval(() => this.checkSync(), 30000); // Check every 30 seconds

    // Start cache cleanup
    setInterval(() => this.cleanupCache(), 60000); // Cleanup every minute
  }

  private handleOnline() {
    this.isOnline = true;
    this.notifyListeners(true);
    this.syncOfflineActions();
  }

  private handleOffline() {
    this.isOnline = false;
    this.notifyListeners(false);
  }

  private notifyListeners(online: boolean) {
    this.listeners.forEach(listener => listener(online));
  }

  public addOnlineStatusListener(listener: (online: boolean) => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public isOnlineStatus(): boolean {
    return this.isOnline;
  }

  // Cache Management
  public setCache(key: string, data: any, ttl: number = 3600000) { // Default 1 hour
    const cachedData: CachedData = {
      key,
      data,
      timestamp: Date.now(),
      ttl
    };
    this.cache.set(key, cachedData);
    this.saveCacheToStorage();
  }

  public getCache(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    // Check if cache is expired
    if (Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      this.saveCacheToStorage();
      return null;
    }

    return cached.data;
  }

  public clearCache(key?: string) {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
    this.saveCacheToStorage();
  }

  private cleanupCache() {
    const now = Date.now();
    for (const [key, cached] of this.cache.entries()) {
      if (now - cached.timestamp > cached.ttl) {
        this.cache.delete(key);
      }
    }
    this.saveCacheToStorage();
  }

  // Offline Action Queue
  public queueAction(action: Omit<OfflineAction, 'id' | 'timestamp' | 'retryCount'>): string {
    const offlineAction: OfflineAction = {
      ...action,
      id: this.generateId(),
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: action.maxRetries || 3
    };

    this.actionQueue.push(offlineAction);
    this.saveQueueToStorage();
    return offlineAction.id;
  }

  public getQueuedActions(): OfflineAction[] {
    return [...this.actionQueue];
  }

  public removeQueuedAction(actionId: string): boolean {
    const index = this.actionQueue.findIndex(action => action.id === actionId);
    if (index !== -1) {
      this.actionQueue.splice(index, 1);
      this.saveQueueToStorage();
      return true;
    }
    return false;
  }

  private async syncOfflineActions() {
    if (this.syncInProgress || !this.isOnline || this.actionQueue.length === 0) {
      return;
    }

    this.syncInProgress = true;
    const actionsToSync = [...this.actionQueue];

    try {
      for (const action of actionsToSync) {
        await this.executeQueuedAction(action);
      }
    } catch (error) {
      console.error('Error syncing offline actions:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  private async executeQueuedAction(action: OfflineAction): Promise<boolean> {
    try {
      const { isAuthenticated } = useAuthStore.getState();
      if (!isAuthenticated) {
        // Remove action if user is not authenticated
        this.removeQueuedAction(action.id);
        return false;
      }

      const response = await fetch(action.endpoint, {
        method: action.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: action.method !== 'GET' ? JSON.stringify(action.data) : undefined
      });

      if (response.ok) {
        this.removeQueuedAction(action.id);
        return true;
      } else {
        // Increment retry count
        action.retryCount++;
        if (action.retryCount >= action.maxRetries) {
          this.removeQueuedAction(action.id);
          console.warn(`Action ${action.id} failed permanently after ${action.maxRetries} retries`);
        }
        return false;
      }
    } catch (error) {
      console.error(`Error executing queued action ${action.id}:`, error);
      action.retryCount++;
      if (action.retryCount >= action.maxRetries) {
        this.removeQueuedAction(action.id);
      }
      return false;
    }
  }

  private checkSync() {
    if (this.isOnline && this.actionQueue.length > 0) {
      this.syncOfflineActions();
    }
  }

  // Storage Management
  private saveCacheToStorage() {
    try {
      const cacheData = Array.from(this.cache.entries());
      localStorage.setItem('offline_cache', JSON.stringify(cacheData));
    } catch (error) {
      console.error('Error saving cache to storage:', error);
    }
  }

  private saveQueueToStorage() {
    try {
      localStorage.setItem('offline_queue', JSON.stringify(this.actionQueue));
    } catch (error) {
      console.error('Error saving queue to storage:', error);
    }
  }

  private loadFromStorage() {
    try {
      // Load cache
      const cacheData = localStorage.getItem('offline_cache');
      if (cacheData) {
        const parsed = JSON.parse(cacheData);
        this.cache = new Map(parsed);
      }

      // Load action queue
      const queueData = localStorage.getItem('offline_queue');
      if (queueData) {
        this.actionQueue = JSON.parse(queueData);
      }
    } catch (error) {
      console.error('Error loading from storage:', error);
      // Clear corrupted data
      localStorage.removeItem('offline_cache');
      localStorage.removeItem('offline_queue');
    }
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  // Utility Methods
  public getOfflineStats() {
    return {
      isOnline: this.isOnline,
      queuedActions: this.actionQueue.length,
      cacheSize: this.cache.size,
      syncInProgress: this.syncInProgress
    };
  }

  public clearAllData() {
    this.actionQueue = [];
    this.cache.clear();
    localStorage.removeItem('offline_cache');
    localStorage.removeItem('offline_queue');
  }
}

// Global offline service instance
export const offlineService = new OfflineService();

// React Hook for offline status
export const useOfflineStatus = () => {
  const [isOnline, setIsOnline] = React.useState(offlineService.isOnlineStatus());

  React.useEffect(() => {
    const unsubscribe = offlineService.addOnlineStatusListener(setIsOnline);
    return unsubscribe;
  }, []);

  return isOnline;
};

// Enhanced API wrapper for offline support
export class OfflineAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Check if we're online
    if (offlineService.isOnlineStatus()) {
      try {
        const response = await fetch(url, options);
        
        // Cache successful GET requests
        if (response.ok && options.method === 'GET') {
          const data = await response.clone().json();
          offlineService.setCache(endpoint, data);
        }
        
        return response;
      } catch (error) {
        // If request fails and it's a GET, try to return cached data
        if (options.method === 'GET') {
          const cached = offlineService.getCache(endpoint);
          if (cached) {
            return new Response(JSON.stringify(cached), {
              status: 200,
              headers: { 'Content-Type': 'application/json' }
            });
          }
        }
        throw error;
      }
    } else {
      // Offline mode
      if (options.method === 'GET') {
        const cached = offlineService.getCache(endpoint);
        if (cached) {
          return new Response(JSON.stringify(cached), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
          });
        }
        throw new Error('No cached data available offline');
      } else {
        // Queue non-GET requests for later sync
        const actionId = offlineService.queueAction({
          type: 'api_request',
          endpoint: url,
          method: options.method || 'GET',
          data: options.body ? JSON.parse(options.body as string) : null,
          maxRetries: 3
        });
        
        return new Response(JSON.stringify({ 
          queued: true, 
          actionId,
          message: 'Action queued for offline sync' 
        }), {
          status: 202,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }
  }

  async get(endpoint: string): Promise<Response> {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint: string, data: any): Promise<Response> {
    return this.request(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  }

  async put(endpoint: string, data: any): Promise<Response> {
    return this.request(endpoint, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  }

  async delete(endpoint: string): Promise<Response> {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Export the enhanced API instance
export const offlineAPI = new OfflineAPI(import.meta.env.VITE_API_URL || 'http://localhost:8000');