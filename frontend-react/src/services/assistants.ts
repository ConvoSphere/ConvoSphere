import api from "./api";
import config from "../config";

export type AssistantDto = {
  id: string;
  name: string;
  description?: string;
  personality?: string;
  system_prompt: string;
  instructions?: string;
  model: string;
  temperature: number | string;
  max_tokens: number | string;
  status: string;
  is_public: boolean;
  is_template: boolean;
  category?: string;
  tags: string[];
  tools_config: any[];
  tools_enabled: boolean;
  creator_id: string;
  created_at?: string;
  updated_at?: string;
};

export function mapAssistant(dto: AssistantDto) {
  return {
    id: dto.id,
    name: dto.name,
    description: dto.description,
    personality: dto.personality,
    model: dto.model,
    temperature: dto.temperature,
    isActive: dto.status === "active",
    knowledgeBaseIds: [],
    toolIds: (dto.tools_config || []).map((t) => t.id).filter(Boolean),
    usageCount: 0,
    avgRating: 0,
    tags: dto.tags || [],
    ownerId: dto.creator_id,
    visibility: dto.is_public ? "public" : "private",
  };
}

export async function getAssistants() {
  const response = await api.get(config.apiEndpoints.assistants);
  const data = response.data as AssistantDto[];
  return Array.isArray(data) ? data.map(mapAssistant) : data;
}

export async function addAssistant(data: {
  name: string;
  description: string;
}) {
  const response = await api.post(config.apiEndpoints.assistants, data);
  return response.data;
}

export async function updateAssistant(id: string, data: Partial<AssistantDto>) {
  const response = await api.put(`${config.apiEndpoints.assistants}/${id}`, data);
  return response.data as AssistantDto;
}

export async function deleteAssistant(id: number) {
  await api.delete(`${config.apiEndpoints.assistants}/${id}`);
}

export async function getDefaultAssistantId() {
  const response = await api.get(
    `${config.apiEndpoints.assistants}/default/id`,
  );
  return response.data;
}

export async function setDefaultAssistant(assistantId: string) {
  const response = await api.post(
    `${config.apiEndpoints.assistants}/default/set`,
    {
      assistant_id: assistantId,
    },
  );
  return response.data;
}

export async function getDefaultAssistant() {
  const response = await api.get(`${config.apiEndpoints.assistants}/default`);
  return response.data;
}

export async function getAssistantModels() {
  const response = await api.get(`${config.apiEndpoints.assistants}/models`);
  return response.data;
}
