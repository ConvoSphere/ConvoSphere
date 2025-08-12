import axios from "axios";
import config from "../config";

// Create a separate axios instance for auth operations to prevent loops
const authApi = axios.create({
  baseURL: config.apiUrl,
  withCredentials: true,
});

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export async function login(
  username: string,
  password: string,
): Promise<string> {
  const response = await authApi.post(`${config.apiEndpoints.auth}/login`, {
    username,
    password,
  });
  const { access_token, refresh_token } = response.data;

  // Store both tokens
  localStorage.setItem("token", access_token);
  localStorage.setItem("refresh_token", refresh_token);

  // Set token expiry (default 30 minutes)
  const expiresIn = response.data.expires_in || 30 * 60 * 1000;
  const expiryTime = Date.now() + expiresIn;
  localStorage.setItem("token_expiry", expiryTime.toString());

  return access_token;
}

export async function refreshToken(): Promise<string | null> {
  try {
    const refresh_token = localStorage.getItem("refresh_token");
    if (!refresh_token) {
      return null;
    }

    // Use the separate authApi instance to prevent loops
    const response = await authApi.post(`${config.apiEndpoints.auth}/refresh`, {
      refresh_token,
    });
    const { access_token, refresh_token: new_refresh_token } = response.data;

    // Update tokens
    localStorage.setItem("token", access_token);
    localStorage.setItem("refresh_token", new_refresh_token);

    // Update expiry
    const expiresIn = response.data.expires_in || 30 * 60 * 1000;
    const expiryTime = Date.now() + expiresIn;
    localStorage.setItem("token_expiry", expiryTime.toString());

    return access_token;
  } catch (error) {
    console.error("Token refresh failed:", error);
    // Clear invalid tokens
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("token_expiry");
    return null;
  }
}

export function isTokenExpired(): boolean {
  const expiryTime = localStorage.getItem("token_expiry");
  if (!expiryTime) return true;

  // Add 5 minute buffer before expiry
  const buffer = 5 * 60 * 1000;
  return Date.now() > parseInt(expiryTime) - buffer;
}

export async function register(
  username: string,
  password: string,
  email: string,
) {
  const response = await authApi.post(`${config.apiEndpoints.auth}/register`, {
    username,
    password,
    email,
  });
  // Registration doesn't return a token, user needs to login after registration
  return null;
}

export async function getSSOProviders() {
  const response = await authApi.get(
    `${config.apiEndpoints.auth}/sso/providers`,
  );
  return response.data.providers;
}

export async function ssoLogin(provider: string) {
  // Redirect to backend SSO login endpoint
  window.location.href = `/api/v1/auth/sso/login/${provider}`;
}

export async function handleSSOCallback(
  provider: string,
  code: string,
  state?: string,
) {
  // Handle SSO callback with authorization code
  const response = await authApi.get(
    `${config.apiEndpoints.auth}/sso/callback/${provider}?code=${code}${state ? `&state=${state}` : ""}`,
  );
  const { access_token } = response.data;
  localStorage.setItem("token", access_token);
  return access_token;
}

export async function ssoLink(provider: string) {
  // Call backend SSO link endpoint
  const response = await authApi.post(
    `${config.apiEndpoints.auth}/sso/link/${provider}`,
  );
  return response.data;
}

export async function ssoUnlink(provider: string) {
  // Call backend SSO unlink endpoint
  const response = await authApi.get(
    `${config.apiEndpoints.auth}/sso/unlink/${provider}`,
  );
  return response.data;
}

export async function getUserProvisioningStatus(userId: string) {
  // Get user provisioning status
  const response = await authApi.get(
    `${config.apiEndpoints.auth}/sso/provisioning/status/${userId}`,
  );
  return response.data;
}

export async function bulkSyncUsers(provider: string, userList: any[]) {
  // Bulk sync users from SSO provider
  const response = await authApi.post(
    `${config.apiEndpoints.auth}/sso/bulk-sync/${provider}`,
    {
      user_list: userList,
    },
  );
  return response.data;
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("token_expiry");
}

// Password Reset Functions
export async function forgotPassword(
  email: string,
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await authApi.post(
      `${config.apiEndpoints.auth}/forgot-password`,
      {
        email,
      },
    );

    return {
      success: true,
      message: response.data.message || "Password reset email sent",
    };
  } catch (error: any) {
    console.error("Forgot password failed:", error);
    return {
      success: false,
      message:
        error.response?.data?.detail || "Failed to send password reset email",
    };
  }
}

export async function resetPassword(
  token: string,
  newPassword: string,
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await authApi.post(
      `${config.apiEndpoints.auth}/reset-password`,
      {
        token,
        new_password: newPassword,
      },
    );

    return {
      success: true,
      message: response.data.message || "Password reset successfully",
    };
  } catch (error: any) {
    console.error("Reset password failed:", error);
    return {
      success: false,
      message: error.response?.data?.detail || "Failed to reset password",
    };
  }
}

export async function validateResetToken(
  token: string,
): Promise<{ valid: boolean; message: string }> {
  try {
    const response = await authApi.post(
      `${config.apiEndpoints.auth}/validate-reset-token`,
      {
        token,
      },
    );

    return {
      valid: response.data.valid,
      message: response.data.message,
    };
  } catch (error: any) {
    console.error("Token validation failed:", error);
    return {
      valid: false,
      message: error.response?.data?.detail || "Failed to validate token",
    };
  }
}
