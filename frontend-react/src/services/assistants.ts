import api from "./api";
import config from "../config";

export async function getAssistants() {
  const response = await api.get(config.apiEndpoints.assistants);
  return response.data;
}

export async function addAssistant(data: {
  name: string;
  description: string;
}) {
  const response = await api.post(config.apiEndpoints.assistants, data);
  return response.data;
}

export async function deleteAssistant(id: number) {
  await api.delete(`${config.apiEndpoints.assistants}/${id}`);
}

export async function getDefaultAssistantId() {
  const response = await api.get(`${config.apiEndpoints.assistants}/default/id`);
  return response.data;
}

export async function setDefaultAssistant(assistantId: string) {
  const response = await api.post(`${config.apiEndpoints.assistants}/default/set`, {
    assistant_id: assistantId,
  });
  return response.data;
}

export async function getDefaultAssistant() {
  const response = await api.get(`${config.apiEndpoints.assistants}/default`);
  return response.data;
}
