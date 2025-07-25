import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, List, Avatar, Progress, Tag, Space, Typography, Divider } from 'antd';
import { 
  MessageOutlined, 
  BookOutlined, 
  TeamOutlined, 
  ToolOutlined,
  UserOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  TrendingUpOutlined,
  RobotOutlined,
  ApiOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';

const { Title, Text } = Typography;

interface DashboardStats {
  totalConversations: number;
  totalMessages: number;
  totalDocuments: number;
  totalAssistants: number;
  totalTools: number;
  activeUsers: number;
  systemHealth: 'healthy' | 'warning' | 'error';
  recentActivity: Array<{
    id: string;
    type: 'conversation' | 'document' | 'assistant' | 'tool';
    title: string;
    timestamp: string;
    user: string;
  }>;
}

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');

  const [stats, setStats] = useState<DashboardStats>({
    totalConversations: 0,
    totalMessages: 0,
    totalDocuments: 0,
    totalAssistants: 0,
    totalTools: 0,
    activeUsers: 0,
    systemHealth: 'healthy',
    recentActivity: []
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      setLoading(true);
      try {
        // TODO: Replace with actual API calls
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setStats({
          totalConversations: 156,
          totalMessages: 2847,
          totalDocuments: 89,
          totalAssistants: 12,
          totalTools: 8,
          activeUsers: 23,
          systemHealth: 'healthy',
          recentActivity: [
            {
              id: '1',
              type: 'conversation',
              title: 'Neue Konversation gestartet',
              timestamp: '2024-01-15T10:30:00Z',
              user: 'Max Mustermann'
            },
            {
              id: '2',
              type: 'document',
              title: 'Dokument hochgeladen: Projektplan.pdf',
              timestamp: '2024-01-15T09:15:00Z',
              user: 'Anna Schmidt'
            },
            {
              id: '3',
              type: 'assistant',
              title: 'Assistent "Support Bot" erstellt',
              timestamp: '2024-01-15T08:45:00Z',
              user: 'Admin'
            },
            {
              id: '4',
              type: 'tool',
              title: 'MCP Tool "Weather API" hinzugefügt',
              timestamp: '2024-01-15T08:30:00Z',
              user: 'Admin'
            }
          ]
        });
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'conversation': return <MessageOutlined style={{ color: colors.colorPrimary }} />;
      case 'document': return <FileTextOutlined style={{ color: colors.colorSecondary }} />;
      case 'assistant': return <RobotOutlined style={{ color: colors.colorAccent }} />;
      case 'tool': return <ApiOutlined style={{ color: colors.colorPrimary }} />;
      default: return <ClockCircleOutlined />;
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const quickActions = [
    {
      title: t('dashboard.quick_actions.start_chat'),
      icon: <MessageOutlined />,
      action: () => navigate('/chat'),
      color: colors.colorPrimary
    },
    {
      title: t('dashboard.quick_actions.upload_document'),
      icon: <FileTextOutlined />,
      action: () => navigate('/knowledge-base'),
      color: colors.colorSecondary
    },
    {
      title: t('dashboard.quick_actions.manage_assistants'),
      icon: <RobotOutlined />,
      action: () => navigate('/assistants'),
      color: colors.colorAccent
    },
    {
      title: t('dashboard.quick_actions.view_tools'),
      icon: <ToolOutlined />,
      action: () => navigate('/tools'),
      color: colors.colorPrimary
    }
  ];

  return (
    <div style={{ padding: '24px 0' }}>
      {/* Welcome Section */}
      <div style={{ marginBottom: 32 }}>
        <Title level={2} style={{ color: colors.colorTextBase, marginBottom: 8 }}>
          {t('dashboard.welcome', { username: user?.username || t('common.user') })}
        </Title>
        <Text type="secondary" style={{ fontSize: '16px' }}>
          {t('dashboard.subtitle')}
        </Text>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title={t('dashboard.stats.conversations')}
              value={stats.totalConversations}
              prefix={<MessageOutlined style={{ color: colors.colorPrimary }} />}
              valueStyle={{ color: colors.colorPrimary }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title={t('dashboard.stats.messages')}
              value={stats.totalMessages}
              prefix={<MessageOutlined style={{ color: colors.colorSecondary }} />}
              valueStyle={{ color: colors.colorSecondary }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title={t('dashboard.stats.documents')}
              value={stats.totalDocuments}
              prefix={<BookOutlined style={{ color: colors.colorAccent }} />}
              valueStyle={{ color: colors.colorAccent }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title={t('dashboard.stats.assistants')}
              value={stats.totalAssistants}
              prefix={<TeamOutlined style={{ color: colors.colorPrimary }} />}
              valueStyle={{ color: colors.colorPrimary }}
            />
          </Card>
        </Col>
      </Row>

      {/* System Health and Quick Actions */}
      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        <Col xs={24} lg={16}>
          <Card 
            title={t('dashboard.system_health')}
            extra={
              <Tag color={getHealthColor(stats.systemHealth)}>
                {t(`dashboard.health.${stats.systemHealth}`)}
              </Tag>
            }
          >
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title={t('dashboard.stats.active_users')}
                  value={stats.activeUsers}
                  prefix={<UserOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title={t('dashboard.stats.tools')}
                  value={stats.totalTools}
                  prefix={<ToolOutlined />}
                />
              </Col>
            </Row>
            <Divider />
            <div>
              <Text strong>{t('dashboard.performance')}</Text>
              <Progress 
                percent={85} 
                status="active" 
                strokeColor={colors.colorPrimary}
                style={{ marginTop: 8 }}
              />
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title={t('dashboard.quick_actions.title')}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  type="text"
                  icon={action.icon}
                  onClick={action.action}
                  style={{ 
                    width: '100%', 
                    textAlign: 'left',
                    color: action.color,
                    border: `1px solid ${colors.colorBorder}`,
                    marginBottom: 8
                  }}
                >
                  {action.title}
                </Button>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Recent Activity */}
      <Card title={t('dashboard.recent_activity')}>
        <List
          loading={loading}
          dataSource={stats.recentActivity}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <Avatar 
                    icon={getActivityIcon(item.type)}
                    style={{ backgroundColor: colors.colorBgContainer }}
                  />
                }
                title={
                  <Space>
                    <Text strong>{item.title}</Text>
                    <Tag size="small" color="blue">{item.user}</Tag>
                  </Space>
                }
                description={
                  <Space>
                    <ClockCircleOutlined />
                    <Text type="secondary">
                      {new Date(item.timestamp).toLocaleString()}
                    </Text>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      {/* Admin Section */}
      {isAdmin && (
        <Card 
          title={t('dashboard.admin_section')}
          style={{ marginTop: 16 }}
          extra={
            <Button type="primary" onClick={() => navigate('/admin')}>
              {t('dashboard.admin_dashboard')}
            </Button>
          }
        >
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title={t('dashboard.admin.total_users')}
                value={156}
                prefix={<UserOutlined />}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title={t('dashboard.admin.system_load')}
                value={23}
                suffix="%"
                prefix={<TrendingUpOutlined />}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title={t('dashboard.admin.uptime')}
                value={99.9}
                suffix="%"
                precision={1}
                prefix={<ClockCircleOutlined />}
              />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
};

export default Dashboard; 