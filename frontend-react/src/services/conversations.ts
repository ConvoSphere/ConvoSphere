import api from "./api";
import config from "../config";

export async function getConversations(options?: { mine?: boolean }) {
  const params = new URLSearchParams();
  if (options?.mine) params.set("mine", "1");
  const url = params.toString()
    ? `${config.apiEndpoints.conversations}?${params.toString()}`
    : config.apiEndpoints.conversations;
  const response = await api.get(url);
  return response.data;
}

export async function getConversation(id: number) {
  const response = await api.get(`${config.apiEndpoints.conversations}/${id}`);
  return response.data;
}
