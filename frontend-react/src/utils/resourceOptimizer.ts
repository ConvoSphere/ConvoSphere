// Resource Optimizer für Image Optimization, Lazy Loading und Resource Prioritization

export interface ResourceConfig {
  enableLazyLoading: boolean;
  enablePreloading: boolean;
  enableImageOptimization: boolean;
  enableResourceHints: boolean;
  maxConcurrentLoads: number;
  preloadDistance: number;
}

export interface ImageConfig {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'avif' | 'jpg' | 'png';
  lazy?: boolean;
  priority?: 'high' | 'normal' | 'low';
}

export interface PreloadConfig {
  href: string;
  as: 'script' | 'style' | 'image' | 'font' | 'fetch';
  type?: string;
  crossorigin?: string;
  media?: string;
}

class ResourceOptimizer {
  private config: ResourceConfig;
  private loadingQueue: Array<{ resource: string; priority: number; resolve: () => void }> = [];
  private activeLoads = 0;
  private loadedResources = new Set<string>();
  private intersectionObserver: IntersectionObserver | null = null;
  private isInitialized = false;

  constructor(config: Partial<ResourceConfig> = {}) {
    this.config = {
      enableLazyLoading: true,
      enablePreloading: true,
      enableImageOptimization: true,
      enableResourceHints: true,
      maxConcurrentLoads: 6,
      preloadDistance: 100,
      ...config,
    };
  }

  init() {
    if (this.isInitialized) return;

    this.setupLazyLoading();
    this.setupResourceHints();
    this.processQueue();

    this.isInitialized = true;
    console.log('Resource Optimizer initialized');
  }

  // Image Optimization
  optimizeImage(config: ImageConfig): string {
    if (!this.config.enableImageOptimization) {
      return config.src;
    }

    const url = new URL(config.src, window.location.origin);
    
    // Add optimization parameters
    if (config.width) {
      url.searchParams.set('w', config.width.toString());
    }
    if (config.height) {
      url.searchParams.set('h', config.height.toString());
    }
    if (config.quality) {
      url.searchParams.set('q', config.quality.toString());
    }
    if (config.format) {
      url.searchParams.set('f', config.format);
    }

    // Add WebP/AVIF support detection
    if (this.supportsWebP() && config.format !== 'avif') {
      url.searchParams.set('webp', '1');
    }
    if (this.supportsAVIF() && config.format === 'avif') {
      url.searchParams.set('avif', '1');
    }

    return url.toString();
  }

  // Lazy Loading Setup
  private setupLazyLoading() {
    if (!this.config.enableLazyLoading || !('IntersectionObserver' in window)) {
      return;
    }

    this.intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const element = entry.target as HTMLElement;
            this.loadLazyResource(element);
            this.intersectionObserver?.unobserve(element);
          }
        });
      },
      {
        rootMargin: `${this.config.preloadDistance}px`,
        threshold: 0.1,
      }
    );

    // Observe existing lazy elements
    this.observeLazyElements();
  }

  private observeLazyElements() {
    const lazyElements = document.querySelectorAll('[data-lazy], [loading="lazy"]');
    lazyElements.forEach((element) => {
      this.intersectionObserver?.observe(element);
    });
  }

  private loadLazyResource(element: HTMLElement) {
    const src = element.getAttribute('data-src') || element.getAttribute('src');
    if (!src) return;

    const priority = this.getPriority(element);
    this.queueResource(src, priority);
  }

  // Resource Queue Management
  private queueResource(resource: string, priority: number) {
    if (this.loadedResources.has(resource)) {
      return Promise.resolve();
    }

    return new Promise<void>((resolve) => {
      this.loadingQueue.push({ resource, priority, resolve });
      this.loadingQueue.sort((a, b) => b.priority - a.priority);
      this.processQueue();
    });
  }

  private async processQueue() {
    while (this.loadingQueue.length > 0 && this.activeLoads < this.config.maxConcurrentLoads) {
      const item = this.loadingQueue.shift();
      if (!item) break;

      this.activeLoads++;
      
      try {
        await this.loadResource(item.resource);
        this.loadedResources.add(item.resource);
        item.resolve();
      } catch (error) {
        console.warn(`Failed to load resource: ${item.resource}`, error);
        item.resolve(); // Resolve anyway to prevent blocking
      } finally {
        this.activeLoads--;
        this.processQueue(); // Process next item
      }
    }
  }

  private async loadResource(resource: string): Promise<void> {
    const url = new URL(resource, window.location.origin);
    
    // Handle different resource types
    if (url.pathname.match(/\.(jpg|jpeg|png|gif|webp|avif|svg)$/i)) {
      return this.loadImage(resource);
    } else if (url.pathname.match(/\.(css)$/i)) {
      return this.loadStylesheet(resource);
    } else if (url.pathname.match(/\.(js)$/i)) {
      return this.loadScript(resource);
    } else {
      return this.loadFetch(resource);
    }
  }

  private loadImage(src: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve();
      img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
      img.src = src;
    });
  }

  private loadStylesheet(href: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.onload = () => resolve();
      link.onerror = () => reject(new Error(`Failed to load stylesheet: ${href}`));
      document.head.appendChild(link);
    });
  }

  private loadScript(src: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
      document.head.appendChild(script);
    });
  }

  private loadFetch(url: string): Promise<void> {
    return fetch(url, { method: 'HEAD' }).then(() => {});
  }

  // Preloading
  preloadResources(configs: PreloadConfig[]) {
    if (!this.config.enablePreloading) return;

    configs.forEach((config) => {
      this.addPreloadLink(config);
    });
  }

  private addPreloadLink(config: PreloadConfig) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = config.href;
    link.as = config.as;
    
    if (config.type) link.type = config.type;
    if (config.crossorigin) link.crossOrigin = config.crossorigin;
    if (config.media) link.media = config.media;

    document.head.appendChild(link);
  }

  // Resource Hints
  private setupResourceHints() {
    if (!this.config.enableResourceHints) return;

    // DNS prefetch for external domains
    this.addDNSPrefetch();
    
    // Preconnect to critical domains
    this.addPreconnect();
  }

  private addDNSPrefetch() {
    const externalDomains = this.getExternalDomains();
    externalDomains.forEach((domain) => {
      const link = document.createElement('link');
      link.rel = 'dns-prefetch';
      link.href = `//${domain}`;
      document.head.appendChild(link);
    });
  }

  private addPreconnect() {
    const criticalDomains = this.getCriticalDomains();
    criticalDomains.forEach((domain) => {
      const link = document.createElement('link');
      link.rel = 'preconnect';
      link.href = `//${domain}`;
      link.crossOrigin = 'anonymous';
      document.head.appendChild(link);
    });
  }

  private getExternalDomains(): string[] {
    // Extract external domains from current page resources
    const domains = new Set<string>();
    const links = document.querySelectorAll('a[href], img[src], script[src], link[href]');
    
    links.forEach((element) => {
      const href = element.getAttribute('href') || element.getAttribute('src');
      if (href) {
        try {
          const url = new URL(href, window.location.origin);
          if (url.hostname !== window.location.hostname) {
            domains.add(url.hostname);
          }
        } catch {
          // Invalid URL, skip
        }
      }
    });

    return Array.from(domains);
  }

  private getCriticalDomains(): string[] {
    // Return domains that are critical for the application
    return [
      'api.example.com', // Replace with your API domain
      'cdn.example.com', // Replace with your CDN domain
    ];
  }

  // Utility Methods
  private getPriority(element: HTMLElement): number {
    const priority = element.getAttribute('data-priority');
    switch (priority) {
      case 'high': return 3;
      case 'low': return 1;
      default: return 2;
    }
  }

  private supportsWebP(): boolean {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('image/webp') === 5;
  }

  private supportsAVIF(): boolean {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/avif').indexOf('image/avif') === 5;
  }

  // Public API
  lazyLoadImage(element: HTMLImageElement, config: ImageConfig) {
    if (!this.config.enableLazyLoading) {
      element.src = this.optimizeImage(config);
      return;
    }

    element.setAttribute('data-src', this.optimizeImage(config));
    element.setAttribute('data-lazy', 'true');
    element.setAttribute('data-priority', config.priority || 'normal');
    
    if (config.alt) {
      element.alt = config.alt;
    }

    this.intersectionObserver?.observe(element);
  }

  preloadCriticalResources() {
    const criticalResources: PreloadConfig[] = [
      // Add your critical resources here
      { href: '/api/config', as: 'fetch' },
      { href: '/images/logo.webp', as: 'image' },
    ];

    this.preloadResources(criticalResources);
  }

  getResourceStats() {
    return {
      isInitialized: this.isInitialized,
      loadedResources: this.loadedResources.size,
      activeLoads: this.activeLoads,
      queueLength: this.loadingQueue.length,
      config: { ...this.config },
    };
  }

  // Cleanup
  destroy() {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
      this.intersectionObserver = null;
    }

    this.loadingQueue = [];
    this.loadedResources.clear();
    this.activeLoads = 0;
    this.isInitialized = false;
  }
}

// Singleton instance
export const resourceOptimizer = new ResourceOptimizer();

// Auto-initialize
if (typeof window !== 'undefined') {
  resourceOptimizer.init();
}

export default resourceOptimizer;