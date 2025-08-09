import React from 'react';
import {
  Table,
  Button,
  Space,
  Avatar,
  Tag,
  Switch,
  Modal,
  Form,
  Input,
  Select,
  Popconfirm,
  Tooltip,
  message,
} from 'antd';
import {
  UserOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CrownOutlined,
  SafetyOutlined,
  MailOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useUserManagement } from '../hooks/useUserManagement';
import { User, UserFormData } from '../types/admin.types';
import ModernCard from '../../../components/ModernCard';
import ModernButton from '../../../components/ModernButton';

const { Option } = Select;

const UserManagement: React.FC = () => {
  const { t } = useTranslation();
  const {
    users,
    loading,
    userModalVisible,
    selectedUser,
    userForm,
    handleUserSave,
    handleUserDelete,
    handleUserStatusChange,
    handleUserRoleChange,
    openUserModal,
    closeUserModal,
  } = useUserManagement();

  const [form] = Form.useForm();

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'super_admin':
        return <CrownOutlined style={{ color: '#ff4d4f' }} />;
      case 'admin':
        return <SafetyOutlined style={{ color: '#1890ff' }} />;
      default:
        return <UserOutlined style={{ color: '#52c41a' }} />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'red';
      case 'admin':
        return 'blue';
      case 'moderator':
        return 'orange';
      default:
        return 'green';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'inactive':
        return 'orange';
      case 'suspended':
        return 'red';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleEditUser = (user: User) => {
    form.setFieldsValue({
      email: user.email,
      username: user.username,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      role: user.role,
      status: user.status,
    });
    openUserModal(user);
  };

  const handleCreateUser = () => {
    form.resetFields();
    openUserModal();
  };

  const handleFormSubmit = async (values: UserFormData) => {
    await handleUserSave(values);
    form.resetFields();
  };

  const columns = [
    {
      title: t('admin.users.avatar'),
      key: 'avatar',
      width: 60,
      render: (user: User) => (
        <Avatar
          icon={getRoleIcon(user.role)}
          src={user.avatar}
          size="small"
        />
      ),
    },
    {
      title: t('admin.users.username'),
      dataIndex: 'username',
      key: 'username',
      render: (text: string, user: User) => (
        <Space>
          <span>{text}</span>
          {user.email_verified && (
            <MailOutlined style={{ color: '#52c41a' }} />
          )}
        </Space>
      ),
    },
    {
      title: t('admin.users.email'),
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: t('admin.users.role'),
      dataIndex: 'role',
      key: 'role',
      render: (role: string, user: User) => (
        <Select
          value={role}
          style={{ width: 120 }}
          onChange={(value) => handleUserRoleChange(user.id, value)}
        >
          <Option value="user">{t('admin.roles.user')}</Option>
          <Option value="moderator">{t('admin.roles.moderator')}</Option>
          <Option value="admin">{t('admin.roles.admin')}</Option>
          <Option value="super_admin">{t('admin.roles.super_admin')}</Option>
        </Select>
      ),
    },
    {
      title: t('admin.users.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string, user: User) => (
        <Switch
          checked={status === 'active'}
          onChange={(checked) =>
            handleUserStatusChange(user.id, checked ? 'active' : 'inactive')
          }
        />
      ),
    },
    {
      title: t('admin.users.created'),
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => formatDate(date),
    },
    {
      title: t('admin.users.last_login'),
      dataIndex: 'lastLogin',
      key: 'lastLogin',
      render: (date: string) => date ? formatDate(date) : t('admin.users.never'),
    },
    {
      title: t('admin.users.actions'),
      key: 'actions',
      width: 120,
      render: (user: User) => (
        <Space size="small">
          <Tooltip title={t('admin.users.view')}>
            <Button
              type="text"
              icon={<EyeOutlined />}
              size="small"
              onClick={() => handleEditUser(user)}
            />
          </Tooltip>
          <Tooltip title={t('admin.users.edit')}>
            <Button
              type="text"
              icon={<EditOutlined />}
              size="small"
              onClick={() => handleEditUser(user)}
            />
          </Tooltip>
          <Popconfirm
            title={t('admin.users.delete_confirm')}
            onConfirm={() => handleUserDelete(user.id)}
            okText={t('common.yes')}
            cancelText={t('common.no')}
          >
            <Tooltip title={t('admin.users.delete')}>
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                size="small"
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <ModernCard
        title={t('admin.users.title')}
        extra={
          <ModernButton
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateUser}
          >
            {t('admin.users.create')}
          </ModernButton>
        }
      >
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} users`,
          }}
        />
      </ModernCard>

      <Modal
        title={
          selectedUser
            ? t('admin.users.edit_user')
            : t('admin.users.create_user')
        }
        open={userModalVisible}
        onCancel={closeUserModal}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFormSubmit}
          initialValues={userForm}
        >
          <Form.Item
            name="email"
            label={t('admin.users.email')}
            rules={[
              { required: true, message: t('admin.users.email_required') },
              { type: 'email', message: t('admin.users.email_invalid') },
            ]}
          >
            <Input prefix={<MailOutlined />} />
          </Form.Item>

          <Form.Item
            name="username"
            label={t('admin.users.username')}
            rules={[
              { required: true, message: t('admin.users.username_required') },
            ]}
          >
            <Input prefix={<UserOutlined />} />
          </Form.Item>

          {!selectedUser && (
            <Form.Item
              name="password"
              label={t('admin.users.password')}
              rules={[
                { required: true, message: t('admin.users.password_required') },
                { min: 8, message: t('admin.users.password_min_length') },
              ]}
            >
              <Input.Password />
            </Form.Item>
          )}

          <Form.Item name="first_name" label={t('admin.users.first_name')}>
            <Input />
          </Form.Item>

          <Form.Item name="last_name" label={t('admin.users.last_name')}>
            <Input />
          </Form.Item>

          <Form.Item
            name="role"
            label={t('admin.users.role')}
            rules={[{ required: true, message: t('admin.users.role_required') }]}
          >
            <Select>
              <Option value="user">{t('admin.roles.user')}</Option>
              <Option value="moderator">{t('admin.roles.moderator')}</Option>
              <Option value="admin">{t('admin.roles.admin')}</Option>
              <Option value="super_admin">{t('admin.roles.super_admin')}</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="status"
            label={t('admin.users.status')}
            rules={[{ required: true, message: t('admin.users.status_required') }]}
          >
            <Select>
              <Option value="active">{t('admin.status.active')}</Option>
              <Option value="inactive">{t('admin.status.inactive')}</Option>
              <Option value="suspended">{t('admin.status.suspended')}</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit">
                {selectedUser ? t('common.update') : t('common.create')}
              </ModernButton>
              <Button onClick={closeUserModal}>{t('common.cancel')}</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;