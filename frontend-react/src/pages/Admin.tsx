import React, { useEffect, useState } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Select, 
  Button, 
  message, 
  Spin, 
  Row, 
  Col, 
  Space, 
  Typography, 
  Switch, 
  Divider,
  Avatar,
  Tooltip,
  Popconfirm,
  Badge,
  Tabs,
  Statistic,
  Progress,
  Alert,
  Modal,
  Form,
  Input,
  DatePicker,
  Descriptions,
  List,
  Timeline
} from 'antd';
import { 
  UserOutlined, 
  SettingOutlined, 
  TeamOutlined,
  DashboardOutlined,
  SecurityScanOutlined,
  GlobalOutlined,
  BellOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  LockOutlined,
  UnlockOutlined,
  ExportOutlined,
  ImportOutlined,
  DownloadOutlined,
  UploadOutlined,
  BarChartOutlined,
  PieChartOutlined,
  LineChartOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

interface User {
  id: number;
  username: string;
  email: string;
  role: 'user' | 'admin' | 'super_admin' | 'moderator';
  status: 'active' | 'inactive' | 'suspended';
  createdAt: string;
  lastLogin: string;
  loginCount: number;
  avatar?: string;
}

interface SystemConfig {
  defaultLanguage: string;
  maxFileSize: number;
  maxUsers: number;
  enableRegistration: boolean;
  enableEmailVerification: boolean;
  maintenanceMode: boolean;
  debugMode: boolean;
}

interface SystemStats {
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

interface AuditLog {
  id: string;
  userId: number;
  username: string;
  action: string;
  resource: string;
  details: string;
  ipAddress: string;
  timestamp: string;
  status: 'success' | 'failed';
}

const Admin: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  
  const [users, setUsers] = useState<User[]>([]);
  const [systemConfig, setSystemConfig] = useState<SystemConfig | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');

  // Mock data for demonstration
  const mockUsers: User[] = [
    {
      id: 1,
      username: 'admin',
      email: 'admin@convosphere.com',
      role: 'super_admin',
      status: 'active',
      createdAt: '2024-01-01T00:00:00Z',
      lastLogin: '2024-01-15T10:30:00Z',
      loginCount: 1250
    },
    {
      id: 2,
      username: 'moderator1',
      email: 'moderator1@convosphere.com',
      role: 'moderator',
      status: 'active',
      createdAt: '2024-01-05T00:00:00Z',
      lastLogin: '2024-01-15T09:15:00Z',
      loginCount: 890
    },
    {
      id: 3,
      username: 'user1',
      email: 'user1@example.com',
      role: 'user',
      status: 'active',
      createdAt: '2024-01-10T00:00:00Z',
      lastLogin: '2024-01-15T08:45:00Z',
      loginCount: 450
    },
    {
      id: 4,
      username: 'user2',
      email: 'user2@example.com',
      role: 'user',
      status: 'suspended',
      createdAt: '2024-01-12T00:00:00Z',
      lastLogin: '2024-01-14T16:20:00Z',
      loginCount: 320
    }
  ];

  const mockSystemConfig: SystemConfig = {
    defaultLanguage: 'de',
    maxFileSize: 10485760,
    maxUsers: 1000,
    enableRegistration: true,
    enableEmailVerification: true,
    maintenanceMode: false,
    debugMode: false
  };

  const mockSystemStats: SystemStats = {
    totalUsers: 156,
    activeUsers: 89,
    totalConversations: 2847,
    totalMessages: 12543,
    totalDocuments: 456,
    systemUptime: 99.9,
    cpuUsage: 23.5,
    memoryUsage: 67.8,
    diskUsage: 45.2
  };

  const mockAuditLogs: AuditLog[] = [
    {
      id: '1',
      userId: 1,
      username: 'admin',
      action: 'LOGIN',
      resource: 'Authentication',
      details: 'Successful login',
      ipAddress: '192.168.1.100',
      timestamp: '2024-01-15T10:30:00Z',
      status: 'success'
    },
    {
      id: '2',
      userId: 2,
      username: 'moderator1',
      action: 'UPDATE_USER',
      resource: 'User Management',
      details: 'Updated user status',
      ipAddress: '192.168.1.101',
      timestamp: '2024-01-15T09:15:00Z',
      status: 'success'
    },
    {
      id: '3',
      userId: 4,
      username: 'user2',
      action: 'LOGIN',
      resource: 'Authentication',
      details: 'Failed login attempt',
      ipAddress: '192.168.1.102',
      timestamp: '2024-01-15T08:45:00Z',
      status: 'failed'
    }
  ];

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }

    // Simulate API calls
    setTimeout(() => {
      setUsers(mockUsers);
      setSystemConfig(mockSystemConfig);
      setSystemStats(mockSystemStats);
      setAuditLogs(mockAuditLogs);
      setLoading(false);
    }, 1000);
  }, [isAdmin, navigate]);

  const handleConfigChange = async (key: keyof SystemConfig, value: any) => {
    if (!systemConfig) return;
    
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const updatedConfig = { ...systemConfig, [key]: value };
      setSystemConfig(updatedConfig);
      message.success(t('admin.config_updated'));
    } catch (error) {
      message.error(t('admin.config_update_failed'));
    } finally {
      setSaving(false);
    }
  };

  const handleUserStatusChange = async (userId: number, status: string) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, status: status as any } : u));
      message.success(t('admin.user_status_updated'));
    } catch (error) {
      message.error(t('admin.user_status_update_failed'));
    }
  };

  const handleUserRoleChange = async (userId: number, role: string) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: role as any } : u));
      message.success(t('admin.user_role_updated'));
    } catch (error) {
      message.error(t('admin.user_role_update_failed'));
    }
  };

  const openUserModal = (user: User | null) => {
    setEditingUser(user);
    if (user) {
      form.setFieldsValue(user);
    } else {
      form.resetFields();
    }
    setUserModalVisible(true);
  };

  const handleUserSave = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingUser) {
        // Update existing user
        setUsers(prev => prev.map(u => u.id === editingUser.id ? { ...u, ...values } : u));
        message.success(t('admin.user_updated'));
      } else {
        // Create new user
        const newUser: User = {
          id: Date.now(),
          ...values,
          createdAt: new Date().toISOString(),
          lastLogin: '',
          loginCount: 0
        };
        setUsers(prev => [...prev, newUser]);
        message.success(t('admin.user_created'));
      }
      
      setUserModalVisible(false);
      setEditingUser(null);
      form.resetFields();
    } catch (error) {
      message.error(t('admin.user_save_failed'));
    }
  };

  const userColumns = [
    {
      title: t('admin.users.username'),
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: User) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <Text strong>{username}</Text>
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
      render: (role: string) => (
        <Select
          value={role}
          onChange={(value) => handleUserRoleChange(1, value)}
          style={{ width: 120 }}
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
      render: (status: string) => (
        <Select
          value={status}
          onChange={(value) => handleUserStatusChange(1, value)}
          style={{ width: 120 }}
        >
          <Option value="active">{t('admin.status.active')}</Option>
          <Option value="inactive">{t('admin.status.inactive')}</Option>
          <Option value="suspended">{t('admin.status.suspended')}</Option>
        </Select>
      ),
    },
    {
      title: t('admin.users.last_login'),
      dataIndex: 'lastLogin',
      key: 'lastLogin',
      render: (timestamp: string) => timestamp ? new Date(timestamp).toLocaleString() : '-',
    },
    {
      title: t('admin.users.actions'),
      key: 'actions',
      render: (_, record: User) => (
        <Space>
          <Tooltip title={t('admin.actions.edit')}>
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => openUserModal(record)}
            />
          </Tooltip>
          <Tooltip title={t('admin.actions.view')}>
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
            />
          </Tooltip>
          <Popconfirm
            title={t('admin.delete_user_confirm')}
            onConfirm={() => {
              setUsers(prev => prev.filter(u => u.id !== record.id));
              message.success(t('admin.user_deleted'));
            }}
            okText={t('common.yes')}
            cancelText={t('common.no')}
          >
            <Button 
              type="text" 
              danger 
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const auditColumns = [
    {
      title: t('admin.audit.timestamp'),
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => new Date(timestamp).toLocaleString(),
    },
    {
      title: t('admin.audit.user'),
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: t('admin.audit.action'),
      dataIndex: 'action',
      key: 'action',
    },
    {
      title: t('admin.audit.resource'),
      dataIndex: 'resource',
      key: 'resource',
    },
    {
      title: t('admin.audit.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'success' ? 'green' : 'red'}>
          {status === 'success' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
          {t(`admin.audit.status.${status}`)}
        </Tag>
      ),
    },
    {
      title: t('admin.audit.ip'),
      dataIndex: 'ipAddress',
      key: 'ipAddress',
    },
  ];

  if (!isAdmin) {
    return null;
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px 0' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ color: colors.colorTextBase, marginBottom: 8 }}>
          {t('admin.title')}
        </Title>
        <Text type="secondary">
          {t('admin.subtitle')}
        </Text>
      </div>

      <Tabs defaultActiveKey="overview">
        <TabPane 
          tab={
            <Space>
              <DashboardOutlined />
              {t('admin.tabs.overview')}
            </Space>
          } 
          key="overview"
        >
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title={t('admin.stats.total_users')}
                  value={systemStats?.totalUsers}
                  prefix={<UserOutlined style={{ color: colors.colorPrimary }} />}
                  valueStyle={{ color: colors.colorPrimary }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title={t('admin.stats.active_users')}
                  value={systemStats?.activeUsers}
                  prefix={<TeamOutlined style={{ color: colors.colorSecondary }} />}
                  valueStyle={{ color: colors.colorSecondary }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title={t('admin.stats.total_conversations')}
                  value={systemStats?.totalConversations}
                  prefix={<BarChartOutlined style={{ color: colors.colorAccent }} />}
                  valueStyle={{ color: colors.colorAccent }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title={t('admin.stats.system_uptime')}
                  value={systemStats?.systemUptime}
                  suffix="%"
                  prefix={<CheckCircleOutlined style={{ color: colors.colorPrimary }} />}
                  valueStyle={{ color: colors.colorPrimary }}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title={t('admin.system_performance')}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text>CPU Usage</Text>
                    <Progress 
                      percent={systemStats?.cpuUsage || 0} 
                      status={systemStats?.cpuUsage && systemStats.cpuUsage > 80 ? 'exception' : 'active'}
                    />
                  </div>
                  <div>
                    <Text>Memory Usage</Text>
                    <Progress 
                      percent={systemStats?.memoryUsage || 0} 
                      status={systemStats?.memoryUsage && systemStats.memoryUsage > 80 ? 'exception' : 'active'}
                    />
                  </div>
                  <div>
                    <Text>Disk Usage</Text>
                    <Progress 
                      percent={systemStats?.diskUsage || 0} 
                      status={systemStats?.diskUsage && systemStats.diskUsage > 80 ? 'exception' : 'active'}
                    />
                  </div>
                </Space>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title={t('admin.system_config')}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>{t('admin.config.maintenance_mode')}</Text>
                    <Switch 
                      checked={systemConfig?.maintenanceMode} 
                      onChange={(checked) => handleConfigChange('maintenanceMode', checked)}
                      loading={saving}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>{t('admin.config.debug_mode')}</Text>
                    <Switch 
                      checked={systemConfig?.debugMode} 
                      onChange={(checked) => handleConfigChange('debugMode', checked)}
                      loading={saving}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>{t('admin.config.enable_registration')}</Text>
                    <Switch 
                      checked={systemConfig?.enableRegistration} 
                      onChange={(checked) => handleConfigChange('enableRegistration', checked)}
                      loading={saving}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>{t('admin.config.default_language')}</Text>
                    <Select
                      value={systemConfig?.defaultLanguage}
                      onChange={(value) => handleConfigChange('defaultLanguage', value)}
                      style={{ width: 120 }}
                      loading={saving}
                    >
                      <Option value="de">Deutsch</Option>
                      <Option value="en">English</Option>
                    </Select>
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane 
          tab={
            <Space>
              <TeamOutlined />
              {t('admin.tabs.user_management')}
            </Space>
          } 
          key="users"
        >
          <Card>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={4} style={{ margin: 0 }}>{t('admin.user_management')}</Title>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={() => openUserModal(null)}
              >
                {t('admin.add_user')}
              </Button>
            </div>
            <Table 
              dataSource={users} 
              columns={userColumns} 
              rowKey="id" 
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <Space>
              <SecurityScanOutlined />
              {t('admin.tabs.audit_log')}
            </Space>
          } 
          key="audit"
        >
          <Card>
            <Table 
              dataSource={auditLogs} 
              columns={auditColumns} 
              rowKey="id" 
              pagination={{ pageSize: 10 }}
              scroll={{ x: 800 }}
            />
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <Space>
              <SettingOutlined />
              {t('admin.tabs.system_status')}
            </Space>
          } 
          key="status"
        >
          <Card>
            <div style={{ marginBottom: 16 }}>
              <Button 
                type="primary" 
                icon={<ReloadOutlined />} 
                onClick={() => navigate('/admin/system-status')}
              >
                {t('admin.view_detailed_status')}
              </Button>
            </div>
            <Alert
              message={t('admin.system_operational')}
              description={t('admin.system_operational_description')}
              type="success"
              showIcon
            />
          </Card>
        </TabPane>
      </Tabs>

      <Modal
        open={userModalVisible}
        title={editingUser ? t('admin.edit_user') : t('admin.add_user')}
        onCancel={() => {
          setUserModalVisible(false);
          setEditingUser(null);
          form.resetFields();
        }}
        onOk={handleUserSave}
        okText={editingUser ? t('common.update') : t('common.add')}
        cancelText={t('common.cancel')}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="username" 
                label={t('admin.users.username')} 
                rules={[{ required: true, message: t('admin.users.username_required') }]}
              >
                <Input placeholder={t('admin.users.username_placeholder')} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                name="email" 
                label={t('admin.users.email')} 
                rules={[
                  { required: true, message: t('admin.users.email_required') },
                  { type: 'email', message: t('admin.users.email_invalid') }
                ]}
              >
                <Input placeholder={t('admin.users.email_placeholder')} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="role" label={t('admin.users.role')} rules={[{ required: true }]}>
                <Select placeholder={t('admin.users.role_placeholder')}>
                  <Option value="user">{t('admin.roles.user')}</Option>
                  <Option value="moderator">{t('admin.roles.moderator')}</Option>
                  <Option value="admin">{t('admin.roles.admin')}</Option>
                  <Option value="super_admin">{t('admin.roles.super_admin')}</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="status" label={t('admin.users.status')} rules={[{ required: true }]}>
                <Select placeholder={t('admin.users.status_placeholder')}>
                  <Option value="active">{t('admin.status.active')}</Option>
                  <Option value="inactive">{t('admin.status.inactive')}</Option>
                  <Option value="suspended">{t('admin.status.suspended')}</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          {!editingUser && (
            <Form.Item 
              name="password" 
              label={t('admin.users.password')} 
              rules={[{ required: true, message: t('admin.users.password_required') }]}
            >
              <Input.Password placeholder={t('admin.users.password_placeholder')} />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default Admin; 