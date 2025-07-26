import { renderHook, act } from "@testing-library/react";
import { useAuthStore } from "../authStore";
import * as authService from "../../services/auth";

// Mock the auth service
jest.mock("../../services/auth");

describe("AuthStore", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset the store to initial state
    act(() => {
      useAuthStore.getState().logout();
    });
  });

  describe("Initial State", () => {
    test("should have correct initial state", () => {
      const { result } = renderHook(() => useAuthStore());

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe("Login", () => {
    test("should login successfully", async () => {
      const mockUser = {
        id: "1",
        email: "test@example.com",
        username: "testuser",
      };
      const mockToken = "fake-token";

      jest.mocked(authService.login).mockResolvedValue({
        user: mockUser,
        token: mockToken,
      });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe(mockToken);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    test("should handle login error", async () => {
      const errorMessage = "Invalid credentials";
      jest.mocked(authService.login).mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login("test@example.com", "wrongpassword");
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
    });

    test("should set loading state during login", async () => {
      jest
        .mocked(authService.login)
        .mockImplementation(
          () => new Promise((resolve) => setTimeout(resolve, 100)),
        );

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.login("test@example.com", "password123");
      });

      expect(result.current.loading).toBe(true);
    });

    test("should clear error on successful login", async () => {
      // First, set an error
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setError("Previous error");
      });

      expect(result.current.error).toBe("Previous error");

      // Then login successfully
      const mockUser = { id: "1", email: "test@example.com" };
      const mockToken = "fake-token";

      jest.mocked(authService.login).mockResolvedValue({
        user: mockUser,
        token: mockToken,
      });

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe("Register", () => {
    test("should register successfully", async () => {
      const mockUser = {
        id: "1",
        email: "test@example.com",
        username: "testuser",
      };
      const mockToken = "fake-token";

      jest.mocked(authService.register).mockResolvedValue({
        user: mockUser,
        token: mockToken,
      });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.register({
          email: "test@example.com",
          username: "testuser",
          password: "password123",
          fullName: "Test User",
        });
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe(mockToken);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    test("should handle registration error", async () => {
      const errorMessage = "Email already exists";
      jest
        .mocked(authService.register)
        .mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.register({
          email: "existing@example.com",
          username: "existinguser",
          password: "password123",
          fullName: "Existing User",
        });
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
    });
  });

  describe("Logout", () => {
    test("should logout successfully", async () => {
      // First, login
      const mockUser = { id: "1", email: "test@example.com" };
      const mockToken = "fake-token";

      jest.mocked(authService.login).mockResolvedValue({
        user: mockUser,
        token: mockToken,
      });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      expect(result.current.isAuthenticated).toBe(true);

      // Then logout
      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    test("should call logout API", async () => {
      jest.mocked(authService.logout).mockResolvedValue(undefined);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.logout();
      });

      expect(authService.logout).toHaveBeenCalled();
    });

    test("should handle logout error gracefully", async () => {
      jest
        .mocked(authService.logout)
        .mockRejectedValue(new Error("Network error"));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        try {
          await result.current.logout();
        } catch (error) {
          // Expected error, continue
        }
      });

      // Should still clear local state even if API call fails
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe("Token Management", () => {
    test("should refresh token successfully", async () => {
      const newToken = "new-fake-token";
      jest
        .mocked(authService.refreshToken)
        .mockResolvedValue({ token: newToken });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.token).toBe(newToken);
      expect(result.current.loading).toBe(false);
    });

    test("should handle token refresh error", async () => {
      jest
        .mocked(authService.refreshToken)
        .mockRejectedValue(new Error("Token expired"));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.token).toBeNull();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBe("Token expired");
    });

    test("should validate token", async () => {
      jest.mocked(authService.validateToken).mockResolvedValue(true);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        const isValid = await result.current.validateToken("fake-token");
        expect(isValid).toBe(true);
      });
    });
  });

  describe("User Management", () => {
    test("should update user profile", async () => {
      const updatedUser = {
        id: "1",
        email: "test@example.com",
        fullName: "Updated Name",
      };
      jest.mocked(authService.updateProfile).mockResolvedValue(updatedUser);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.updateProfile({ fullName: "Updated Name" });
      });

      expect(result.current.user).toEqual(updatedUser);
    });

    test("should handle profile update error", async () => {
      jest
        .mocked(authService.updateProfile)
        .mockRejectedValue(new Error("Update failed"));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.updateProfile({ fullName: "Updated Name" });
      });

      expect(result.current.error).toBe("Update failed");
    });

    test("should change password", async () => {
      jest.mocked(authService.changePassword).mockResolvedValue(undefined);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.changePassword("oldpass", "newpass");
      });

      expect(authService.changePassword).toHaveBeenCalledWith(
        "oldpass",
        "newpass",
      );
    });
  });

  describe("Persistence", () => {
    test("should load user from localStorage on init", () => {
      const mockUser = { id: "1", email: "test@example.com" };
      const mockToken = "fake-token";

      // Mock localStorage
      const localStorageMock = {
        getItem: jest.fn((key: string) => {
          if (key === "user") return JSON.stringify(mockUser);
          if (key === "token") return mockToken;
          return null;
        }),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      };
      Object.defineProperty(window, "localStorage", {
        value: localStorageMock,
      });

      const { result } = renderHook(() => useAuthStore());

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe(mockToken);
      expect(result.current.isAuthenticated).toBe(true);
    });

    test("should save user to localStorage on login", async () => {
      const mockUser = { id: "1", email: "test@example.com" };
      const mockToken = "fake-token";

      const localStorageMock = {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      };
      Object.defineProperty(window, "localStorage", {
        value: localStorageMock,
      });

      jest.mocked(authService.login).mockResolvedValue({
        user: mockUser,
        token: mockToken,
      });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login("test@example.com", "password123");
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "user",
        JSON.stringify(mockUser),
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith("token", mockToken);
    });

    test("should clear localStorage on logout", async () => {
      const localStorageMock = {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      };
      Object.defineProperty(window, "localStorage", {
        value: localStorageMock,
      });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.logout();
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith("user");
      expect(localStorageMock.removeItem).toHaveBeenCalledWith("token");
    });
  });

  describe("Error Handling", () => {
    test("should set error message", () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setError("Test error message");
      });

      expect(result.current.error).toBe("Test error message");
    });

    test("should clear error message", () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setError("Test error message");
      });

      expect(result.current.error).toBe("Test error message");

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe("Loading States", () => {
    test("should set loading state", () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.loading).toBe(true);
    });

    test("should clear loading state", () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.loading).toBe(true);

      act(() => {
        result.current.setLoading(false);
      });

      expect(result.current.loading).toBe(false);
    });
  });

  describe("Selectors", () => {
    test("should return correct isAuthenticated value", () => {
      const { result } = renderHook(() => useAuthStore());

      expect(result.current.isAuthenticated).toBe(false);

      act(() => {
        result.current.user = { id: "1", email: "test@example.com" };
        result.current.token = "fake-token";
      });

      expect(result.current.isAuthenticated).toBe(true);
    });

    test("should return user display name", () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.user = {
          id: "1",
          email: "test@example.com",
          username: "testuser",
          fullName: "Test User",
        };
      });

      expect(result.current.userDisplayName).toBe("Test User");
    });

    test("should fallback to username if no fullName", () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.user = {
          id: "1",
          email: "test@example.com",
          username: "testuser",
        };
      });

      expect(result.current.userDisplayName).toBe("testuser");
    });

    test("should fallback to email if no username or fullName", () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.user = {
          id: "1",
          email: "test@example.com",
        };
      });

      expect(result.current.userDisplayName).toBe("test@example.com");
    });
  });
});
