// Accessibility Manager für Keyboard Navigation, Screen Reader Support und WCAG Compliance

export interface AccessibilityConfig {
  enableKeyboardNavigation: boolean;
  enableScreenReaderSupport: boolean;
  enableFocusManagement: boolean;
  enableHighContrast: boolean;
  enableReducedMotion: boolean;
  enableLargeText: boolean;
  announceChanges: boolean;
}

export interface FocusableElement {
  element: HTMLElement;
  priority: number;
  group?: string;
}

class AccessibilityManager {
  private config: AccessibilityConfig;
  private focusableElements: FocusableElement[] = [];
  private focusGroups: Map<string, HTMLElement[]> = new Map();
  private isInitialized = false;
  private announcementQueue: string[] = [];
  private announcementTimer: NodeJS.Timeout | null = null;

  constructor(config: Partial<AccessibilityConfig> = {}) {
    this.config = {
      enableKeyboardNavigation: true,
      enableScreenReaderSupport: true,
      enableFocusManagement: true,
      enableHighContrast: false,
      enableReducedMotion: false,
      enableLargeText: false,
      announceChanges: true,
      ...config,
    };
  }

  init() {
    if (this.isInitialized) return;

    this.setupKeyboardNavigation();
    this.setupFocusManagement();
    this.setupScreenReaderSupport();
    this.setupPreferenceListeners();
    this.createAnnouncementRegion();

    this.isInitialized = true;
    console.log("Accessibility Manager initialized");
  }

  // Keyboard Navigation Setup
  private setupKeyboardNavigation() {
    if (!this.config.enableKeyboardNavigation) return;

    document.addEventListener("keydown", (event) => {
      this.handleKeyboardNavigation(event);
    });

    // Trap focus in modals
    document.addEventListener("keydown", (event) => {
      if (event.key === "Tab") {
        this.handleTabNavigation(event);
      }
    });
  }

  private handleKeyboardNavigation(event: KeyboardEvent) {
    const target = event.target as HTMLElement;

    // Skip if target is an input or textarea
    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") {
      return;
    }

    switch (event.key) {
      case "ArrowUp":
      case "ArrowDown":
        event.preventDefault();
        this.navigateVertically(event.key === "ArrowUp" ? -1 : 1);
        break;
      case "ArrowLeft":
      case "ArrowRight":
        event.preventDefault();
        this.navigateHorizontally(event.key === "ArrowLeft" ? -1 : 1);
        break;
      case "Home":
        event.preventDefault();
        this.focusFirst();
        break;
      case "End":
        event.preventDefault();
        this.focusLast();
        break;
      case "Escape":
        this.handleEscape();
        break;
    }
  }

  private navigateVertically(direction: number) {
    const currentElement = document.activeElement as HTMLElement;
    if (!currentElement) return;

    const currentRect = currentElement.getBoundingClientRect();
    const currentCenter = currentRect.top + currentRect.height / 2;

    let bestCandidate: HTMLElement | null = null;
    let bestDistance = Infinity;

    this.focusableElements.forEach(({ element }) => {
      if (element === currentElement) return;

      const rect = element.getBoundingClientRect();
      const center = rect.top + rect.height / 2;
      const distance = Math.abs(center - currentCenter);

      // Check if element is in the right direction
      const isInDirection =
        direction > 0 ? center > currentCenter : center < currentCenter;

      if (isInDirection && distance < bestDistance) {
        bestCandidate = element;
        bestDistance = distance;
      }
    });

    if (bestCandidate) {
      (bestCandidate as HTMLElement).focus();
    }
  }

  private navigateHorizontally(direction: number) {
    const currentElement = document.activeElement as HTMLElement;
    if (!currentElement) return;

    const currentRect = currentElement.getBoundingClientRect();
    const currentCenter = currentRect.left + currentRect.width / 2;

    let bestCandidate: HTMLElement | null = null;
    let bestDistance = Infinity;

    this.focusableElements.forEach(({ element }) => {
      if (element === currentElement) return;

      const rect = element.getBoundingClientRect();
      const center = rect.left + rect.width / 2;
      const distance = Math.abs(center - currentCenter);

      // Check if element is in the right direction
      const isInDirection =
        direction > 0 ? center > currentCenter : center < currentCenter;

      if (isInDirection && distance < bestDistance) {
        bestCandidate = element;
        bestDistance = distance;
      }
    });

    if (bestCandidate) {
      (bestCandidate as HTMLElement).focus();
    }
  }

  private focusFirst() {
    if (this.focusableElements.length > 0) {
      (this.focusableElements[0].element as HTMLElement).focus();
    }
  }

  private focusLast() {
    if (this.focusableElements.length > 0) {
      (
        this.focusableElements[this.focusableElements.length - 1]
          .element as HTMLElement
      ).focus();
    }
  }

  private handleEscape() {
    // Close modals, dropdowns, etc.
    const event = new CustomEvent("accessibility:escape", {
      detail: { timestamp: Date.now() },
    });
    document.dispatchEvent(event);
  }

  // Focus Management
  private setupFocusManagement() {
    if (!this.config.enableFocusManagement) return;

    // Track focusable elements
    this.updateFocusableElements();

    // Listen for DOM changes
    const observer = new MutationObserver(() => {
      this.updateFocusableElements();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["tabindex", "disabled", "hidden", "style", "class"],
    });
  }

  private updateFocusableElements() {
    this.focusableElements = [];
    this.focusGroups.clear();

    const focusableSelectors = [
      "button:not([disabled])",
      "input:not([disabled])",
      "select:not([disabled])",
      "textarea:not([disabled])",
      "a[href]",
      '[tabindex]:not([tabindex="-1"])',
      '[role="button"]',
      '[role="link"]',
      '[role="menuitem"]',
      '[role="tab"]',
      '[role="option"]',
    ].join(", ");

    const elements = document.querySelectorAll(focusableSelectors);

    elements.forEach((element) => {
      const htmlElement = element as HTMLElement;

      // Skip hidden elements
      if (this.isElementHidden(htmlElement)) return;

      const priority = this.calculateFocusPriority(htmlElement);
      const group = htmlElement.getAttribute("data-focus-group") ?? undefined;

      this.focusableElements.push({
        element: htmlElement,
        priority,
        group,
      });

      if (group) {
        if (!this.focusGroups.has(group)) {
          this.focusGroups.set(group, []);
        }
        this.focusGroups.get(group)!.push(htmlElement);
      }
    });

    // Sort by priority
    this.focusableElements.sort((a, b) => b.priority - a.priority);
  }

  private isElementHidden(element: HTMLElement): boolean {
    const style = window.getComputedStyle(element);
    return (
      style.display === "none" ||
      style.visibility === "hidden" ||
      style.opacity === "0" ||
      element.hasAttribute("hidden") ||
      element.getAttribute("aria-hidden") === "true"
    );
  }

  private calculateFocusPriority(element: HTMLElement): number {
    let priority = 0;

    // Higher priority for interactive elements
    if (element.tagName === "BUTTON" || element.tagName === "A") {
      priority += 10;
    }

    // Higher priority for elements with higher tabindex
    const tabIndex = parseInt(element.getAttribute("tabindex") || "0");
    priority += tabIndex;

    // Higher priority for elements in viewport
    const rect = element.getBoundingClientRect();
    if (rect.top >= 0 && rect.bottom <= window.innerHeight) {
      priority += 5;
    }

    return priority;
  }

  // Screen Reader Support
  private setupScreenReaderSupport() {
    if (!this.config.enableScreenReaderSupport) return;

    // Announce page changes
    this.announcePageChange();

    // Announce dynamic content changes
    this.setupContentAnnouncements();
  }

  private announcePageChange() {
    const pageTitle = document.title;
    const mainHeading = document.querySelector('h1, [role="main"] h1');

    if (mainHeading) {
      this.announce(`${pageTitle}. ${mainHeading.textContent}`);
    } else {
      this.announce(pageTitle);
    }
  }

  private setupContentAnnouncements() {
    // Listen for content changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === "childList") {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              const element = node as HTMLElement;
              this.handleContentChange(element);
            }
          });
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  private handleContentChange(element: HTMLElement) {
    // Announce important changes
    if (
      element.hasAttribute("aria-live") ||
      element.getAttribute("role") === "alert" ||
      element.classList.contains("announce")
    ) {
      const text = element.textContent?.trim();
      if (text) {
        this.announce(text);
      }
    }
  }

  private createAnnouncementRegion() {
    let region = document.getElementById("accessibility-announcements");

    if (!region) {
      region = document.createElement("div");
      region.id = "accessibility-announcements";
      region.setAttribute("aria-live", "polite");
      region.setAttribute("aria-atomic", "true");
      region.style.cssText = `
        position: absolute;
        left: -10000px;
        width: 1px;
        height: 1px;
        overflow: hidden;
      `;
      document.body.appendChild(region);
    }
  }

  // Announce text to screen readers
  announce(text: string, priority: "polite" | "assertive" = "polite") {
    if (!this.config.announceChanges) return;

    const region = document.getElementById("accessibility-announcements");
    if (!region) return;

    region.setAttribute("aria-live", priority);

    // Queue announcements to prevent overlap
    this.announcementQueue.push(text);

    if (this.announcementTimer) {
      clearTimeout(this.announcementTimer);
    }

    this.announcementTimer = setTimeout(() => {
      const message = this.announcementQueue.join(". ");
      region.textContent = message;
      this.announcementQueue = [];

      // Clear after announcement
      setTimeout(() => {
        region.textContent = "";
      }, 100);
    }, 100);
  }

  // Tab Navigation (Focus Trap)
  private handleTabNavigation(event: KeyboardEvent) {
    const modal = document.querySelector(
      '[role="dialog"], .modal, [data-modal]',
    );
    if (!modal) return;

    const focusableElements = modal.querySelectorAll(
      'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])',
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;

    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }

  // Preference Listeners
  private setupPreferenceListeners() {
    // High contrast mode
    const highContrastQuery = window.matchMedia("(prefers-contrast: high)");
    highContrastQuery.addEventListener("change", (e) => {
      this.config.enableHighContrast = e.matches;
      this.applyAccessibilityPreferences();
    });

    // Reduced motion
    const reducedMotionQuery = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    );
    reducedMotionQuery.addEventListener("change", (e) => {
      this.config.enableReducedMotion = e.matches;
      this.applyAccessibilityPreferences();
    });

    // Apply initial preferences
    this.config.enableHighContrast = highContrastQuery.matches;
    this.config.enableReducedMotion = reducedMotionQuery.matches;
    this.applyAccessibilityPreferences();
  }

  private applyAccessibilityPreferences() {
    const html = document.documentElement;

    if (this.config.enableHighContrast) {
      html.classList.add("high-contrast");
    } else {
      html.classList.remove("high-contrast");
    }

    if (this.config.enableReducedMotion) {
      html.classList.add("reduced-motion");
    } else {
      html.classList.remove("reduced-motion");
    }

    if (this.config.enableLargeText) {
      html.classList.add("large-text");
    } else {
      html.classList.remove("large-text");
    }
  }

  // Public API
  setFocusGroup(group: string, elements: HTMLElement[]) {
    this.focusGroups.set(group, elements);
  }

  focusGroup(group: string) {
    const elements = this.focusGroups.get(group);
    if (elements && elements.length > 0) {
      elements[0].focus();
    }
  }

  focusNext() {
    const currentIndex = this.focusableElements.findIndex(
      ({ element }) => element === document.activeElement,
    );

    const nextIndex = (currentIndex + 1) % this.focusableElements.length;
    (this.focusableElements[nextIndex].element as HTMLElement).focus();
  }

  focusPrevious() {
    const currentIndex = this.focusableElements.findIndex(
      ({ element }) => element === document.activeElement,
    );

    const prevIndex =
      currentIndex > 0 ? currentIndex - 1 : this.focusableElements.length - 1;
    (this.focusableElements[prevIndex].element as HTMLElement).focus();
  }

  getAccessibilityStatus() {
    return {
      isInitialized: this.isInitialized,
      focusableElements: this.focusableElements.length,
      focusGroups: this.focusGroups.size,
      config: { ...this.config },
    };
  }

  // Destroy manager
  destroy() {
    if (this.announcementTimer) {
      clearTimeout(this.announcementTimer);
      this.announcementTimer = null;
    }

    this.focusableElements = [];
    this.focusGroups.clear();
    this.isInitialized = false;
  }
}

// Singleton instance
export const accessibilityManager = new AccessibilityManager();

// Auto-initialize
if (typeof window !== "undefined") {
  accessibilityManager.init();
}

export default accessibilityManager;
