import { useState, useCallback, useEffect } from 'react';
import { message } from 'antd';
import { User, UserFormData } from '../types/admin.types';

export const useUserManagement = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userForm] = useState(() => ({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'user',
    status: 'active',
  }));

  const loadUsers = useCallback(async () => {
    setLoading(true);
    try {
      // Mock data for now - replace with actual API call
      const mockUsers: User[] = [
        {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          role: 'super_admin',
          status: 'active',
          createdAt: '2024-01-01T00:00:00Z',
          lastLogin: '2024-01-15T10:30:00Z',
          loginCount: 150,
          first_name: 'Admin',
          last_name: 'User',
          email_verified: true,
        },
        {
          id: 2,
          username: 'user1',
          email: 'user1@example.com',
          role: 'user',
          status: 'active',
          createdAt: '2024-01-02T00:00:00Z',
          lastLogin: '2024-01-14T15:20:00Z',
          loginCount: 25,
          first_name: 'John',
          last_name: 'Doe',
          email_verified: true,
        },
      ];
      setUsers(mockUsers);
    } catch (error) {
      message.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleUserSave = useCallback(async (userData: UserFormData) => {
    try {
      if (selectedUser) {
        // Update existing user
        const updatedUsers = users.map(user =>
          user.id === selectedUser.id ? { ...user, ...userData } : user
        );
        setUsers(updatedUsers);
        message.success('User updated successfully');
      } else {
        // Create new user
        const newUser: User = {
          id: Date.now(),
          username: userData.username,
          email: userData.email,
          role: userData.role as User['role'],
          status: userData.status as User['status'],
          createdAt: new Date().toISOString(),
          lastLogin: '',
          loginCount: 0,
          first_name: userData.first_name,
          last_name: userData.last_name,
          email_verified: false,
        };
        setUsers(prev => [...prev, newUser]);
        message.success('User created successfully');
      }
      setUserModalVisible(false);
      setSelectedUser(null);
    } catch (error) {
      message.error('Failed to save user');
    }
  }, [selectedUser, users]);

  const handleUserDelete = useCallback(async (userId: number) => {
    try {
      setUsers(prev => prev.filter(user => user.id !== userId));
      message.success('User deleted successfully');
    } catch (error) {
      message.error('Failed to delete user');
    }
  }, []);

  const handleUserStatusChange = useCallback(async (userId: number, status: string) => {
    try {
      setUsers(prev =>
        prev.map(user =>
          user.id === userId ? { ...user, status: status as User['status'] } : user
        )
      );
      message.success('User status updated successfully');
    } catch (error) {
      message.error('Failed to update user status');
    }
  }, []);

  const handleUserRoleChange = useCallback(async (userId: number, role: string) => {
    try {
      setUsers(prev =>
        prev.map(user =>
          user.id === userId ? { ...user, role: role as User['role'] } : user
        )
      );
      message.success('User role updated successfully');
    } catch (error) {
      message.error('Failed to update user role');
    }
  }, []);

  const openUserModal = useCallback((user: User | null = null) => {
    setSelectedUser(user);
    setUserModalVisible(true);
  }, []);

  const closeUserModal = useCallback(() => {
    setSelectedUser(null);
    setUserModalVisible(false);
  }, []);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  return {
    users,
    loading,
    userModalVisible,
    selectedUser,
    userForm,
    loadUsers,
    handleUserSave,
    handleUserDelete,
    handleUserStatusChange,
    handleUserRoleChange,
    openUserModal,
    closeUserModal,
  };
};