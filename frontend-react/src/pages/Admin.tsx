import React, { useEffect, useState } from 'react';
import { 
  Typography, 
  Space, 
  Divider, 
  Row, 
  Col, 
  Statistic, 
  Progress, 
  Switch, 
  Select, 
  Button, 
  message, 
  Spin, 
  Avatar,
  Tooltip,
  Popconfirm,
  Badge,
  Tabs,
  Alert,
  Modal,
  Form,
  Input,
  DatePicker,
  Descriptions,
  List,
  Timeline,
  Tag,
  Table
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
  LineChartOutlined,
  CrownOutlined,
  MonitorOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  MessageOutlined,
  ToolOutlined,
  ShieldOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import ModernCard from '../components/ModernCard';
import ModernButton from '../components/ModernButton';
import ModernInput from '../components/ModernInput';
import ModernSelect from '../components/ModernSelect';
import ModernForm, { ModernFormItem } from '../components/ModernForm';

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
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [systemConfig, setSystemConfig] = useState<SystemConfig | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }

    loadAdminData();
  }, [isAdmin, navigate]);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      // Simulate loading admin data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSystemStats({
        totalUsers: 156,
        activeUsers: 89,
        totalConversations: 1247,
        totalMessages: 28473,
        totalDocuments: 456,
        systemUptime: 99.8,
        cpuUsage: 23,
        memoryUsage: 67,
        diskUsage: 45
      });

      setSystemConfig({
        defaultLanguage: 'de',
        maxFileSize: 10,
        maxUsers: 1000,
        enableRegistration: true,
        enableEmailVerification: true,
        maintenanceMode: false,
        debugMode: false
      });

      setUsers([
        {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          role: 'super_admin',
          status: 'active',
          createdAt: '2024-01-01T00:00:00Z',
          lastLogin: '2024-01-15T10:30:00Z',
          loginCount: 156
        },
        {
          id: 2,
          username: 'moderator1',
          email: 'mod1@example.com',
          role: 'moderator',
          status: 'active',
          createdAt: '2024-01-05T00:00:00Z',
          lastLogin: '2024-01-15T09:15:00Z',
          loginCount: 89
        }
      ]);

      setAuditLogs([
        {
          id: '1',
          userId: 1,
          username: 'admin',
          action: 'LOGIN',
          resource: 'AUTH',
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
          resource: 'USER',
          details: 'Updated user profile',
          ipAddress: '192.168.1.101',
          timestamp: '2024-01-15T09:15:00Z',
          status: 'success'
        }
      ]);
    } catch (error) {
      message.error(t('admin.load_failed', 'Fehler beim Laden der Admin-Daten'));
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = async (key: keyof SystemConfig, value: any) => {
    setSaving(true);
    try {
      setSystemConfig(prev => prev ? { ...prev, [key]: value } : null);
      message.success(t('admin.config_updated', 'Konfiguration aktualisiert'));
    } catch (error) {
      message.error(t('admin.config_update_failed', 'Fehler beim Aktualisieren der Konfiguration'));
    } finally {
      setSaving(false);
    }
  };

  const handleUserStatusChange = async (userId: number, status: string) => {
    try {
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, status: status as any } : u));
      message.success(t('admin.user_status_updated', 'Benutzerstatus aktualisiert'));
    } catch (error) {
      message.error(t('admin.user_status_update_failed', 'Fehler beim Aktualisieren des Benutzerstatus'));
    }
  };

  const handleUserRoleChange = async (userId: number, role: string) => {
    try {
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: role as any } : u));
      message.success(t('admin.user_role_updated', 'Benutzerrolle aktualisiert'));
    } catch (error) {
      message.error(t('admin.user_role_update_failed', 'Fehler beim Aktualisieren der Benutzerrolle'));
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
        setUsers(prev => prev.map(u => u.id === editingUser.id ? { ...u, ...values } : u));
        message.success(t('admin.user_updated', 'Benutzer aktualisiert'));
      } else {
        const newUser: User = {
          id: Date.now(),
          ...values,
          createdAt: new Date().toISOString(),
          lastLogin: '',
          loginCount: 0
        };
        setUsers(prev => [...prev, newUser]);
        message.success(t('admin.user_created', 'Benutzer erstellt'));
      }
      
      setUserModalVisible(false);
      setEditingUser(null);
      form.resetFields();
    } catch (error) {
      message.error(t('admin.user_save_failed', 'Fehler beim Speichern des Benutzers'));
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'super_admin':
        return <CrownOutlined style={{ color: '#FFD700' }} />;
      case 'admin':
        return <CrownOutlined style={{ color: '#FF6B6B' }} />;
      case 'moderator':
        return <ShieldOutlined style={{ color: '#4ECDC4' }} />;
      default:
        return <UserOutlined style={{ color: colors.colorPrimary }} />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin':
        return '#FFD700';
      case 'admin':
        return '#FF6B6B';
      case 'moderator':
        return '#4ECDC4';
      default:
        return colors.colorPrimary;
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
        return 'blue';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const userColumns = [
    {
      title: t('admin.users.username', 'Benutzername'),
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: User) => (
        <Space>
          <Avatar 
            icon={getRoleIcon(record.role)}
            style={{ backgroundColor: getRoleColor(record.role) }}
          />
          <div>
            <Text strong>{username}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {record.email}
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: t('admin.users.role', 'Rolle'),
      dataIndex: 'role',
      key: 'role',
      render: (role: string, record: User) => (
        <ModernSelect
          value={role}
          onChange={(value) => handleUserRoleChange(record.id, value)}
          style={{ width: 140 }}
        >
          <ModernSelect.Option value="user">{t('admin.roles.user', 'Benutzer')}</ModernSelect.Option>
          <ModernSelect.Option value="moderator">{t('admin.roles.moderator', 'Moderator')}</ModernSelect.Option>
          <ModernSelect.Option value="admin">{t('admin.roles.admin', 'Administrator')}</ModernSelect.Option>
          <ModernSelect.Option value="super_admin">{t('admin.roles.super_admin', 'Super Admin')}</ModernSelect.Option>
        </ModernSelect>
      ),
    },
    {
      title: t('admin.users.status', 'Status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string, record: User) => (
        <ModernSelect
          value={status}
          onChange={(value) => handleUserStatusChange(record.id, value)}
          style={{ width: 120 }}
        >
          <ModernSelect.Option value="active">{t('admin.status.active', 'Aktiv')}</ModernSelect.Option>
          <ModernSelect.Option value="inactive">{t('admin.status.inactive', 'Inaktiv')}</ModernSelect.Option>
          <ModernSelect.Option value="suspended">{t('admin.status.suspended', 'Gesperrt')}</ModernSelect.Option>
        </ModernSelect>
      ),
    },
    {
      title: t('admin.users.last_login', 'Letzter Login'),
      dataIndex: 'lastLogin',
      key: 'lastLogin',
      render: (timestamp: string) => (
        <div>
          <Text>{timestamp ? formatDate(timestamp) : '-'}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {timestamp ? t('admin.users.login_count', '{{count}} Logins', { count: 0 }) : ''}
          </Text>
        </div>
      ),
    },
    {
      title: t('admin.users.actions', 'Aktionen'),
      key: 'actions',
      render: (_, record: User) => (
        <Space>
          <Tooltip title={t('admin.actions.edit', 'Bearbeiten')}>
            <ModernButton
              variant="secondary"
              size="sm"
              icon={<EditOutlined />}
              onClick={() => openUserModal(record)}
            />
          </Tooltip>
          <Tooltip title={t('admin.actions.view', 'Anzeigen')}>
            <ModernButton
              variant="secondary"
              size="sm"
              icon={<EyeOutlined />}
            />
          </Tooltip>
          <Popconfirm
            title={t('admin.delete_user_confirm', 'Benutzer wirklich löschen?')}
            onConfirm={() => {
              setUsers(prev => prev.filter(u => u.id !== record.id));
              message.success(t('admin.user_deleted', 'Benutzer gelöscht'));
            }}
            okText={t('common.yes', 'Ja')}
            cancelText={t('common.no', 'Nein')}
          >
            <ModernButton
              variant="secondary"
              size="sm"
              icon={<DeleteOutlined />}
              danger
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const auditColumns = [
    {
      title: t('admin.audit.timestamp', 'Zeitstempel'),
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => formatDate(timestamp),
    },
    {
      title: t('admin.audit.user', 'Benutzer'),
      dataIndex: 'username',
      key: 'username',
      render: (username: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <Text>{username}</Text>
        </Space>
      ),
    },
    {
      title: t('admin.audit.action', 'Aktion'),
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => (
        <Tag color="blue" style={{ fontSize: '12px' }}>
          {action}
        </Tag>
      ),
    },
    {
      title: t('admin.audit.resource', 'Ressource'),
      dataIndex: 'resource',
      key: 'resource',
    },
    {
      title: t('admin.audit.status', 'Status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'success' ? 'green' : 'red'} style={{ fontSize: '12px' }}>
          {status === 'success' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
          {t(`admin.audit.status.${status}`, status)}
        </Tag>
      ),
    },
    {
      title: t('admin.audit.ip', 'IP-Adresse'),
      dataIndex: 'ipAddress',
      key: 'ipAddress',
      render: (ip: string) => (
        <Text type="secondary" style={{ fontSize: '12px' }}>
          {ip}
        </Text>
      ),
    },
  ];

  if (!isAdmin) {
    return null;
  }

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: colors.colorGradientPrimary
      }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh',
      background: colors.colorGradientPrimary,
      padding: '24px'
    }}>
      <div style={{ maxWidth: 1400, margin: '0 auto' }}>
        {/* Header Section */}
        <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: 'center', padding: '32px 0' }}>
            <div style={{ 
              width: 80, 
              height: 80, 
              borderRadius: '50%',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 24px',
              fontSize: '32px'
            }}>
              👑
            </div>
            <Title level={1} style={{ color: '#FFFFFF', marginBottom: 8, fontSize: '2.5rem' }}>
              {t('admin.title', 'Administration')}
            </Title>
            <Text style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.9)' }}>
              {t('admin.subtitle', 'Systemverwaltung und Benutzeradministration')}
            </Text>
          </div>
        </ModernCard>

        <div style={{ marginTop: 32 }}>
          <Tabs 
            defaultActiveKey="overview"
            type="card"
            size="large"
            style={{ 
              backgroundColor: colors.colorBgContainer,
              borderRadius: '16px',
              padding: '24px'
            }}
          >
            <TabPane 
              tab={
                <Space>
                  <DashboardOutlined />
                  {t('admin.tabs.overview', 'Übersicht')}
                </Space>
              } 
              key="overview"
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                
                {/* Statistics Cards */}
                <div className="modern-card-grid" style={{ marginBottom: 24 }}>
                  <ModernCard variant="elevated" size="md" className="stagger-children">
                    <Statistic
                      title={t('admin.stats.total_users', 'Gesamtbenutzer')}
                      value={systemStats?.totalUsers}
                      prefix={<UserOutlined style={{ color: colors.colorPrimary }} />}
                      valueStyle={{ color: colors.colorPrimary, fontSize: '2rem' }}
                    />
                  </ModernCard>
                  
                  <ModernCard variant="elevated" size="md" className="stagger-children">
                    <Statistic
                      title={t('admin.stats.active_users', 'Aktive Benutzer')}
                      value={systemStats?.activeUsers}
                      prefix={<TeamOutlined style={{ color: colors.colorSecondary }} />}
                      valueStyle={{ color: colors.colorSecondary, fontSize: '2rem' }}
                    />
                  </ModernCard>
                  
                  <ModernCard variant="elevated" size="md" className="stagger-children">
                    <Statistic
                      title={t('admin.stats.total_conversations', 'Gespräche')}
                      value={systemStats?.totalConversations}
                      prefix={<MessageOutlined style={{ color: colors.colorAccent }} />}
                      valueStyle={{ color: colors.colorAccent, fontSize: '2rem' }}
                    />
                  </ModernCard>
                  
                  <ModernCard variant="elevated" size="md" className="stagger-children">
                    <Statistic
                      title={t('admin.stats.system_uptime', 'Uptime')}
                      value={systemStats?.systemUptime}
                      suffix="%"
                      prefix={<CheckCircleOutlined style={{ color: '#52C41A' }} />}
                      valueStyle={{ color: '#52C41A', fontSize: '2rem' }}
                    />
                  </ModernCard>
                </div>

                <Row gutter={[24, 24]}>
                  {/* System Performance */}
                  <Col xs={24} lg={12}>
                    <ModernCard 
                      variant="elevated" 
                      size="lg"
                      header={
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <MonitorOutlined style={{ color: colors.colorPrimary, fontSize: '20px' }} />
                          <Title level={4} style={{ margin: 0 }}>
                            {t('admin.system_performance', 'Systemleistung')}
                          </Title>
                        </div>
                      }
                    >
                      <Space direction="vertical" style={{ width: '100%' }} size="large">
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <Text strong>CPU Usage</Text>
                            <Text>{systemStats?.cpuUsage}%</Text>
                          </div>
                          <Progress 
                            percent={systemStats?.cpuUsage || 0} 
                            status={systemStats?.cpuUsage && systemStats.cpuUsage > 80 ? 'exception' : 'active'}
                            strokeColor={colors.colorPrimary}
                            strokeWidth={8}
                          />
                        </div>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <Text strong>Memory Usage</Text>
                            <Text>{systemStats?.memoryUsage}%</Text>
                          </div>
                          <Progress 
                            percent={systemStats?.memoryUsage || 0} 
                            status={systemStats?.memoryUsage && systemStats.memoryUsage > 80 ? 'exception' : 'active'}
                            strokeColor={colors.colorSecondary}
                            strokeWidth={8}
                          />
                        </div>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <Text strong>Disk Usage</Text>
                            <Text>{systemStats?.diskUsage}%</Text>
                          </div>
                          <Progress 
                            percent={systemStats?.diskUsage || 0} 
                            status={systemStats?.diskUsage && systemStats.diskUsage > 80 ? 'exception' : 'active'}
                            strokeColor={colors.colorAccent}
                            strokeWidth={8}
                          />
                        </div>
                      </Space>
                    </ModernCard>
                  </Col>

                  {/* System Configuration */}
                  <Col xs={24} lg={12}>
                    <ModernCard 
                      variant="elevated" 
                      size="lg"
                      header={
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <SettingOutlined style={{ color: colors.colorSecondary, fontSize: '20px' }} />
                          <Title level={4} style={{ margin: 0 }}>
                            {t('admin.system_config', 'Systemkonfiguration')}
                          </Title>
                        </div>
                      }
                    >
                      <Space direction="vertical" style={{ width: '100%' }} size="large">
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          padding: '16px',
                          backgroundColor: colors.colorBgContainer,
                          borderRadius: '12px',
                          border: `1px solid ${colors.colorBorder}`
                        }}>
                          <div>
                            <Text strong style={{ fontSize: '16px' }}>
                              {t('admin.config.maintenance_mode', 'Wartungsmodus')}
                            </Text>
                            <br />
                            <Text type="secondary">
                              {t('admin.config.maintenance_mode_desc', 'System für Wartung sperren')}
                            </Text>
                          </div>
                          <Switch 
                            checked={systemConfig?.maintenanceMode} 
                            onChange={(checked) => handleConfigChange('maintenanceMode', checked)}
                            loading={saving}
                          />
                        </div>

                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          padding: '16px',
                          backgroundColor: colors.colorBgContainer,
                          borderRadius: '12px',
                          border: `1px solid ${colors.colorBorder}`
                        }}>
                          <div>
                            <Text strong style={{ fontSize: '16px' }}>
                              {t('admin.config.debug_mode', 'Debug-Modus')}
                            </Text>
                            <br />
                            <Text type="secondary">
                              {t('admin.config.debug_mode_desc', 'Erweiterte Logging aktivieren')}
                            </Text>
                          </div>
                          <Switch 
                            checked={systemConfig?.debugMode} 
                            onChange={(checked) => handleConfigChange('debugMode', checked)}
                            loading={saving}
                          />
                        </div>

                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          padding: '16px',
                          backgroundColor: colors.colorBgContainer,
                          borderRadius: '12px',
                          border: `1px solid ${colors.colorBorder}`
                        }}>
                          <div>
                            <Text strong style={{ fontSize: '16px' }}>
                              {t('admin.config.enable_registration', 'Registrierung')}
                            </Text>
                            <br />
                            <Text type="secondary">
                              {t('admin.config.enable_registration_desc', 'Neue Benutzerregistrierung erlauben')}
                            </Text>
                          </div>
                          <Switch 
                            checked={systemConfig?.enableRegistration} 
                            onChange={(checked) => handleConfigChange('enableRegistration', checked)}
                            loading={saving}
                          />
                        </div>
                      </Space>
                    </ModernCard>
                  </Col>
                </Row>
              </div>
            </TabPane>

            <TabPane 
              tab={
                <Space>
                  <UserOutlined />
                  {t('admin.tabs.users', 'Benutzer')}
                </Space>
              } 
              key="users"
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                
                {/* User Management Header */}
                <ModernCard variant="elevated" size="md">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Title level={3} style={{ margin: 0 }}>
                        {t('admin.user_management', 'Benutzerverwaltung')}
                      </Title>
                      <Text type="secondary">
                        {t('admin.user_management_desc', 'Verwalten Sie Benutzerkonten und Berechtigungen')}
                      </Text>
                    </div>
                    <Space>
                      <ModernButton
                        variant="secondary"
                        size="md"
                        icon={<ExportOutlined />}
                      >
                        {t('admin.export_users', 'Exportieren')}
                      </ModernButton>
                      <ModernButton
                        variant="primary"
                        size="md"
                        icon={<PlusOutlined />}
                        onClick={() => openUserModal(null)}
                      >
                        {t('admin.add_user', 'Benutzer hinzufügen')}
                      </ModernButton>
                    </Space>
                  </div>
                </ModernCard>

                {/* Users Table */}
                <ModernCard variant="elevated" size="lg">
                  <Table
                    dataSource={users}
                    columns={userColumns}
                    rowKey="id"
                    pagination={{
                      pageSize: 10,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total, range) => 
                        t('admin.table.showing', '{{start}}-{{end}} von {{total}} Einträgen', {
                          start: range[0],
                          end: range[1],
                          total
                        })
                    }}
                    scroll={{ x: 1200 }}
                  />
                </ModernCard>
              </div>
            </TabPane>

            <TabPane 
              tab={
                <Space>
                  <SecurityScanOutlined />
                  {t('admin.tabs.audit', 'Audit-Log')}
                </Space>
              } 
              key="audit"
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                
                {/* Audit Log Header */}
                <ModernCard variant="elevated" size="md">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Title level={3} style={{ margin: 0 }}>
                        {t('admin.audit_log', 'Audit-Log')}
                      </Title>
                      <Text type="secondary">
                        {t('admin.audit_log_desc', 'Überwachung aller Systemaktivitäten')}
                      </Text>
                    </div>
                    <Space>
                      <ModernButton
                        variant="secondary"
                        size="md"
                        icon={<ReloadOutlined />}
                        onClick={loadAdminData}
                      >
                        {t('admin.refresh', 'Aktualisieren')}
                      </ModernButton>
                      <ModernButton
                        variant="secondary"
                        size="md"
                        icon={<DownloadOutlined />}
                      >
                        {t('admin.download_log', 'Download')}
                      </ModernButton>
                    </Space>
                  </div>
                </ModernCard>

                {/* Audit Log Table */}
                <ModernCard variant="elevated" size="lg">
                  <Table
                    dataSource={auditLogs}
                    columns={auditColumns}
                    rowKey="id"
                    pagination={{
                      pageSize: 20,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total, range) => 
                        t('admin.table.showing', '{{start}}-{{end}} von {{total}} Einträgen', {
                          start: range[0],
                          end: range[1],
                          total
                        })
                    }}
                    scroll={{ x: 1000 }}
                  />
                </ModernCard>
              </div>
            </TabPane>
          </Tabs>
        </div>

        {/* User Modal */}
        <Modal
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <UserOutlined style={{ color: colors.colorPrimary }} />
              {editingUser ? t('admin.edit_user', 'Benutzer bearbeiten') : t('admin.add_user', 'Benutzer hinzufügen')}
            </div>
          }
          open={userModalVisible}
          onCancel={() => {
            setUserModalVisible(false);
            setEditingUser(null);
            form.resetFields();
          }}
          footer={null}
          width={600}
          style={{ top: 20 }}
        >
          <ModernForm
            form={form}
            layout="vertical"
            onFinish={handleUserSave}
          >
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <ModernFormItem
                  name="username"
                  label={t('admin.users.username', 'Benutzername')}
                  rules={[{ required: true, message: t('admin.users.username_required', 'Benutzername ist erforderlich') }]}
                >
                  <ModernInput
                    prefix={<UserOutlined style={{ color: colors.colorPrimary }} />}
                    placeholder={t('admin.users.username_placeholder', 'Benutzername eingeben')}
                  />
                </ModernFormItem>
              </Col>
              
              <Col span={12}>
                <ModernFormItem
                  name="email"
                  label={t('admin.users.email', 'E-Mail')}
                  rules={[
                    { required: true, message: t('admin.users.email_required', 'E-Mail ist erforderlich') },
                    { type: 'email', message: t('admin.users.email_invalid', 'Ungültige E-Mail-Adresse') }
                  ]}
                >
                  <ModernInput
                    prefix={<MailOutlined style={{ color: colors.colorSecondary }} />}
                    placeholder={t('admin.users.email_placeholder', 'E-Mail eingeben')}
                  />
                </ModernFormItem>
              </Col>
            </Row>

            <Row gutter={[16, 16]}>
              <Col span={12}>
                <ModernFormItem
                  name="role"
                  label={t('admin.users.role', 'Rolle')}
                  rules={[{ required: true, message: t('admin.users.role_required', 'Rolle ist erforderlich') }]}
                >
                  <ModernSelect
                    placeholder={t('admin.users.role_placeholder', 'Rolle auswählen')}
                  >
                    <ModernSelect.Option value="user">{t('admin.roles.user', 'Benutzer')}</ModernSelect.Option>
                    <ModernSelect.Option value="moderator">{t('admin.roles.moderator', 'Moderator')}</ModernSelect.Option>
                    <ModernSelect.Option value="admin">{t('admin.roles.admin', 'Administrator')}</ModernSelect.Option>
                    <ModernSelect.Option value="super_admin">{t('admin.roles.super_admin', 'Super Admin')}</ModernSelect.Option>
                  </ModernSelect>
                </ModernFormItem>
              </Col>
              
              <Col span={12}>
                <ModernFormItem
                  name="status"
                  label={t('admin.users.status', 'Status')}
                  rules={[{ required: true, message: t('admin.users.status_required', 'Status ist erforderlich') }]}
                >
                  <ModernSelect
                    placeholder={t('admin.users.status_placeholder', 'Status auswählen')}
                  >
                    <ModernSelect.Option value="active">{t('admin.status.active', 'Aktiv')}</ModernSelect.Option>
                    <ModernSelect.Option value="inactive">{t('admin.status.inactive', 'Inaktiv')}</ModernSelect.Option>
                    <ModernSelect.Option value="suspended">{t('admin.status.suspended', 'Gesperrt')}</ModernSelect.Option>
                  </ModernSelect>
                </ModernFormItem>
              </Col>
            </Row>

            <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
              <ModernButton
                variant="primary"
                size="lg"
                htmlType="submit"
                style={{ flex: 1 }}
              >
                {editingUser ? t('admin.save', 'Speichern') : t('admin.create', 'Erstellen')}
              </ModernButton>
              
              <ModernButton
                variant="outlined"
                size="lg"
                onClick={() => {
                  setUserModalVisible(false);
                  setEditingUser(null);
                  form.resetFields();
                }}
                style={{ flex: 1 }}
              >
                {t('admin.cancel', 'Abbrechen')}
              </ModernButton>
            </div>
          </ModernForm>
        </Modal>
      </div>
    </div>
  );
};

export default Admin; 