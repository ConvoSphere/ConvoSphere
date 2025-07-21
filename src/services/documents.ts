import api from './api';

export async function getDocuments() {
  const response = await api.get('/knowledge/documents');
  return response.data;
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
} 