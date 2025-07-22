import { TextEncoder, TextDecoder } from 'util';
import '@testing-library/jest-dom';

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

if (typeof window !== 'undefined' && !window.matchMedia) {
  window.matchMedia = function matchMedia(query) {
    return {
      matches: false,
      media: query,
      onchange: null,
      addListener: function () {},
      removeListener: function () {},
      addEventListener: function () {},
      removeEventListener: function () {},
      dispatchEvent: function () { return false; },
    };
  };
} 