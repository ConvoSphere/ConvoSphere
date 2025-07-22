import React from 'react';
import { useThemeStore } from '../store/themeStore';
import './Logo.css';

export interface LogoProps {
  variant?: 'main' | 'text' | 'icon' | 'minimal';
  size?: number;
  className?: string;
  alt?: string;
  animated?: boolean;
}

export const Logo: React.FC<LogoProps> = ({
  variant = 'main',
  size,
  className = '',
  alt = 'ConvoSphere',
  animated = true,
}) => {
  const { mode } = useThemeStore();

  const getLogoSrc = () => {
    switch (variant) {
      case 'text':
        return '/logo-convosphere-text.svg';
      case 'icon':
        return '/logo-convosphere-icon.svg';
      case 'minimal':
        return '/logo-convosphere-minimal.svg';
      case 'main':
      default:
        return mode === 'dark' ? '/logo-convosphere-dark.svg' : '/logo-convosphere.svg';
    }
  };

  const getDefaultSize = () => {
    switch (variant) {
      case 'text':
        return { width: 400, height: 120 };
      case 'icon':
        return { width: 64, height: 64 };
      case 'minimal':
        return { width: 32, height: 32 };
      case 'main':
      default:
        return { width: 200, height: 200 };
    }
  };

  const defaultSize = getDefaultSize();
  const finalSize = size ? { width: size, height: size } : defaultSize;

  const style: React.CSSProperties = {
    ...finalSize,
    transition: 'transform 0.3s ease',
  };

  const handleMouseEnter = (e: React.MouseEvent<HTMLImageElement>) => {
    if (animated) {
      e.currentTarget.style.transform = 'scale(1.05)';
    }
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLImageElement>) => {
    if (animated) {
      e.currentTarget.style.transform = 'scale(1)';
    }
  };

  return (
    <img
      src={getLogoSrc()}
      alt={alt}
      className={`convosphere-logo ${className}`}
      style={style}
      data-variant={variant}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    />
  );
};

export default Logo;