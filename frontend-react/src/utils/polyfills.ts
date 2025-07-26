// Polyfills for better browser compatibility and Progressive Enhancement

// Check if we need to load polyfills
const needsPolyfills = () => {
  return !(
    "Promise" in window &&
    "fetch" in window &&
    "IntersectionObserver" in window &&
    "ResizeObserver" in window &&
    "PerformanceObserver" in window &&
    "requestIdleCallback" in window &&
    "requestAnimationFrame" in window &&
    "URLSearchParams" in window &&
    "AbortController" in window &&
    "structuredClone" in window
  );
};

// Load polyfills dynamically
const loadPolyfills = async () => {
  if (!needsPolyfills()) {
    return;
  }

  console.log("Loading polyfills for better browser compatibility...");

  const polyfills = [];

  // Core polyfills - simplified for now
  if (!("PerformanceObserver" in window)) {
    // Custom PerformanceObserver polyfill
    polyfills.push(
      Promise.resolve().then(() => {
        if (!("PerformanceObserver" in window)) {
          (window as any).PerformanceObserver = class PerformanceObserver {
            private callback: (...args: unknown[]) => void;
            constructor(callback: unknown) {
              if (typeof callback === "function") {
                this.callback = callback;
              } else {
                this.callback = () => {};
              }
            }
            observe() {}
            disconnect() {}
          };
        }
      }),
    );
  }

  if (!("requestIdleCallback" in window)) {
    polyfills.push(
      Promise.resolve().then(() => {
        if (!("requestIdleCallback" in window)) {
          (window as any).requestIdleCallback = (callback: unknown) => {
            const start = Date.now();
            if (typeof callback === "function") {
              return setTimeout(() => {
                callback({
                  didTimeout: false,
                  timeRemaining: () => Math.max(0, 50 - (Date.now() - start)),
                });
              }, 1);
            }
            return undefined;
          };
          (window as any).cancelIdleCallback = (id: number) => clearTimeout(id);
        }
      }),
    );
  }

  if (!("AbortController" in window)) {
    polyfills.push(
      Promise.resolve().then(() => {
        if (!("AbortController" in window)) {
          (window as any).AbortController = class AbortController {
            signal = { aborted: false };
            abort() {
              this.signal.aborted = true;
            }
          };
        }
      }),
    );
  }

  if (!("structuredClone" in window)) {
    polyfills.push(
      Promise.resolve().then(() => {
        if (!("structuredClone" in window)) {
          (window as any).structuredClone = (obj: unknown) =>
            JSON.parse(JSON.stringify(obj));
        }
      }),
    );
  }

  try {
    await Promise.all(polyfills);
    console.log("Polyfills loaded successfully");
  } catch (error) {
    console.warn("Some polyfills failed to load:", error);
  }
};

// Feature detection utilities
export const featureDetection = {
  // Check if browser supports modern CSS features
  css: {
    grid: CSS.supports("display", "grid"),
    flexbox: CSS.supports("display", "flex"),
    customProperties: CSS.supports("--custom-property", "value"),
    backdropFilter: CSS.supports("backdrop-filter", "blur(10px)"),
    aspectRatio: CSS.supports("aspect-ratio", "16/9"),
  },

  // Check if browser supports modern JavaScript features
  js: {
    asyncAwait: (() => {
      try {
        new Function("async () => {}");
        return true;
      } catch {
        return false;
      }
    })(),
    modules: "noModule" in HTMLScriptElement.prototype,
    webWorkers: "Worker" in window,
    serviceWorkers: "serviceWorker" in navigator,
    webAssembly: "WebAssembly" in window,
  },

  // Check if browser supports modern Web APIs
  web: {
    fetch: "fetch" in window,
    intersectionObserver: "IntersectionObserver" in window,
    resizeObserver: "ResizeObserver" in window,
    performanceObserver: "PerformanceObserver" in window,
    requestIdleCallback: "requestIdleCallback" in window,
    requestAnimationFrame: "requestAnimationFrame" in window,
    geolocation: "geolocation" in navigator,
    notifications: "Notification" in window,
    pushManager: "PushManager" in window,
    indexedDB: "indexedDB" in window,
  },

  // Check device capabilities
  device: {
    touch: "ontouchstart" in window || navigator.maxTouchPoints > 0,
    mobile:
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent,
      ),
    retina: window.devicePixelRatio > 1,
    lowBandwidth:
      (navigator as any).connection?.effectiveType === "slow-2g" ||
      (navigator as any).connection?.effectiveType === "2g",
    saveData: (navigator as any).connection?.saveData || false,
  },
};

// Progressive enhancement utilities
export const progressiveEnhancement = {
  // Apply CSS classes based on feature support
  applyFeatureClasses() {
    const html = document.documentElement;

    // CSS features
    if (featureDetection.css.grid) html.classList.add("css-grid");
    if (featureDetection.css.flexbox) html.classList.add("css-flexbox");
    if (featureDetection.css.customProperties)
      html.classList.add("css-custom-properties");
    if (featureDetection.css.backdropFilter)
      html.classList.add("css-backdrop-filter");
    if (featureDetection.css.aspectRatio)
      html.classList.add("css-aspect-ratio");

    // JavaScript features
    if (featureDetection.js.asyncAwait) html.classList.add("js-async-await");
    if (featureDetection.js.modules) html.classList.add("js-modules");
    if (featureDetection.js.webWorkers) html.classList.add("js-web-workers");
    if (featureDetection.js.serviceWorkers)
      html.classList.add("js-service-workers");

    // Web APIs
    if (featureDetection.web.fetch) html.classList.add("web-fetch");
    if (featureDetection.web.intersectionObserver)
      html.classList.add("web-intersection-observer");
    if (featureDetection.web.resizeObserver)
      html.classList.add("web-resize-observer");
    if (featureDetection.web.performanceObserver)
      html.classList.add("web-performance-observer");
    if (featureDetection.web.requestIdleCallback)
      html.classList.add("web-request-idle-callback");

    // Device features
    if (featureDetection.device.touch) html.classList.add("device-touch");
    if (featureDetection.device.mobile) html.classList.add("device-mobile");
    if (featureDetection.device.retina) html.classList.add("device-retina");
    if (featureDetection.device.lowBandwidth)
      html.classList.add("device-low-bandwidth");
    if (featureDetection.device.saveData)
      html.classList.add("device-save-data");
  },

  // Get appropriate image format based on browser support
  getImageFormat() {
    if (featureDetection.css.backdropFilter) {
      return "webp"; // Modern browsers support WebP
    }
    return "jpg"; // Fallback for older browsers
  },

  // Get appropriate video format based on browser support
  getVideoFormat() {
    const video = document.createElement("video");
    if (video.canPlayType("video/webm")) {
      return "webm";
    }
    if (video.canPlayType("video/mp4")) {
      return "mp4";
    }
    return "mp4"; // Default fallback
  },

  // Check if we should load heavy features
  shouldLoadHeavyFeatures() {
    return (
      !featureDetection.device.lowBandwidth &&
      !featureDetection.device.saveData &&
      featureDetection.js.asyncAwait
    );
  },

  // Check if we should enable animations
  shouldEnableAnimations() {
    return (
      !featureDetection.device.lowBandwidth &&
      !featureDetection.device.saveData &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  },
};

// Initialize polyfills and progressive enhancement
export const initializePolyfills = async () => {
  await loadPolyfills();
  progressiveEnhancement.applyFeatureClasses();

  // Add CSS classes for progressive enhancement
  const style = document.createElement("style");
  style.textContent = `
    /* Progressive enhancement styles */
    .css-grid .grid-layout { display: grid; }
    .no-css-grid .grid-layout { display: flex; flex-wrap: wrap; }
    
    .css-flexbox .flex-layout { display: flex; }
    .no-css-flexbox .flex-layout { display: block; }
    
    .css-custom-properties .theme-aware { /* Custom properties work */ }
    .no-css-custom-properties .theme-aware { /* Fallback colors */ }
    
    .device-touch .touch-optimized { /* Touch-friendly styles */ }
    .device-mobile .mobile-optimized { /* Mobile-specific styles */ }
    .device-retina .retina-optimized { /* High-DPI images */ }
    .device-low-bandwidth .low-bandwidth { /* Reduced features */ }
    .device-save-data .save-data { /* Data-saving features */ }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
      .animated { animation: none !important; }
      .transition { transition: none !important; }
    }
  `;
  document.head.appendChild(style);
};

// Export for use in main.tsx
export default initializePolyfills;
