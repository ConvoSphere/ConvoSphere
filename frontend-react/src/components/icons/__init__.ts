/**
 * Icon System Module
 * 
 * This module provides a comprehensive icon system with categorized icons
 * for better organization and maintainability.
 */

// Export the main Icon component
export { default as Icon } from './Icon';

// Export icon types
export type { IconName, IconSize, IconVariant, IconProps } from './types';

// Export icon categories
export * from './navigation';
export * from './actions';
export * from './communication';
export * from './media';
export * from './system';
export * from './data';
export * from './feedback';
export * from './text-format';