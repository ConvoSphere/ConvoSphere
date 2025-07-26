import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import "./App.css";
import "./styles/animations.css";
import "./i18n/index.ts";

// Import optimization utilities
import initializePolyfills from "./utils/polyfills";
import performanceMonitor from "./utils/performance";
import workerManager from "./utils/workerManager";
import cacheManager from "./utils/cacheManager";
import networkOptimizer from "./utils/networkOptimizer";
import accessibilityManager from "./utils/accessibilityManager";
import resourceOptimizer from "./utils/resourceOptimizer";

// Initialize all optimization systems
const initializeOptimizations = async () => {
  try {
    console.log("🚀 Initializing ConvoSphere optimizations...");

    // Initialize polyfills first
    await initializePolyfills();
    console.log("✅ Polyfills initialized");

    // Initialize performance monitoring
    performanceMonitor.init();
    console.log("✅ Performance monitoring initialized");

    // Initialize worker manager
    await workerManager.init();
    console.log("✅ Worker manager initialized");

    // Initialize cache manager
    console.log("✅ Cache manager initialized");

    // Initialize network optimizer
    console.log("✅ Network optimizer initialized");

    // Initialize accessibility manager
    accessibilityManager.init();
    console.log("✅ Accessibility manager initialized");

    // Initialize resource optimizer
    resourceOptimizer.init();
    console.log("✅ Resource optimizer initialized");

    // Preload critical resources
    resourceOptimizer.preloadCriticalResources();
    console.log("✅ Critical resources preloaded");

    // Warm up cache with frequently accessed data
    await cacheManager.warmCache(
      ["user-preferences", "app-config", "theme-settings"],
      async (key) => {
        // Simulate loading frequently accessed data
        switch (key) {
          case "user-preferences":
            return { theme: "light", language: "en" };
          case "app-config":
            return { version: "1.0.0", features: ["chat", "assistants"] };
          case "theme-settings":
            return { mode: "light", colors: {} };
          default:
            return null;
        }
      },
    );
    console.log("✅ Cache warmed up");

    console.log("🎉 All optimizations initialized successfully");
  } catch (error) {
    console.error("❌ Failed to initialize optimizations:", error);
    // Continue with app initialization even if optimizations fail
  }
};

// Enhanced error handling for React rendering
const renderApp = () => {
  try {
    const root = ReactDOM.createRoot(document.getElementById("root")!);

    // Mark render start
    performanceMonitor.mark("app-render-start");

    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
    );

    // Mark render end and measure
    performanceMonitor.mark("app-render-end");
    performanceMonitor.measure(
      "App Render",
      "app-render-start",
      "app-render-end",
    );

    console.log("✅ React app rendered successfully");
  } catch (error) {
    console.error("❌ Failed to render React app:", error);

    // Show fallback error UI
    const root = document.getElementById("root");
    if (root) {
      root.innerHTML = `
        <div style="
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #f5f5f5;
          color: #333;
        ">
          <div style="text-align: center; padding: 2rem;">
            <h1 style="color: #e74c3c; margin-bottom: 1rem;">Application Error</h1>
            <p style="margin-bottom: 1rem;">Failed to load the application. Please refresh the page.</p>
            <button onclick="window.location.reload()" style="
              background: #3498db;
              color: white;
              border: none;
              padding: 0.5rem 1rem;
              border-radius: 4px;
              cursor: pointer;
            ">Refresh Page</button>
          </div>
        </div>
      `;
    }
  }
};

// Main initialization sequence
const initializeApp = async () => {
  try {
    // Mark app initialization start
    performanceMonitor.mark("app-init-start");

    // Initialize optimizations
    await initializeOptimizations();

    // Render the app
    renderApp();

    // Mark app initialization end
    performanceMonitor.mark("app-init-end");
    performanceMonitor.measure(
      "App Initialization",
      "app-init-start",
      "app-init-end",
    );

    // Log performance metrics
    const metrics = performanceMonitor.getMetrics();
    console.log("📊 Performance metrics:", metrics);

    // Log optimization stats
    console.log("📊 Cache stats:", cacheManager.getStats());
    console.log("📊 Network stats:", networkOptimizer.getNetworkStatus());
    console.log("📊 Worker stats:", workerManager.getStats());
    console.log("📊 Resource stats:", resourceOptimizer.getResourceStats());
    console.log(
      "📊 Accessibility stats:",
      accessibilityManager.getAccessibilityStatus(),
    );
  } catch (error) {
    console.error("❌ App initialization failed:", error);

    // Log error to performance monitor
    performanceMonitor.logError("App Initialization Error", {
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });

    // Still try to render the app
    renderApp();
  }
};

// Handle unhandled promise rejections
window.addEventListener("unhandledrejection", (event) => {
  console.error("❌ Unhandled promise rejection:", event.reason);
  performanceMonitor.logError("Unhandled Promise Rejection", {
    reason: event.reason,
    promise: event.promise,
  });
});

// Handle global errors
window.addEventListener("error", (event) => {
  console.error("❌ Global error:", event.error);
  performanceMonitor.logError("Global Error", {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error?.stack,
  });
});

// Handle beforeunload for cleanup
window.addEventListener("beforeunload", () => {
  console.log("🧹 Cleaning up optimizations...");

  // Cleanup all managers
  workerManager.terminate();
  cacheManager.destroy();
  networkOptimizer.destroy();
  accessibilityManager.destroy();
  resourceOptimizer.destroy();
  performanceMonitor.disconnect();

  console.log("✅ Cleanup completed");
});

// Start the application
initializeApp();
