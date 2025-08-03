import api from './api';
import config from '../config';

export interface DomainGroup {
  id: string;
  name: string;
  description: string;
  parentId: string | null;
  level: number;
  path: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  userCount: number;
  permissions: string[];
  metadata: Record<string, any>;
}

export interface DomainGroupCreate {
  name: string;
  description?: string;
  parentId?: string;
  permissions?: string[];
  metadata?: Record<string, any>;
}

export interface DomainGroupUpdate {
  name?: string;
  description?: string;
  parentId?: string;
  isActive?: boolean;
  permissions?: string[];
  metadata?: Record<string, any>;
}

export interface UserAssignment {
  userId: string;
  groupId: string;
  role: 'member' | 'admin' | 'viewer';
  assignedAt: string;
  assignedBy: string;
}

export interface BulkUserAssignment {
  userIds: string[];
  groupId: string;
  role: 'member' | 'admin' | 'viewer';
}

export interface GroupPermissions {
  groupId: string;
  permissions: {
    conversations: {
      read: boolean;
      write: boolean;
      delete: boolean;
    };
    knowledge: {
      read: boolean;
      write: boolean;
      delete: boolean;
    };
    assistants: {
      read: boolean;
      write: boolean;
      delete: boolean;
    };
    tools: {
      read: boolean;
      write: boolean;
      delete: boolean;
    };
    users: {
      read: boolean;
      write: boolean;
      delete: boolean;
    };
  };
}

export const domainGroupsService = {
  // Get all domain groups
  getGroups: async (): Promise<DomainGroup[]> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups`);
    return response.data;
  },

  // Get domain group by ID
  getGroup: async (groupId: string): Promise<DomainGroup> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups/${groupId}`);
    return response.data;
  },

  // Create new domain group
  createGroup: async (groupData: DomainGroupCreate): Promise<DomainGroup> => {
    const response = await api.post(`${config.apiEndpoints.domainGroups}/groups`, groupData);
    return response.data;
  },

  // Update domain group
  updateGroup: async (groupId: string, groupData: DomainGroupUpdate): Promise<DomainGroup> => {
    const response = await api.put(`${config.apiEndpoints.domainGroups}/groups/${groupId}`, groupData);
    return response.data;
  },

  // Delete domain group
  deleteGroup: async (groupId: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.domainGroups}/groups/${groupId}`);
  },

  // Get group hierarchy
  getGroupHierarchy: async (): Promise<DomainGroup[]> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups/hierarchy`);
    return response.data;
  },

  // Get users in group
  getGroupUsers: async (groupId: string): Promise<UserAssignment[]> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups/${groupId}/users`);
    return response.data;
  },

  // Assign user to group
  assignUser: async (groupId: string, userId: string, role: 'member' | 'admin' | 'viewer'): Promise<UserAssignment> => {
    const response = await api.post(`${config.apiEndpoints.domainGroups}/groups/${groupId}/users`, {
      userId,
      role,
    });
    return response.data;
  },

  // Bulk assign users to group
  bulkAssignUsers: async (assignment: BulkUserAssignment): Promise<UserAssignment[]> => {
    const response = await api.post(`${config.apiEndpoints.domainGroups}/groups/bulk-assign`, assignment);
    return response.data;
  },

  // Remove user from group
  removeUser: async (groupId: string, userId: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.domainGroups}/groups/${groupId}/users/${userId}`);
  },

  // Update user role in group
  updateUserRole: async (groupId: string, userId: string, role: 'member' | 'admin' | 'viewer'): Promise<UserAssignment> => {
    const response = await api.put(`${config.apiEndpoints.domainGroups}/groups/${groupId}/users/${userId}`, {
      role,
    });
    return response.data;
  },

  // Get group permissions
  getGroupPermissions: async (groupId: string): Promise<GroupPermissions> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups/${groupId}/permissions`);
    return response.data;
  },

  // Update group permissions
  updateGroupPermissions: async (groupId: string, permissions: GroupPermissions['permissions']): Promise<GroupPermissions> => {
    const response = await api.put(`${config.apiEndpoints.domainGroups}/groups/${groupId}/permissions`, {
      permissions,
    });
    return response.data;
  },

  // Get user's groups
  getUserGroups: async (userId: string): Promise<DomainGroup[]> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/users/${userId}/groups`);
    return response.data;
  },

  // Search groups
  searchGroups: async (query: string): Promise<DomainGroup[]> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups/search`, {
      params: { q: query },
    });
    return response.data;
  },

  // Get group statistics
  getGroupStats: async (groupId: string): Promise<any> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups/${groupId}/stats`);
    return response.data;
  },

  // Export group data
  exportGroupData: async (groupId: string, format: 'csv' | 'json' = 'csv'): Promise<Blob> => {
    const response = await api.get(`${config.apiEndpoints.domainGroups}/groups/${groupId}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },
};