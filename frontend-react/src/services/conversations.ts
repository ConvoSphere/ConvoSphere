import api from "./api";
import config from "../config";

export async function getConversations() {
  const response = await api.get(config.apiEndpoints.conversations);
  return response.data;
}

export async function getConversation(id: number) {
  const response = await api.get(`${config.apiEndpoints.conversations}/${id}`);
  return response.data;
}
