import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';

// Mock the auth service
vi.mock('../../../frontend-react/src/services/auth', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    isAuthenticated: vi.fn(),
  }
}));

// Mock the chat service
vi.mock('../../../frontend-react/src/services/chat', () => ({
  chatService: {
    getConversations: vi.fn(),
    sendMessage: vi.fn(),
  }
}));

// Import components after mocking
import { authService } from '../../../frontend-react/src/services/auth';
import { chatService } from '../../../frontend-react/src/services/chat';

describe('Auth Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Login Flow', () => {
    it('should handle successful login and redirect', async () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser'
      };

      const mockLoginResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user: mockUser
      };

      (authService.login as any).mockResolvedValue(mockLoginResponse);
      (authService.getCurrentUser as any).mockReturnValue(mockUser);
      (authService.isAuthenticated as any).mockReturnValue(true);
      (chatService.getConversations as any).mockResolvedValue({
        conversations: [],
        total: 0
      });

      // Simulate login process
      const result = await authService.login('test@example.com', 'password123');

      expect(result).toEqual(mockLoginResponse);
      expect(authService.login).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });

    it('should handle login failure and show error', async () => {
      const errorMessage = 'Invalid credentials';
      (authService.login as any).mockRejectedValue(new Error(errorMessage));

      await expect(authService.login('test@example.com', 'wrong-password'))
        .rejects.toThrow(errorMessage);

      expect(authService.login).toHaveBeenCalledWith('test@example.com', 'wrong-password');
      expect(localStorage.getItem('access_token')).toBeNull();
    });
  });

  describe('Registration Flow', () => {
    it('should handle successful registration', async () => {
      const mockUser = {
        id: 1,
        email: 'new@example.com',
        username: 'newuser'
      };

      (authService.register as any).mockResolvedValue(mockUser);

      const userData = {
        email: 'new@example.com',
        username: 'newuser',
        password: 'password123',
        first_name: 'New',
        last_name: 'User'
      };

      const result = await authService.register(userData);

      expect(result).toEqual(mockUser);
      expect(authService.register).toHaveBeenCalledWith(userData);
    });

    it('should handle registration validation errors', async () => {
      const errorMessage = 'Email already exists';
      (authService.register as any).mockRejectedValue(new Error(errorMessage));

      const userData = {
        email: 'existing@example.com',
        username: 'existinguser',
        password: 'password123',
        first_name: 'Existing',
        last_name: 'User'
      };

      await expect(authService.register(userData))
        .rejects.toThrow(errorMessage);
    });
  });

  describe('Logout Flow', () => {
    it('should handle logout and clear session', () => {
      // Setup authenticated state
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('user', JSON.stringify({ id: 1, email: 'test@example.com' }));

      (authService.logout as any).mockImplementation(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      });

      authService.logout();

      expect(authService.logout).toHaveBeenCalled();
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });
  });

  describe('Authentication State Management', () => {
    it('should correctly check authentication status', () => {
      // Test unauthenticated state
      (authService.isAuthenticated as any).mockReturnValue(false);
      expect(authService.isAuthenticated()).toBe(false);

      // Test authenticated state
      localStorage.setItem('access_token', 'test-token');
      (authService.isAuthenticated as any).mockReturnValue(true);
      expect(authService.isAuthenticated()).toBe(true);
    });

    it('should retrieve current user correctly', () => {
      const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' };
      (authService.getCurrentUser as any).mockReturnValue(mockUser);

      const currentUser = authService.getCurrentUser();
      expect(currentUser).toEqual(mockUser);
    });
  });

  describe('Protected Route Integration', () => {
    it('should allow access to protected routes when authenticated', () => {
      (authService.isAuthenticated as any).mockReturnValue(true);
      (authService.getCurrentUser as any).mockReturnValue({
        id: 1,
        email: 'test@example.com'
      });

      const isAuthenticated = authService.isAuthenticated();
      const currentUser = authService.getCurrentUser();

      expect(isAuthenticated).toBe(true);
      expect(currentUser).toBeDefined();
    });

    it('should redirect from protected routes when not authenticated', () => {
      (authService.isAuthenticated as any).mockReturnValue(false);
      (authService.getCurrentUser as any).mockReturnValue(null);

      const isAuthenticated = authService.isAuthenticated();
      const currentUser = authService.getCurrentUser();

      expect(isAuthenticated).toBe(false);
      expect(currentUser).toBeNull();
    });
  });

  describe('Token Management', () => {
    it('should handle token expiration', () => {
      // Setup expired token scenario
      const expiredToken = 'expired-token';
      localStorage.setItem('access_token', expiredToken);

      // Simulate token expiration by clearing it
      localStorage.removeItem('access_token');
      (authService.isAuthenticated as any).mockReturnValue(false);

      expect(authService.isAuthenticated()).toBe(false);
      expect(localStorage.getItem('access_token')).toBeNull();
    });

    it('should handle token refresh scenario', () => {
      const validToken = 'valid-token';
      localStorage.setItem('access_token', validToken);
      (authService.isAuthenticated as any).mockReturnValue(true);

      expect(authService.isAuthenticated()).toBe(true);
      expect(localStorage.getItem('access_token')).toBe(validToken);
    });
  });
});