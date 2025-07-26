import api from "./api";

export async function getConversations() {
  const response = await api.get("/v1/conversations");
  return response.data;
}

export async function getConversation(id: number) {
  const response = await api.get(`/v1/conversations/${id}`);
  return response.data;
}
