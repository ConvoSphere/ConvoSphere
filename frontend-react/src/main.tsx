import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import "./App.css";
import "./styles/animations.css";
import "./i18n/index.ts";

// Simple initialization without complex optimizations
const initializeApp = () => {
  try {
    const root = ReactDOM.createRoot(document.getElementById("root")!);
    
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
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

// Handle unhandled promise rejections
window.addEventListener("unhandledrejection", (event) => {
  console.error("❌ Unhandled promise rejection:", event.reason);
});

// Handle global errors
window.addEventListener("error", (event) => {
  console.error("❌ Global error:", event.error);
});

// Start the application
initializeApp();
