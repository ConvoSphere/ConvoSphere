import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authService } from '../../../frontend-react/src/services/auth';

// Mock fetch
global.fetch = vi.fn();

describe('Auth Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'test@example.com',
          username: 'testuser'
        }
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.login('test@example.com', 'password123');

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
        }),
      });

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });

    it('should throw error on login failure', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' })
      });

      await expect(authService.login('test@example.com', 'wrong-password'))
        .rejects.toThrow('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should successfully register a new user', async () => {
      const mockResponse = {
        id: 1,
        email: 'new@example.com',
        username: 'newuser'
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const userData = {
        email: 'new@example.com',
        username: 'newuser',
        password: 'password123',
        first_name: 'New',
        last_name: 'User'
      };

      const result = await authService.register(userData);

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      expect(result).toEqual(mockResponse);
    });
  });

  describe('logout', () => {
    it('should clear token and user data on logout', () => {
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('user', JSON.stringify({ id: 1, email: 'test@example.com' }));

      authService.logout();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user from localStorage', () => {
      const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' };
      localStorage.setItem('user', JSON.stringify(mockUser));

      const result = authService.getCurrentUser();

      expect(result).toEqual(mockUser);
    });

    it('should return null if no user in localStorage', () => {
      const result = authService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true if token exists', () => {
      localStorage.setItem('access_token', 'test-token');

      const result = authService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false if no token', () => {
      const result = authService.isAuthenticated();

      expect(result).toBe(false);
    });
  });
});