/* global jest */
import "@testing-library/jest-dom";
import { TextEncoder, TextDecoder } from "util";

// Vitest compatibility: map jest API to vi when running under Vitest
// eslint-disable-next-line no-undef
if (typeof vi !== "undefined") {
  // eslint-disable-next-line no-undef
  globalThis.jest = vi;
}

// Add TextEncoder and TextDecoder to global scope
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (globalThis.jest || { fn: () => () }).fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: (globalThis.jest || { fn: () => () }).fn(), // deprecated
    removeListener: (globalThis.jest || { fn: () => () }).fn(), // deprecated
    addEventListener: (globalThis.jest || { fn: () => () }).fn(),
    removeEventListener: (globalThis.jest || { fn: () => () }).fn(),
    dispatchEvent: (globalThis.jest || { fn: () => () }).fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = (globalThis.jest || { fn: () => () }).fn().mockImplementation(() => ({
  observe: (globalThis.jest || { fn: () => () }).fn(),
  unobserve: (globalThis.jest || { fn: () => () }).fn(),
  disconnect: (globalThis.jest || { fn: () => () }).fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = (globalThis.jest || { fn: () => () }).fn().mockImplementation(() => ({
  observe: (globalThis.jest || { fn: () => () }).fn(),
  unobserve: (globalThis.jest || { fn: () => () }).fn(),
  disconnect: (globalThis.jest || { fn: () => () }).fn(),
}));

// Mock WebSocket
global.WebSocket = (globalThis.jest || { fn: () => () }).fn().mockImplementation(() => ({
  send: (globalThis.jest || { fn: () => () }).fn(),
  close: (globalThis.jest || { fn: () => () }).fn(),
  addEventListener: (globalThis.jest || { fn: () => () }).fn(),
  removeEventListener: (globalThis.jest || { fn: () => () }).fn(),
}));

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: (globalThis.jest || { fn: () => () }).fn(),
  debug: (globalThis.jest || { fn: () => () }).fn(),
  info: (globalThis.jest || { fn: () => () }).fn(),
  warn: (globalThis.jest || { fn: () => () }).fn(),
  error: (globalThis.jest || { fn: () => () }).fn(),
};
