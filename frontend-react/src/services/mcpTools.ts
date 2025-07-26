import api from "./api";

export async function getMcpTools() {
  const response = await api.get("/mcp/tools");
  return response.data;
}

export async function runMcpTool(id: number, params: any) {
  const response = await api.post(`/mcp/tools/${id}/run`, params);
  return response.data;
}
