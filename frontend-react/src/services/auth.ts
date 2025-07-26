import api from "./api";

export async function login(username: string, password: string) {
  const response = await api.post("/v1/auth/login", { username, password });
  const { access_token } = response.data;
  localStorage.setItem("token", access_token);
  return access_token;
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
}
