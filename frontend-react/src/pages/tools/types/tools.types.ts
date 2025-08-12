export interface Tool {
  id: number;
  name: string;
  description: string;
  category: string;
  isActive: boolean;
  parameters: ToolParameter[];
  executionTime: number;
  successRate: number;
  lastUsed: string;
  usageCount: number;
  tags: string[];
  version: string;
  author: string;
}

export interface ToolParameter {
  name: string;
  type: "string" | "number" | "boolean" | "file" | "select";
  required: boolean;
  description: string;
  defaultValue?: any;
  options?: string[];
}

export interface ToolExecution {
  id: string;
  toolId: number;
  toolName: string;
  parameters: Record<string, any>;
  result: any;
  status: "success" | "error" | "running";
  executionTime: number;
  timestamp: string;
  error?: string;
}

export interface ToolCategory {
  value: string;
  label: string;
  icon: React.ReactNode;
}

export interface ToolStats {
  total: number;
  active: number;
  totalExecutions: number;
  successRate: string;
}

export interface ToolFilter {
  searchQuery: string;
  activeTab: string;
  category: string;
}
