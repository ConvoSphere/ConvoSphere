// Cache Manager für intelligentes Caching und Memory Management

export interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  size: number;
  accessCount: number;
  lastAccessed: number;
}

export interface CacheConfig {
  maxSize: number; // Maximum cache size in bytes
  maxEntries: number; // Maximum number of entries
  defaultTTL: number; // Default time to live in milliseconds
  cleanupInterval: number; // Cleanup interval in milliseconds
}

class CacheManager {
  private cache = new Map<string, CacheEntry>();
  private config: CacheConfig;
  private currentSize = 0;
  private cleanupTimer: NodeJS.Timeout | null = null;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: 50 * 1024 * 1024, // 50MB
      maxEntries: 1000,
      defaultTTL: 5 * 60 * 1000, // 5 minutes
      cleanupInterval: 60 * 1000, // 1 minute
      ...config,
    };

    this.startCleanupTimer();
  }

  // Set cache entry
  set<T>(key: string, data: T, ttl?: number): boolean {
    try {
      const entry: CacheEntry<T> = {
        data,
        timestamp: Date.now(),
        ttl: ttl || this.config.defaultTTL,
        size: this.estimateSize(data),
        accessCount: 0,
        lastAccessed: Date.now(),
      };

      // Check if we need to evict entries
      if (this.shouldEvict(entry.size)) {
        this.evictEntries(entry.size);
      }

      // Remove existing entry if it exists
      const existing = this.cache.get(key);
      if (existing) {
        this.currentSize -= existing.size;
      }

      // Add new entry
      this.cache.set(key, entry);
      this.currentSize += entry.size;

      return true;
    } catch (error) {
      console.warn("Cache set failed:", error);
      return false;
    }
  }

  // Get cache entry
  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T>;

    if (!entry) {
      return null;
    }

    // Check if entry is expired
    if (this.isExpired(entry)) {
      this.delete(key);
      return null;
    }

    // Update access statistics
    entry.accessCount++;
    entry.lastAccessed = Date.now();

    return entry.data;
  }

  // Check if key exists and is not expired
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }

    if (this.isExpired(entry)) {
      this.delete(key);
      return false;
    }

    return true;
  }

  // Delete cache entry
  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (entry) {
      this.currentSize -= entry.size;
      this.cache.delete(key);
      return true;
    }
    return false;
  }

  // Clear all cache
  clear(): void {
    this.cache.clear();
    this.currentSize = 0;
  }

  // Get cache statistics
  getStats() {
    const entries = Array.from(this.cache.values());
    const now = Date.now();

    return {
      size: this.currentSize,
      entryCount: this.cache.size,
      maxSize: this.config.maxSize,
      maxEntries: this.config.maxEntries,
      hitRate: this.calculateHitRate(),
      averageAge:
        entries.length > 0
          ? entries.reduce((sum, entry) => sum + (now - entry.timestamp), 0) /
            entries.length
          : 0,
      averageSize:
        entries.length > 0
          ? entries.reduce((sum, entry) => sum + entry.size, 0) / entries.length
          : 0,
    };
  }

  // Cache warming - preload frequently accessed data
  async warmCache(
    keys: string[],
    loader: (key: string) => Promise<any>,
  ): Promise<void> {
    const promises = keys.map(async (key) => {
      if (!this.has(key)) {
        try {
          const data = await loader(key);
          this.set(key, data);
        } catch (error) {
          console.warn(`Failed to warm cache for key ${key}:`, error);
        }
      }
    });

    await Promise.allSettled(promises);
  }

  // Batch operations
  async getBatch<T>(keys: string[]): Promise<Map<string, T | null>> {
    const result = new Map<string, T | null>();

    for (const key of keys) {
      result.set(key, this.get<T>(key));
    }

    return result;
  }

  async setBatch<T>(
    entries: Array<{ key: string; data: T; ttl?: number }>,
  ): Promise<void> {
    for (const { key, data, ttl } of entries) {
      this.set(key, data, ttl);
    }
  }

  // Memory management
  private shouldEvict(newEntrySize: number): boolean {
    return (
      this.currentSize + newEntrySize > this.config.maxSize ||
      this.cache.size >= this.config.maxEntries
    );
  }

  private evictEntries(requiredSpace: number): void {
    const entries = Array.from(this.cache.entries());

    // Sort by LRU (Least Recently Used) and access count
    entries.sort(([, a], [, b]) => {
      const aScore = a.lastAccessed + a.accessCount * 1000;
      const bScore = b.lastAccessed + b.accessCount * 1000;
      return aScore - bScore;
    });

    let freedSpace = 0;
    const toDelete: string[] = [];

    for (const [key, entry] of entries) {
      if (freedSpace >= requiredSpace) break;

      toDelete.push(key);
      freedSpace += entry.size;
    }

    // Delete entries
    toDelete.forEach((key) => this.delete(key));
  }

  private isExpired(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp > entry.ttl;
  }

  private estimateSize(data: any): number {
    try {
      const jsonString = JSON.stringify(data);
      return new Blob([jsonString]).size;
    } catch {
      // Fallback estimation
      return 1024; // 1KB default
    }
  }

  private calculateHitRate(): number {
    // This would need to be implemented with actual hit tracking
    // For now, return a placeholder
    return 0.85; // 85% hit rate placeholder
  }

  private startCleanupTimer(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
    }

    this.cleanupTimer = setInterval(() => {
      this.cleanup();
    }, this.config.cleanupInterval);
  }

  private cleanup(): void {
    const now = Date.now();
    const toDelete: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (this.isExpired(entry)) {
        toDelete.push(key);
      }
    }

    toDelete.forEach((key) => this.delete(key));

    if (toDelete.length > 0) {
      console.log(`Cache cleanup: removed ${toDelete.length} expired entries`);
    }
  }

  // Destroy cache manager
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }
    this.clear();
  }
}

// Specialized cache managers
export const apiCache = new CacheManager({
  maxSize: 10 * 1024 * 1024, // 10MB
  maxEntries: 500,
  defaultTTL: 2 * 60 * 1000, // 2 minutes
});

export const uiCache = new CacheManager({
  maxSize: 5 * 1024 * 1024, // 5MB
  maxEntries: 200,
  defaultTTL: 10 * 60 * 1000, // 10 minutes
});

export const imageCache = new CacheManager({
  maxSize: 20 * 1024 * 1024, // 20MB
  maxEntries: 100,
  defaultTTL: 30 * 60 * 1000, // 30 minutes
});

// Singleton instance
export const cacheManager = new CacheManager();

export default cacheManager;
