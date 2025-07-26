import api from "./api";

export async function getAssistants() {
  const response = await api.get("/v1/assistants");
  return response.data;
}

export async function addAssistant(data: {
  name: string;
  description: string;
}) {
  const response = await api.post("/v1/assistants", data);
  return response.data;
}

export async function deleteAssistant(id: number) {
  await api.delete(`/v1/assistants/${id}`);
}

export async function getDefaultAssistantId() {
  const response = await api.get("/v1/assistants/default/id");
  return response.data;
}

export async function setDefaultAssistant(assistantId: string) {
  const response = await api.post("/v1/assistants/default/set", {
    assistant_id: assistantId,
  });
  return response.data;
}

export async function getDefaultAssistant() {
  const response = await api.get("/v1/assistants/default");
  return response.data;
}
