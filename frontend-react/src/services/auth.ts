import api from "./api";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export async function login(username: string, password: string): Promise<string> {
  const response = await api.post("/v1/auth/login", { username, password });
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

    const response = await api.post("/v1/auth/refresh", { refresh_token });
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
  return Date.now() + buffer > parseInt(expiryTime);
}

export async function register(
  username: string,
  password: string,
  email: string,
) {
  const response = await api.post("/v1/auth/register", {
    username,
    password,
    email,
  });
  // Registration doesn't return a token, user needs to login after registration
  return null;
}

export async function getSSOProviders() {
  const response = await api.get("/v1/auth/sso/providers");
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
  const response = await api.get(
    `/v1/auth/sso/callback/${provider}?code=${code}${state ? `&state=${state}` : ""}`,
  );
  const { access_token } = response.data;
  localStorage.setItem("token", access_token);
  return access_token;
}

export async function ssoLink(provider: string) {
  // Call backend SSO link endpoint
  const response = await api.post(`/v1/auth/sso/link/${provider}`);
  return response.data;
}

export async function ssoUnlink(provider: string) {
  // Call backend SSO unlink endpoint
  const response = await api.get(`/v1/auth/sso/unlink/${provider}`);
  return response.data;
}

export async function getUserProvisioningStatus(userId: string) {
  // Get user provisioning status
  const response = await api.get(`/v1/auth/sso/provisioning/status/${userId}`);
  return response.data;
}

export async function bulkSyncUsers(provider: string, userList: any[]) {
  // Bulk sync users from SSO provider
  const response = await api.post(`/v1/auth/sso/bulk-sync/${provider}`, {
    user_list: userList,
  });
  return response.data;
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("token_expiry");
}
