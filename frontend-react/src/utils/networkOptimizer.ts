// Network Optimizer für Request Batching, Retry Logic und Connection Quality

export interface NetworkConfig {
  maxRetries: number;
  retryDelay: number;
  timeout: number;
  batchSize: number;
  batchDelay: number;
  offlineTimeout: number;
}

export interface RequestConfig {
  url: string;
  method: string;
  data?: any;
  headers?: Record<string, string>;
  retries?: number;
  timeout?: number;
  priority?: 'high' | 'normal' | 'low';
}

export interface BatchRequest {
  id: string;
  config: RequestConfig;
  resolve: (value: any) => void;
  reject: (error: any) => void;
  timestamp: number;
  priority: 'high' | 'normal' | 'low';
}

class NetworkOptimizer {
  private config: NetworkConfig;
  private requestQueue: BatchRequest[] = [];
  private batchTimer: NodeJS.Timeout | null = null;
  private isOnline = navigator.onLine;
  private connectionQuality: 'fast' | 'slow' | 'offline' = 'fast';
  private pendingRequests = new Map<string, BatchRequest>();

  constructor(config: Partial<NetworkConfig> = {}) {
    this.config = {
      maxRetries: 3,
      retryDelay: 1000,
      timeout: 10000,
      batchSize: 10,
      batchDelay: 50,
      offlineTimeout: 5000,
      ...config,
    };

    this.setupNetworkListeners();
    this.startBatchProcessor();
  }

  // Setup network event listeners
  private setupNetworkListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.connectionQuality = 'fast';
      this.processOfflineQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.connectionQuality = 'offline';
    });

    // Monitor connection quality
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', () => {
        this.updateConnectionQuality(connection);
      });
      this.updateConnectionQuality(connection);
    }
  }

  private updateConnectionQuality(connection: any) {
    if (connection.effectiveType === '4g') {
      this.connectionQuality = 'fast';
    } else if (connection.effectiveType === '3g' || connection.effectiveType === '2g') {
      this.connectionQuality = 'slow';
    } else {
      this.connectionQuality = 'fast';
    }
  }

  // Main request method
  async request<T>(config: RequestConfig): Promise<T> {
    if (!this.isOnline) {
      return this.handleOfflineRequest(config);
    }

    // High priority requests go directly
    if (config.priority === 'high') {
      return this.executeRequest(config);
    }

    // Normal and low priority requests are batched
    return this.queueRequest(config);
  }

  // Execute a single request with retry logic
  private async executeRequest<T>(config: RequestConfig): Promise<T> {
    const maxRetries = config.retries ?? this.config.maxRetries;
    const timeout = config.timeout ?? this.config.timeout;
    let lastError: Error;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(config.url, {
          method: config.method,
          headers: {
            'Content-Type': 'application/json',
            ...config.headers,
          },
          body: config.data ? JSON.stringify(config.data) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        lastError = error as Error;
        
        // Don't retry on certain errors
        if (this.shouldNotRetry(error as Error)) {
          throw error;
        }

        // Wait before retry (exponential backoff)
        if (attempt < maxRetries) {
          const delay = this.config.retryDelay * Math.pow(2, attempt);
          await this.delay(delay);
        }
      }
    }

    throw lastError!;
  }

  // Queue request for batching
  private async queueRequest<T>(config: RequestConfig): Promise<T> {
    return new Promise((resolve, reject) => {
      const request: BatchRequest = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        config,
        resolve,
        reject,
        timestamp: Date.now(),
        priority: config.priority || 'normal',
      };

      this.requestQueue.push(request);
      this.scheduleBatch();
    });
  }

  // Schedule batch processing
  private scheduleBatch() {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
    }

    this.batchTimer = setTimeout(() => {
      this.processBatch();
    }, this.config.batchDelay);
  }

  // Process batched requests
  private async processBatch() {
    if (this.requestQueue.length === 0) return;

    // Sort by priority and timestamp
    this.requestQueue.sort((a, b) => {
      const priorityOrder = { high: 3, normal: 2, low: 1 };
      const aPriority = priorityOrder[a.priority];
      const bPriority = priorityOrder[b.priority];
      
      if (aPriority !== bPriority) {
        return bPriority - aPriority;
      }
      
      return a.timestamp - b.timestamp;
    });

    // Take batch
    const batch = this.requestQueue.splice(0, this.config.batchSize);
    
    // Execute batch
    const promises = batch.map(request => this.executeRequest(request.config));
    
    try {
      const results = await Promise.allSettled(promises);
      
      // Resolve/reject each request
      batch.forEach((request, index) => {
        const result = results[index];
        if (result.status === 'fulfilled') {
          request.resolve(result.value);
        } else {
          request.reject(result.reason);
        }
      });
    } catch (error) {
      // If batch fails, reject all requests
      batch.forEach(request => {
        request.reject(error);
      });
    }
  }

  // Handle offline requests
  private async handleOfflineRequest<T>(config: RequestConfig): Promise<T> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error('Request timeout - offline'));
      }, this.config.offlineTimeout);

      // Store for later processing
      const request: BatchRequest = {
        id: `offline-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        config,
        resolve: (value) => {
          clearTimeout(timeoutId);
          resolve(value);
        },
        reject: (error) => {
          clearTimeout(timeoutId);
          reject(error);
        },
        timestamp: Date.now(),
        priority: config.priority || 'normal',
      };

      this.pendingRequests.set(request.id, request);
    });
  }

  // Process offline queue when back online
  private async processOfflineQueue() {
    const offlineRequests = Array.from(this.pendingRequests.values());
    this.pendingRequests.clear();

    for (const request of offlineRequests) {
      try {
        const result = await this.executeRequest(request.config);
        request.resolve(result);
      } catch (error) {
        request.reject(error);
      }
    }
  }

  // Batch multiple requests into a single API call
  async batchRequests<T>(requests: RequestConfig[]): Promise<T[]> {
    if (requests.length === 0) return [];

    // Group by endpoint
    const groups = new Map<string, RequestConfig[]>();
    requests.forEach(request => {
      const baseUrl = this.getBaseUrl(request.url);
      if (!groups.has(baseUrl)) {
        groups.set(baseUrl, []);
      }
      groups.get(baseUrl)!.push(request);
    });

    // Execute each group
    const results: T[] = [];
    for (const [baseUrl, groupRequests] of groups) {
      try {
        const batchResponse = await this.executeBatchRequest(baseUrl, groupRequests);
        results.push(...batchResponse);
      } catch (error) {
        // Fallback to individual requests
        const individualResults = await Promise.allSettled(
          groupRequests.map(req => this.executeRequest(req))
        );
        individualResults.forEach(result => {
          if (result.status === 'fulfilled') {
            results.push(result.value);
          }
        });
      }
    }

    return results;
  }

  // Execute batch request (customize based on your API)
  private async executeBatchRequest<T>(baseUrl: string, requests: RequestConfig[]): Promise<T[]> {
    const batchData = requests.map((req, index) => ({
      id: index,
      method: req.method,
      path: req.url.replace(baseUrl, ''),
      data: req.data,
      headers: req.headers,
    }));

    const response = await fetch(`${baseUrl}/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ requests: batchData }),
    });

    if (!response.ok) {
      throw new Error(`Batch request failed: ${response.statusText}`);
    }

    const batchResponse = await response.json();
    return batchResponse.results;
  }

  // Utility methods
  private shouldNotRetry(error: Error): boolean {
    // Don't retry on client errors (4xx) except 408, 429
    if (error.message.includes('HTTP 4')) {
      const status = parseInt(error.message.match(/HTTP (\d+)/)?.[1] || '0');
      return ![408, 429].includes(status);
    }
    
    // Don't retry on network errors that won't be resolved by retrying
    return error.name === 'AbortError' || error.name === 'TypeError';
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getBaseUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      return `${urlObj.protocol}//${urlObj.host}`;
    } catch {
      return url;
    }
  }

  private startBatchProcessor() {
    // Process any remaining requests periodically
    setInterval(() => {
      if (this.requestQueue.length > 0) {
        this.processBatch();
      }
    }, 1000);
  }

  // Get network status
  getNetworkStatus() {
    return {
      isOnline: this.isOnline,
      connectionQuality: this.connectionQuality,
      queueLength: this.requestQueue.length,
      pendingRequests: this.pendingRequests.size,
    };
  }

  // Clear all pending requests
  clearQueue() {
    this.requestQueue.forEach(request => {
      request.reject(new Error('Request cancelled'));
    });
    this.requestQueue = [];
    
    this.pendingRequests.forEach(request => {
      request.reject(new Error('Request cancelled'));
    });
    this.pendingRequests.clear();
  }

  // Destroy optimizer
  destroy() {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }
    this.clearQueue();
  }
}

// Singleton instance
export const networkOptimizer = new NetworkOptimizer();

export default networkOptimizer;