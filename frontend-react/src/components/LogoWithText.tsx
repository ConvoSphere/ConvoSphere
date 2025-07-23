import React from 'react';
import { Logo } from './Logo';
import type { LogoProps } from './Logo';

export interface LogoWithTextProps extends Omit<LogoProps, 'variant'> {
  showTagline?: boolean;
  tagline?: string;
  layout?: 'horizontal' | 'vertical';
  logoSize?: number;
  className?: string;
}

export const LogoWithText: React.FC<LogoWithTextProps> = ({
  showTagline = true,
  tagline = 'AI-Powered Conversations',
  layout = 'horizontal',
  logoSize,
  className = '',
  ...logoProps
}) => {
  const containerClass = `logo-container ${layout} ${className}`.trim();
  const textClass = `logo-with-text ${layout}`.trim();

  if (layout === 'vertical') {
    return (
      <div className={containerClass}>
        <Logo variant="icon" size={logoSize || 64} {...logoProps} />
        <div className="logo-text-content">
          <div className="logo-text">ConvoSphere</div>
          {showTagline && <div className="logo-tagline">{tagline}</div>}
        </div>
      </div>
    );
  }

  return (
    <div className={containerClass}>
      <Logo variant="icon" size={logoSize || 48} {...logoProps} />
      <div className={textClass}>
        <div className="logo-text">ConvoSphere</div>
        {showTagline && <div className="logo-tagline">{tagline}</div>}
      </div>
    </div>
  );
};

export default LogoWithText;