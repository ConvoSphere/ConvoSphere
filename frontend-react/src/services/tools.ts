import api from "./api";

export interface Tool {
  id: string;
  name: string;
  description: string;
  version: string;
  category: string;
  function_name: string;
  parameters_schema: any;
  implementation_path: string;
  is_builtin: boolean;
  is_enabled: boolean;
  requires_auth: boolean;
  required_permissions: string[];
  rate_limit: string;
  tags: string[];
  metadata: any;
  creator_id: string;
  created_at: string;
  updated_at: string;
  can_use: boolean;
}

export interface ToolCreate {
  name: string;
  description: string;
  category: string;
  version: string;
  function_name: string;
  parameters_schema: any;
  implementation_path: string;
  is_builtin: boolean;
  is_enabled: boolean;
  requires_auth: boolean;
  required_permissions: string[];
  rate_limit: string;
  tags: string[];
  tool_metadata: any;
}

export async function getTools(
  category?: string,
  search?: string,
): Promise<Tool[]> {
  const params = new URLSearchParams();
  if (category) params.append("category", category);
  if (search) params.append("search", search);

  const response = await api.get(`/tools?${params.toString()}`);
  return response.data.tools || response.data;
}

export async function getTool(id: string): Promise<Tool> {
  const response = await api.get(`/tools/${id}`);
  return response.data;
}

export async function createTool(toolData: ToolCreate): Promise<Tool> {
  const response = await api.post("/tools", toolData);
  return response.data;
}

export async function updateTool(
  id: string,
  toolData: Partial<ToolCreate>,
): Promise<Tool> {
  const response = await api.put(`/tools/${id}`, toolData);
  return response.data;
}

export async function deleteTool(id: string): Promise<void> {
  await api.delete(`/tools/${id}`);
}

export async function toggleToolEnabled(id: string, enabled?: boolean): Promise<Tool> {
  const params = enabled === undefined ? "" : `?enabled=${enabled}`;
  const response = await api.post(`/tools/${id}/toggle${params}`);
  return response.data;
}

export async function runTool(id: string, params: any) {
  const response = await api.post(`/tools/${id}/run`, params);
  return response.data;
}

export async function getToolCategories(): Promise<string[]> {
  const response = await api.get("/tools/categories/list");
  return response.data;
}
