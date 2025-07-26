import api from "./api";

export async function getTools() {
  const response = await api.get("/tools");
  return response.data;
}

export async function runTool(id: number, params: any) {
  const response = await api.post(`/tools/${id}/run`, params);
  return response.data;
}
