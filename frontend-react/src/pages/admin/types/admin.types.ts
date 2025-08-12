export interface User {
  id: number;
  username: string;
  email: string;
  role: "user" | "admin" | "super_admin" | "moderator";
  status: "active" | "inactive" | "suspended";
  createdAt: string;
  lastLogin: string;
  loginCount: number;
  avatar?: string;
  first_name?: string;
  last_name?: string;
  email_verified?: boolean;
}

export interface SystemConfig {
  defaultLanguage: string;
  maxFileSize: number;
  maxUsers: number;
  enableRegistration: boolean;
  enableEmailVerification: boolean;
  maintenanceMode: boolean;
  debugMode: boolean;
}

export interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalConversations: number;
  totalMessages: number;
  totalDocuments: number;
  systemUptime: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
}

export interface AuditLog {
  id: string;
  userId: number;
  username: string;
  action: string;
  resource: string;
  details: string;
  ipAddress: string;
  timestamp: string;
  status: "success" | "failed";
}

export interface UserFormData {
  email: string;
  username: string;
  password?: string;
  first_name?: string;
  last_name?: string;
  role: string;
  status: string;
}

export interface SystemConfigFormData {
  defaultLanguage: string;
  maxFileSize: number;
  maxUsers: number;
  enableRegistration: boolean;
  enableEmailVerification: boolean;
  maintenanceMode: boolean;
  debugMode: boolean;
}
