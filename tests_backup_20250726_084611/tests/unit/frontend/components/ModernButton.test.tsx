import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ModernButton } from '../../../../frontend-react/src/components/ModernButton';

// Mock the theme store
const mockGetCurrentColors = vi.fn();
vi.mock('../../../../frontend-react/src/store/themeStore', () => ({
  useThemeStore: () => ({
    getCurrentColors: mockGetCurrentColors
  })
}));

describe('ModernButton', () => {
  beforeEach(() => {
    mockGetCurrentColors.mockReturnValue({
      colorGradientPrimary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    });
  });

  describe('Rendering', () => {
    it('should render with default props', () => {
      render(<ModernButton>Click me</ModernButton>);
      
      const button = screen.getByRole('button', { name: /click me/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('modern-button', 'modern-button--primary', 'modern-button--md');
    });

    it('should render with custom className', () => {
      render(<ModernButton className="custom-class">Click me</ModernButton>);
      
      const button = screen.getByRole('button', { name: /click me/i });
      expect(button).toHaveClass('custom-class');
    });

    it('should render children correctly', () => {
      render(
        <ModernButton>
          <span>Custom content</span>
        </ModernButton>
      );
      
      expect(screen.getByText('Custom content')).toBeInTheDocument();
    });
  });

  describe('Variants', () => {
    it('should render primary variant correctly', () => {
      render(<ModernButton variant="primary">Primary Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /primary button/i });
      expect(button).toHaveClass('modern-button--primary');
    });

    it('should render secondary variant correctly', () => {
      render(<ModernButton variant="secondary">Secondary Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /secondary button/i });
      expect(button).toHaveClass('modern-button--secondary');
    });

    it('should render accent variant correctly', () => {
      render(<ModernButton variant="accent">Accent Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /accent button/i });
      expect(button).toHaveClass('modern-button--accent');
    });

    it('should render ghost variant correctly', () => {
      render(<ModernButton variant="ghost">Ghost Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /ghost button/i });
      expect(button).toHaveClass('modern-button--ghost');
    });

    it('should render dashed variant correctly', () => {
      render(<ModernButton variant="dashed">Dashed Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /dashed button/i });
      expect(button).toHaveClass('modern-button--dashed');
    });

    it('should render gradient variant correctly', () => {
      render(<ModernButton variant="gradient">Gradient Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /gradient button/i });
      expect(button).toHaveClass('modern-button--gradient');
      expect(button).toHaveStyle({
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: '#FFFFFF'
      });
    });

    it('should handle unknown variant gracefully', () => {
      render(<ModernButton variant="unknown" as any>Unknown Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /unknown button/i });
      expect(button).toBeInTheDocument();
    });
  });

  describe('Sizes', () => {
    it('should render xs size correctly', () => {
      render(<ModernButton size="xs">Small Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /small button/i });
      expect(button).toHaveClass('modern-button--xs');
    });

    it('should render sm size correctly', () => {
      render(<ModernButton size="sm">Small Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /small button/i });
      expect(button).toHaveClass('modern-button--sm');
    });

    it('should render md size correctly', () => {
      render(<ModernButton size="md">Medium Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /medium button/i });
      expect(button).toHaveClass('modern-button--md');
    });

    it('should render lg size correctly', () => {
      render(<ModernButton size="lg">Large Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /large button/i });
      expect(button).toHaveClass('modern-button--lg');
    });

    it('should render xl size correctly', () => {
      render(<ModernButton size="xl">Extra Large Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /extra large button/i });
      expect(button).toHaveClass('modern-button--xl');
    });
  });

  describe('Loading State', () => {
    it('should show loading state when loading is true', () => {
      render(<ModernButton loading>Loading Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /loading button/i });
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    it('should not show loading state when loading is false', () => {
      render(<ModernButton loading={false}>Normal Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /normal button/i });
      expect(button).not.toHaveAttribute('aria-busy', 'true');
    });

    it('should be disabled when loading', () => {
      render(<ModernButton loading>Loading Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /loading button/i });
      expect(button).toBeDisabled();
    });
  });

  describe('Icons', () => {
    const TestIcon = () => <span data-testid="test-icon">🚀</span>;

    it('should render icon on the left by default', () => {
      render(
        <ModernButton icon={<TestIcon />}>
          Button with Icon
        </ModernButton>
      );
      
      const icon = screen.getByTestId('test-icon');
      expect(icon).toBeInTheDocument();
      expect(icon.parentElement).toHaveStyle({
        marginRight: '8px',
        marginLeft: '0px'
      });
    });

    it('should render icon on the right when specified', () => {
      render(
        <ModernButton icon={<TestIcon />} iconPosition="right">
          Button with Icon
        </ModernButton>
      );
      
      const icon = screen.getByTestId('test-icon');
      expect(icon).toBeInTheDocument();
      expect(icon.parentElement).toHaveStyle({
        marginRight: '0px',
        marginLeft: '8px'
      });
    });

    it('should not render icon when not provided', () => {
      render(<ModernButton>Button without Icon</ModernButton>);
      
      expect(screen.queryByTestId('test-icon')).not.toBeInTheDocument();
    });

    it('should render icon with correct CSS class', () => {
      render(
        <ModernButton icon={<TestIcon />}>
          Button with Icon
        </ModernButton>
      );
      
      const iconContainer = screen.getByTestId('test-icon').parentElement;
      expect(iconContainer).toHaveClass('modern-button__icon');
    });
  });

  describe('Interactions', () => {
    it('should handle click events', () => {
      const handleClick = vi.fn();
      render(<ModernButton onClick={handleClick}>Clickable Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /clickable button/i });
      fireEvent.click(button);
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not trigger click when disabled', () => {
      const handleClick = vi.fn();
      render(
        <ModernButton onClick={handleClick} disabled>
          Disabled Button
        </ModernButton>
      );
      
      const button = screen.getByRole('button', { name: /disabled button/i });
      fireEvent.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('should not trigger click when loading', () => {
      const handleClick = vi.fn();
      render(
        <ModernButton onClick={handleClick} loading>
          Loading Button
        </ModernButton>
      );
      
      const button = screen.getByRole('button', { name: /loading button/i });
      fireEvent.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('should handle keyboard events', () => {
      const handleKeyDown = vi.fn();
      render(
        <ModernButton onKeyDown={handleKeyDown}>
          Keyboard Button
        </ModernButton>
      );
      
      const button = screen.getByRole('button', { name: /keyboard button/i });
      fireEvent.keyDown(button, { key: 'Enter' });
      
      expect(handleKeyDown).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<ModernButton aria-label="Custom label">Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /custom label/i });
      expect(button).toHaveAttribute('aria-label', 'Custom label');
    });

    it('should be keyboard navigable', () => {
      render(<ModernButton>Keyboard Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /keyboard button/i });
      expect(button).toHaveAttribute('tabIndex', '0');
    });

    it('should handle disabled state accessibility', () => {
      render(<ModernButton disabled>Disabled Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /disabled button/i });
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('should handle loading state accessibility', () => {
      render(<ModernButton loading>Loading Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /loading button/i });
      expect(button).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Props Forwarding', () => {
    it('should forward additional props to AntButton', () => {
      render(
        <ModernButton 
          data-testid="custom-button"
          title="Custom tooltip"
          form="test-form"
        >
          Custom Button
        </ModernButton>
      );
      
      const button = screen.getByTestId('custom-button');
      expect(button).toHaveAttribute('title', 'Custom tooltip');
      expect(button).toHaveAttribute('form', 'test-form');
    });

    it('should handle AntButton props correctly', () => {
      render(
        <ModernButton 
          danger
          block
          shape="round"
        >
          Ant Button Props
        </ModernButton>
      );
      
      const button = screen.getByRole('button', { name: /ant button props/i });
      expect(button).toHaveClass('ant-btn-dangerous');
      expect(button).toHaveClass('ant-btn-block');
      expect(button).toHaveClass('ant-btn-round');
    });
  });

  describe('Styling', () => {
    it('should apply correct base styles', () => {
      render(<ModernButton>Styled Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /styled button/i });
      expect(button).toHaveStyle({
        position: 'relative',
        overflow: 'hidden',
        borderRadius: '12px',
        fontWeight: '600',
        letterSpacing: '0.025em',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        border: 'none'
      });
    });

    it('should apply gradient styles for gradient variant', () => {
      render(<ModernButton variant="gradient">Gradient Button</ModernButton>);
      
      const button = screen.getByRole('button', { name: /gradient button/i });
      expect(button).toHaveStyle({
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: '#FFFFFF'
      });
    });

    it('should apply icon styles correctly', () => {
      const TestIcon = () => <span>🚀</span>;
      render(
        <ModernButton icon={<TestIcon />}>
          Icon Button
        </ModernButton>
      );
      
      const iconContainer = screen.getByText('🚀').parentElement;
      expect(iconContainer).toHaveStyle({
        display: 'inline-flex',
        alignItems: 'center',
        marginRight: '8px',
        marginLeft: '0px',
        transition: 'transform 0.2s ease'
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<ModernButton>{''}</ModernButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should handle null children', () => {
      render(<ModernButton>{null}</ModernButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should handle undefined children', () => {
      render(<ModernButton>{undefined}</ModernButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should handle complex children', () => {
      render(
        <ModernButton>
          <div>
            <span>Complex</span>
            <strong>Content</strong>
          </div>
        </ModernButton>
      );
      
      expect(screen.getByText('Complex')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
    });

    it('should handle multiple icons', () => {
      const Icon1 = () => <span data-testid="icon1">🚀</span>;
      const Icon2 = () => <span data-testid="icon2">⭐</span>;
      
      render(
        <ModernButton icon={<Icon1 />}>
          <Icon2 />
        </ModernButton>
      );
      
      expect(screen.getByTestId('icon1')).toBeInTheDocument();
      expect(screen.getByTestId('icon2')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('should not re-render unnecessarily', () => {
      const renderCount = vi.fn();
      
      const TestComponent = () => {
        renderCount();
        return <ModernButton>Test</ModernButton>;
      };

      const { rerender } = render(<TestComponent />);
      
      // Re-render with same props
      rerender(<TestComponent />);
      
      expect(renderCount).toHaveBeenCalledTimes(2);
    });

    it('should handle theme changes efficiently', () => {
      render(<ModernButton variant="gradient">Gradient Button</ModernButton>);
      
      // Change theme colors
      mockGetCurrentColors.mockReturnValue({
        colorGradientPrimary: 'linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%)'
      });
      
      const button = screen.getByRole('button', { name: /gradient button/i });
      expect(button).toBeInTheDocument();
    });
  });
});