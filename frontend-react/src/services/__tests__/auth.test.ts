import { login, register, logout, refreshToken, validateToken, updateProfile, changePassword } from '../auth';

// Mock fetch
global.fetch = jest.fn();

describe('Auth Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
  });

  describe('login', () => {
    test('should login successfully', async () => {
      const mockResponse = {
        user: { id: '1', email: 'test@example.com', username: 'testuser' },
        token: 'fake-token',
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await login('test@example.com', 'password123');

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
    });

    test('should handle login error', async () => {
      const errorMessage = 'Invalid credentials';

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ message: errorMessage }),
      });

      await expect(login('test@example.com', 'wrongpassword')).rejects.toThrow(errorMessage);
    });

    test('should handle network error', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(login('test@example.com', 'password123')).rejects.toThrow('Network error');
    });

    test('should handle server error', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ message: 'Internal server error' }),
      });

      await expect(login('test@example.com', 'password123')).rejects.toThrow('Internal server error');
    });
  });

  describe('register', () => {
    test('should register successfully', async () => {
      const mockResponse = {
        user: { id: '1', email: 'test@example.com', username: 'testuser' },
        token: 'fake-token',
      };

      const registerData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
        fullName: 'Test User',
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await register(registerData);

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      });

      expect(result).toEqual(mockResponse);
    });

    test('should handle registration error', async () => {
      const errorMessage = 'Email already exists';

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: errorMessage }),
      });

      await expect(register({
        email: 'existing@example.com',
        username: 'existinguser',
        password: 'password123',
        fullName: 'Existing User',
      })).rejects.toThrow(errorMessage);
    });

    test('should handle validation errors', async () => {
      const validationErrors = {
        email: ['Invalid email format'],
        password: ['Password must be at least 8 characters'],
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({ errors: validationErrors }),
      });

      await expect(register({
        email: 'invalid-email',
        username: 'user',
        password: '123',
        fullName: 'User',
      })).rejects.toThrow('Validation failed');
    });
  });

  describe('logout', () => {
    test('should logout successfully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logged out successfully' }),
      });

      await logout();

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer fake-token',
        },
      });
    });

    test('should handle logout error gracefully', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      // Logout should not throw even if API call fails
      await expect(logout()).resolves.toBeUndefined();
    });

    test('should include auth token in request', async () => {
      // Mock localStorage to return a token
      const localStorageMock = {
        getItem: jest.fn((key: string) => {
          if (key === 'token') return 'fake-token';
          return null;
        }),
      };
      Object.defineProperty(window, 'localStorage', { value: localStorageMock });

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logged out successfully' }),
      });

      await logout();

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer fake-token',
        },
      });
    });
  });

  describe('refreshToken', () => {
    test('should refresh token successfully', async () => {
      const mockResponse = {
        token: 'new-fake-token',
        refresh_token: 'new-refresh-token',
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await refreshToken();

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer fake-token',
        },
      });

      expect(result).toEqual(mockResponse);
    });

    test('should handle token refresh error', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ message: 'Token expired' }),
      });

      await expect(refreshToken()).rejects.toThrow('Token expired');
    });
  });

  describe('validateToken', () => {
    test('should validate token successfully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: true }),
      });

      const result = await validateToken('fake-token');

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: 'fake-token' }),
      });

      expect(result).toBe(true);
    });

    test('should return false for invalid token', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: false }),
      });

      const result = await validateToken('invalid-token');

      expect(result).toBe(false);
    });

    test('should handle validation error', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const result = await validateToken('fake-token');

      expect(result).toBe(false);
    });
  });

  describe('updateProfile', () => {
    test('should update profile successfully', async () => {
      const mockResponse = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        fullName: 'Updated Name',
      };

      const updateData = {
        fullName: 'Updated Name',
        username: 'newusername',
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await updateProfile(updateData);

      expect(fetch).toHaveBeenCalledWith('/api/v1/users/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer fake-token',
        },
        body: JSON.stringify(updateData),
      });

      expect(result).toEqual(mockResponse);
    });

    test('should handle profile update error', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: 'Update failed' }),
      });

      await expect(updateProfile({ fullName: 'Updated Name' })).rejects.toThrow('Update failed');
    });
  });

  describe('changePassword', () => {
    test('should change password successfully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Password changed successfully' }),
      });

      await changePassword('oldpassword', 'newpassword');

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer fake-token',
        },
        body: JSON.stringify({
          oldPassword: 'oldpassword',
          newPassword: 'newpassword',
        }),
      });
    });

    test('should handle password change error', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: 'Old password is incorrect' }),
      });

      await expect(changePassword('wrongpassword', 'newpassword')).rejects.toThrow('Old password is incorrect');
    });
  });

  describe('Error Handling', () => {
    test('should handle JSON parsing error', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(login('test@example.com', 'password123')).rejects.toThrow('Invalid JSON');
    });

    test('should handle timeout', async () => {
      (fetch as jest.Mock).mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      await expect(login('test@example.com', 'password123')).rejects.toThrow('Request timeout');
    });

    test('should handle CORS error', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('CORS error'));

      await expect(login('test@example.com', 'password123')).rejects.toThrow('CORS error');
    });
  });

  describe('Request Configuration', () => {
    test('should use correct base URL', async () => {
      // Mock environment variable
      const originalEnv = process.env;
      process.env.VITE_API_BASE_URL = 'https://api.example.com';

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ user: {}, token: 'fake-token' }),
      });

      await login('test@example.com', 'password123');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('https://api.example.com'),
        expect.any(Object)
      );

      // Restore environment
      process.env = originalEnv;
    });

    test('should include correct headers', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ user: {}, token: 'fake-token' }),
      });

      await login('test@example.com', 'password123');

      const callArgs = (fetch as jest.Mock).mock.calls[0];
      const headers = callArgs[1].headers;

      expect(headers['Content-Type']).toBe('application/json');
      expect(headers['Accept']).toBe('application/json');
    });

    test('should handle missing token gracefully', async () => {
      // Mock localStorage to return null for token
      const localStorageMock = {
        getItem: jest.fn(() => null),
      };
      Object.defineProperty(window, 'localStorage', { value: localStorageMock });

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logged out successfully' }),
      });

      await logout();

      const callArgs = (fetch as jest.Mock).mock.calls[0];
      const headers = callArgs[1].headers;

      expect(headers['Authorization']).toBe('Bearer null');
    });
  });

  describe('Response Handling', () => {
    test('should handle empty response', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => null,
      });

      const result = await login('test@example.com', 'password123');

      expect(result).toBeNull();
    });

    test('should handle response without JSON', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        text: async () => 'Success',
      });

      const result = await login('test@example.com', 'password123');

      expect(result).toBe('Success');
    });

    test('should handle different status codes', async () => {
      const statusCodes = [200, 201, 204, 400, 401, 403, 404, 500];

      for (const statusCode of statusCodes) {
        (fetch as jest.Mock).mockResolvedValueOnce({
          ok: statusCode >= 200 && statusCode < 300,
          status: statusCode,
          json: async () => ({ message: `Status ${statusCode}` }),
        });

        if (statusCode >= 200 && statusCode < 300) {
          await expect(login('test@example.com', 'password123')).resolves.toBeDefined();
        } else {
          await expect(login('test@example.com', 'password123')).rejects.toThrow();
        }
      }
    });
  });
});