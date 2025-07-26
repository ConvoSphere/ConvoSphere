import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ErrorBoundary } from '../../../../frontend-react/src/components/ErrorBoundary';

// Mock console.error to avoid noise in tests
const originalError = console.error;
beforeEach(() => {
  console.error = vi.fn();
});

afterEach(() => {
  console.error = originalError;
});

// Component that throws an error for testing
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Component that throws an error in useEffect
const ThrowErrorInEffect = ({ shouldThrow }: { shouldThrow: boolean }) => {
  React.useEffect(() => {
    if (shouldThrow) {
      throw new Error('Effect error');
    }
  }, [shouldThrow]);

  return <div>Effect component</div>;
};

describe('ErrorBoundary', () => {
  describe('when no error occurs', () => {
    it('should render children normally', () => {
      render(
        <ErrorBoundary>
          <div>Test content</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('should render multiple children', () => {
      render(
        <ErrorBoundary>
          <div>First child</div>
          <div>Second child</div>
          <span>Third child</span>
        </ErrorBoundary>
      );

      expect(screen.getByText('First child')).toBeInTheDocument();
      expect(screen.getByText('Second child')).toBeInTheDocument();
      expect(screen.getByText('Third child')).toBeInTheDocument();
    });
  });

  describe('when an error occurs', () => {
    it('should catch and display error UI', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      // Should show error message
      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
      expect(screen.getByText(/An unexpected error occurred/i)).toBeInTheDocument();
    });

    it('should show error details in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText(/Test error/i)).toBeInTheDocument();
      expect(screen.getByText(/ErrorBoundary/i)).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should not show error details in production mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.queryByText(/Test error/i)).not.toBeInTheDocument();
      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should catch errors in useEffect', () => {
      render(
        <ErrorBoundary>
          <ThrowErrorInEffect shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    });
  });

  describe('error reporting', () => {
    it('should call onError callback when error occurs', () => {
      const onError = vi.fn();
      
      render(
        <ErrorBoundary onError={onError}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String)
        })
      );
    });

    it('should log error to console in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(console.error).toHaveBeenCalled();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('recovery functionality', () => {
    it('should provide retry button', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();
    });

    it('should reset error state when retry is clicked', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      // Initially shows error
      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();

      // Click retry
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      // Re-render without error
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      // Should show normal content
      expect(screen.getByText('No error')).toBeInTheDocument();
      expect(screen.queryByText(/Something went wrong/i)).not.toBeInTheDocument();
    });

    it('should call onRetry callback when retry is clicked', () => {
      const onRetry = vi.fn();
      
      render(
        <ErrorBoundary onRetry={onRetry}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      expect(onRetry).toHaveBeenCalled();
    });
  });

  describe('custom error UI', () => {
    it('should render custom fallback UI when provided', () => {
      const CustomFallback = ({ error }: { error: Error }) => (
        <div data-testid="custom-fallback">
          <h2>Custom Error</h2>
          <p>{error.message}</p>
        </div>
      );

      render(
        <ErrorBoundary fallback={CustomFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
      expect(screen.getByText('Custom Error')).toBeInTheDocument();
      expect(screen.getByText('Test error')).toBeInTheDocument();
    });

    it('should pass error and resetError to custom fallback', () => {
      const CustomFallback = vi.fn(({ error, resetError }) => (
        <div>
          <p>Error: {error.message}</p>
          <button onClick={resetError}>Custom Reset</button>
        </div>
      ));

      render(
        <ErrorBoundary fallback={CustomFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(CustomFallback).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.any(Error),
          resetError: expect.any(Function)
        }),
        expect.any(Object)
      );
    });
  });

  describe('error boundary lifecycle', () => {
    it('should not catch errors in event handlers', () => {
      const ComponentWithEventError = () => {
        const handleClick = () => {
          throw new Error('Event handler error');
        };

        return <button onClick={handleClick}>Click me</button>;
      };

      render(
        <ErrorBoundary>
          <ComponentWithEventError />
        </ErrorBoundary>
      );

      // Error boundary should not catch this error
      expect(screen.getByText('Click me')).toBeInTheDocument();
    });

    it('should catch errors in render method', () => {
      const ComponentWithRenderError = ({ shouldThrow }: { shouldThrow: boolean }) => {
        if (shouldThrow) {
          throw new Error('Render error');
        }
        return <div>Normal render</div>;
      };

      render(
        <ErrorBoundary>
          <ComponentWithRenderError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const errorAlert = screen.getByRole('alert');
      expect(errorAlert).toBeInTheDocument();
      expect(errorAlert).toHaveAttribute('aria-live', 'polite');
    });

    it('should be keyboard navigable', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toHaveAttribute('tabIndex', '0');
    });
  });

  describe('performance', () => {
    it('should not re-render unnecessarily when no error', () => {
      const renderCount = vi.fn();
      
      const TestComponent = () => {
        renderCount();
        return <div>Test</div>;
      };

      const { rerender } = render(
        <ErrorBoundary>
          <TestComponent />
        </ErrorBoundary>
      );

      // Re-render without changes
      rerender(
        <ErrorBoundary>
          <TestComponent />
        </ErrorBoundary>
      );

      expect(renderCount).toHaveBeenCalledTimes(2);
    });
  });
});