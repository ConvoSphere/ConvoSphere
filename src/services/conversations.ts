import api from './api';

export async function getConversations() {
  const response = await api.get('/conversations');
  return response.data;
}

export async function getConversation(id: number) {
  const response = await api.get(`/conversations/${id}`);
  return response.data;
} 