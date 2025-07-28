import React, { createContext, useContext, useState, useEffect } from "react";
import { ConfigProvider } from "antd";

interface AccessibilitySettings {
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  screenReader: boolean;
  keyboardNavigation: boolean;
  focusIndicators: boolean;
}

interface AccessibilityContextType {
  settings: AccessibilitySettings;
  updateSettings: (newSettings: Partial<AccessibilitySettings>) => void;
  toggleSetting: (setting: keyof AccessibilitySettings) => void;
  applyAccessibilityStyles: () => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

const defaultSettings: AccessibilitySettings = {
  highContrast: false,
  largeText: false,
  reducedMotion: false,
  screenReader: false,
  keyboardNavigation: true,
  focusIndicators: true,
};

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error("useAccessibility must be used within an AccessibilityProvider");
  }
  return context;
};

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<AccessibilitySettings>(() => {
    // Load settings from localStorage
    const saved = localStorage.getItem("accessibility_settings");
    return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
  });

  const updateSettings = (newSettings: Partial<AccessibilitySettings>) => {
    const updated = { ...settings, ...newSettings };
    setSettings(updated);
    localStorage.setItem("accessibility_settings", JSON.stringify(updated));
    applyAccessibilityStyles();
  };

  const toggleSetting = (setting: keyof AccessibilitySettings) => {
    updateSettings({ [setting]: !settings[setting] });
  };

  const applyAccessibilityStyles = () => {
    const root = document.documentElement;
    
    // High contrast
    if (settings.highContrast) {
      root.style.setProperty("--color-primary", "#ffffff");
      root.style.setProperty("--color-bg-base", "#000000");
      root.style.setProperty("--color-text-base", "#ffffff");
      root.style.setProperty("--color-border", "#ffffff");
    } else {
      root.style.removeProperty("--color-primary");
      root.style.removeProperty("--color-bg-base");
      root.style.removeProperty("--color-text-base");
      root.style.removeProperty("--color-border");
    }

    // Large text
    if (settings.largeText) {
      root.style.setProperty("--font-size-base", "18px");
      root.style.setProperty("--font-size-lg", "20px");
      root.style.setProperty("--font-size-sm", "16px");
    } else {
      root.style.removeProperty("--font-size-base");
      root.style.removeProperty("--font-size-lg");
      root.style.removeProperty("--font-size-sm");
    }

    // Reduced motion
    if (settings.reducedMotion) {
      root.style.setProperty("--animation-duration", "0s");
      root.style.setProperty("--transition-duration", "0s");
    } else {
      root.style.removeProperty("--animation-duration");
      root.style.removeProperty("--transition-duration");
    }

    // Focus indicators
    if (settings.focusIndicators) {
      root.style.setProperty("--focus-outline", "3px solid #1890ff");
      root.style.setProperty("--focus-outline-offset", "2px");
    } else {
      root.style.removeProperty("--focus-outline");
      root.style.removeProperty("--focus-outline-offset");
    }
  };

  // Apply settings on mount and when settings change
  useEffect(() => {
    applyAccessibilityStyles();
  }, [settings]);

  // Setup keyboard navigation
  useEffect(() => {
    if (!settings.keyboardNavigation) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Skip if user is typing in an input
      if (event.target instanceof HTMLInputElement || 
          event.target instanceof HTMLTextAreaElement ||
          event.target instanceof HTMLSelectElement) {
        return;
      }

      switch (event.key) {
        case "h":
        case "H":
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            // Navigate to home
            window.location.href = "/";
          }
          break;
        case "n":
        case "N":
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            // Navigate to next section
            const focusableElements = document.querySelectorAll(
              'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const currentIndex = Array.from(focusableElements).findIndex(el => el === document.activeElement);
            const nextIndex = (currentIndex + 1) % focusableElements.length;
            (focusableElements[nextIndex] as HTMLElement)?.focus();
          }
          break;
        case "p":
        case "P":
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            // Navigate to previous section
            const focusableElements = document.querySelectorAll(
              'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const currentIndex = Array.from(focusableElements).findIndex(el => el === document.activeElement);
            const prevIndex = currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1;
            (focusableElements[prevIndex] as HTMLElement)?.focus();
          }
          break;
        case "Escape":
          // Close modals or clear focus
          const activeElement = document.activeElement as HTMLElement;
          if (activeElement && activeElement.blur) {
            activeElement.blur();
          }
          break;
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [settings.keyboardNavigation]);

  // Setup screen reader announcements
  useEffect(() => {
    if (!settings.screenReader) return;

    const announceToScreenReader = (message: string) => {
      const announcement = document.createElement("div");
      announcement.setAttribute("aria-live", "polite");
      announcement.setAttribute("aria-atomic", "true");
      announcement.style.position = "absolute";
      announcement.style.left = "-10000px";
      announcement.style.width = "1px";
      announcement.style.height = "1px";
      announcement.style.overflow = "hidden";
      announcement.textContent = message;
      
      document.body.appendChild(announcement);
      setTimeout(() => document.body.removeChild(announcement), 1000);
    };

    // Make announce function globally available
    (window as any).announceToScreenReader = announceToScreenReader;

    return () => {
      delete (window as any).announceToScreenReader;
    };
  }, [settings.screenReader]);

  const contextValue: AccessibilityContextType = {
    settings,
    updateSettings,
    toggleSetting,
    applyAccessibilityStyles,
  };

  return (
    <AccessibilityContext.Provider value={contextValue}>
      <ConfigProvider
        theme={{
          token: {
            // Apply accessibility token overrides
            fontSize: settings.largeText ? 18 : 14,
            borderRadius: settings.highContrast ? 0 : 6,
            motionDurationFast: settings.reducedMotion ? 0 : 0.1,
            motionDurationMid: settings.reducedMotion ? 0 : 0.2,
            motionDurationSlow: settings.reducedMotion ? 0 : 0.3,
          },
        }}
      >
        {children}
      </ConfigProvider>
    </AccessibilityContext.Provider>
  );
};

// Accessibility utility functions
export const accessibilityUtils = {
  // Add ARIA labels to elements
  addAriaLabel: (element: HTMLElement, label: string) => {
    element.setAttribute("aria-label", label);
  },

  // Add ARIA descriptions
  addAriaDescription: (element: HTMLElement, description: string) => {
    element.setAttribute("aria-describedby", description);
  },

  // Make element focusable
  makeFocusable: (element: HTMLElement, tabIndex: number = 0) => {
    element.setAttribute("tabindex", tabIndex.toString());
  },

  // Announce to screen reader
  announce: (message: string) => {
    if ((window as any).announceToScreenReader) {
      (window as any).announceToScreenReader(message);
    }
  },

  // Skip to main content
  skipToMainContent: () => {
    const mainContent = document.querySelector("main") || document.querySelector("[role='main']");
    if (mainContent) {
      (mainContent as HTMLElement).focus();
    }
  },

  // Get focusable elements
  getFocusableElements: (container: HTMLElement = document.body) => {
    return container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
  },

  // Trap focus within container
  trapFocus: (container: HTMLElement) => {
    const focusableElements = accessibilityUtils.getFocusableElements(container);
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (event: KeyboardEvent) => {
      if (event.key === "Tab") {
        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    container.addEventListener("keydown", handleTabKey);
    return () => container.removeEventListener("keydown", handleTabKey);
  },
};

export default AccessibilityProvider;