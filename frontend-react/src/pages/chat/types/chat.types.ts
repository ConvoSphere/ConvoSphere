export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
    tools_used?: string[];
    sources?: string[];
  };
  status?: 'sending' | 'sent' | 'error';
  error?: string;
}

export interface ChatThread {
  id: string;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
  user_id: string;
  assistant_id?: string;
  metadata?: {
    model?: string;
    total_tokens?: number;
    total_cost?: number;
    tags?: string[];
  };
}

export interface ChatSettings {
  model: string;
  temperature: number;
  max_tokens: number;
  use_knowledge_base: boolean;
  use_tools: boolean;
  assistant_id?: string;
  system_prompt?: string;
}

export interface ChatTool {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  parameters?: Record<string, any>;
}

export interface ChatAssistant {
  id: string;
  name: string;
  description: string;
  system_prompt: string;
  model: string;
  temperature: number;
  max_tokens: number;
  tools: ChatTool[];
  avatar?: string;
}

export interface ChatStreamingResponse {
  content: string;
  finish_reason?: string;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
}

export interface ChatError {
  message: string;
  code?: string;
  details?: any;
}

export interface ChatContext {
  thread: ChatThread | null;
  messages: ChatMessage[];
  settings: ChatSettings;
  assistant: ChatAssistant | null;
  isLoading: boolean;
  isStreaming: boolean;
  error: ChatError | null;
}

export interface ChatFormData {
  message: string;
  attachments?: File[];
}

export interface ChatExportOptions {
  format: 'json' | 'txt' | 'md' | 'pdf';
  include_metadata: boolean;
  include_sources: boolean;
}