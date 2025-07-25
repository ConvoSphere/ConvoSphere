import api from './api';

export async function getAssistants() {
  const response = await api.get('/assistants');
  return response.data;
}

export async function addAssistant(data: { name: string; description: string }) {
  const response = await api.post('/assistants', data);
  return response.data;
}

export async function deleteAssistant(id: number) {
  await api.delete(`/assistants/${id}`);
}

export async function getDefaultAssistantId() {
  const response = await api.get('/assistants/default/id');
  return response.data;
}

export async function setDefaultAssistant(assistantId: string) {
  const response = await api.post('/assistants/default/set', { assistant_id: assistantId });
  return response.data;
}

export async function getDefaultAssistant() {
  const response = await api.get('/assistants/default');
  return response.data;
} 