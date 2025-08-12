import { create } from "zustand";
import {
  domainGroupsService,
  type DomainGroup,
  type DomainGroupCreate,
  type DomainGroupUpdate,
  type UserAssignment,
  type BulkUserAssignment,
  type GroupPermissions,
} from "../services/domainGroups";

interface DomainGroupsState {
  // State
  groups: DomainGroup[];
  selectedGroup: DomainGroup | null;
  groupUsers: UserAssignment[];
  groupPermissions: GroupPermissions | null;
  loading: boolean;
  error: string | null;
  searchQuery: string;

  // Actions
  fetchGroups: () => Promise<void>;
  fetchGroup: (groupId: string) => Promise<void>;
  createGroup: (groupData: DomainGroupCreate) => Promise<void>;
  updateGroup: (groupId: string, groupData: DomainGroupUpdate) => Promise<void>;
  deleteGroup: (groupId: string) => Promise<void>;
  fetchGroupUsers: (groupId: string) => Promise<void>;
  assignUser: (
    groupId: string,
    userId: string,
    role: "member" | "admin" | "viewer",
  ) => Promise<void>;
  bulkAssignUsers: (assignment: BulkUserAssignment) => Promise<void>;
  removeUser: (groupId: string, userId: string) => Promise<void>;
  updateUserRole: (
    groupId: string,
    userId: string,
    role: "member" | "admin" | "viewer",
  ) => Promise<void>;
  fetchGroupPermissions: (groupId: string) => Promise<void>;
  updateGroupPermissions: (
    groupId: string,
    permissions: GroupPermissions["permissions"],
  ) => Promise<void>;
  searchGroups: (query: string) => Promise<void>;
  setSelectedGroup: (group: DomainGroup | null) => void;
  setSearchQuery: (query: string) => void;
  clearError: () => void;
  reset: () => void;
}

export const useDomainGroupsStore = create<DomainGroupsState>((set, get) => ({
  // Initial state
  groups: [],
  selectedGroup: null,
  groupUsers: [],
  groupPermissions: null,
  loading: false,
  error: null,
  searchQuery: "",

  // Actions
  fetchGroups: async () => {
    set({ loading: true, error: null });
    try {
      const groups = await domainGroupsService.getGroups();
      set({ groups, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch domain groups",
        loading: false,
      });
    }
  },

  fetchGroup: async (groupId: string) => {
    set({ loading: true, error: null });
    try {
      const group = await domainGroupsService.getGroup(groupId);
      set({ selectedGroup: group, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch domain group",
        loading: false,
      });
    }
  },

  createGroup: async (groupData: DomainGroupCreate) => {
    set({ loading: true, error: null });
    try {
      const newGroup = await domainGroupsService.createGroup(groupData);
      const { groups } = get();
      set({
        groups: [...groups, newGroup],
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to create domain group",
        loading: false,
      });
    }
  },

  updateGroup: async (groupId: string, groupData: DomainGroupUpdate) => {
    set({ loading: true, error: null });
    try {
      const updatedGroup = await domainGroupsService.updateGroup(
        groupId,
        groupData,
      );
      const { groups, selectedGroup } = get();

      const updatedGroups = groups.map((group) =>
        group.id === groupId ? updatedGroup : group,
      );

      set({
        groups: updatedGroups,
        selectedGroup:
          selectedGroup?.id === groupId ? updatedGroup : selectedGroup,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to update domain group",
        loading: false,
      });
    }
  },

  deleteGroup: async (groupId: string) => {
    set({ loading: true, error: null });
    try {
      await domainGroupsService.deleteGroup(groupId);
      const { groups, selectedGroup } = get();

      const updatedGroups = groups.filter((group) => group.id !== groupId);

      set({
        groups: updatedGroups,
        selectedGroup: selectedGroup?.id === groupId ? null : selectedGroup,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to delete domain group",
        loading: false,
      });
    }
  },

  fetchGroupUsers: async (groupId: string) => {
    set({ loading: true, error: null });
    try {
      const users = await domainGroupsService.getGroupUsers(groupId);
      set({ groupUsers: users, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch group users",
        loading: false,
      });
    }
  },

  assignUser: async (
    groupId: string,
    userId: string,
    role: "member" | "admin" | "viewer",
  ) => {
    set({ loading: true, error: null });
    try {
      await domainGroupsService.assignUser(groupId, userId, role);
      await get().fetchGroupUsers(groupId);
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to assign user to group",
        loading: false,
      });
    }
  },

  bulkAssignUsers: async (assignment: BulkUserAssignment) => {
    set({ loading: true, error: null });
    try {
      await domainGroupsService.bulkAssignUsers(assignment);
      await get().fetchGroupUsers(assignment.groupId);
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to bulk assign users",
        loading: false,
      });
    }
  },

  removeUser: async (groupId: string, userId: string) => {
    set({ loading: true, error: null });
    try {
      await domainGroupsService.removeUser(groupId, userId);
      await get().fetchGroupUsers(groupId);
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to remove user from group",
        loading: false,
      });
    }
  },

  updateUserRole: async (
    groupId: string,
    userId: string,
    role: "member" | "admin" | "viewer",
  ) => {
    set({ loading: true, error: null });
    try {
      await domainGroupsService.updateUserRole(groupId, userId, role);
      await get().fetchGroupUsers(groupId);
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to update user role",
        loading: false,
      });
    }
  },

  fetchGroupPermissions: async (groupId: string) => {
    set({ loading: true, error: null });
    try {
      const permissions =
        await domainGroupsService.getGroupPermissions(groupId);
      set({ groupPermissions: permissions, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch group permissions",
        loading: false,
      });
    }
  },

  updateGroupPermissions: async (
    groupId: string,
    permissions: GroupPermissions["permissions"],
  ) => {
    set({ loading: true, error: null });
    try {
      const updatedPermissions =
        await domainGroupsService.updateGroupPermissions(groupId, permissions);
      set({ groupPermissions: updatedPermissions, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to update group permissions",
        loading: false,
      });
    }
  },

  searchGroups: async (query: string) => {
    set({ loading: true, error: null, searchQuery: query });
    try {
      const groups = await domainGroupsService.searchGroups(query);
      set({ groups, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to search groups",
        loading: false,
      });
    }
  },

  setSelectedGroup: (group: DomainGroup | null) => {
    set({ selectedGroup: group });
  },

  setSearchQuery: (query: string) => {
    set({ searchQuery: query });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      groups: [],
      selectedGroup: null,
      groupUsers: [],
      groupPermissions: null,
      loading: false,
      error: null,
      searchQuery: "",
    });
  },
}));
