import React from 'react';
import { Row, Col, Card, Typography, Space, Tag, List, Avatar, Progress, Table } from 'antd';
import { 
  UserOutlined, 
  MessageOutlined, 
  ClockCircleOutlined, 
  SmileOutlined,
  CalendarOutlined,
  TrophyOutlined,
  FireOutlined 
} from '@ant-design/icons';
import { Line, Heatmap } from '@ant-design/plots';
import { useTranslation } from 'react-i18next';
import type { UserBehaviorMetrics } from '../../services/conversationIntelligence';
import ModernCard from '../ModernCard';

const { Title, Text } = Typography;

interface UserBehaviorAnalysisProps {
  data: UserBehaviorMetrics[];
  loading?: boolean;
}

const UserBehaviorAnalysis: React.FC<UserBehaviorAnalysisProps> = ({ 
  data, 
  loading = false 
}) => {
  const { t } = useTranslation();

  if (!data || data.length === 0) {
    return (
      <ModernCard>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Text type="secondary">{t('intelligence.no_user_behavior_data')}</Text>
        </div>
      </ModernCard>
    );
  }

  // Prepare data for activity heatmap
  const heatmapData = data.flatMap(user => 
    user.activeHours.map((activity, hour) => ({
      user: user.username,
      hour: hour,
      activity: activity,
    }))
  );

  // Prepare data for satisfaction trend
  const satisfactionData = data.map(user => ({
    user: user.username,
    satisfaction: user.satisfactionScore,
    conversations: user.totalConversations,
  }));

  // Sort users by engagement
  const sortedUsers = [...data].sort((a, b) => b.totalConversations - a.totalConversations);

  // Table columns for user behavior
  const columns = [
    {
      title: t('intelligence.user'),
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: UserBehaviorMetrics) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <Text strong>{username}</Text>
        </Space>
      ),
    },
    {
      title: t('intelligence.conversations'),
      dataIndex: 'totalConversations',
      key: 'totalConversations',
      sorter: (a: UserBehaviorMetrics, b: UserBehaviorMetrics) => a.totalConversations - b.totalConversations,
      render: (value: number) => (
        <Tag color="blue" icon={<MessageOutlined />}>
          {value}
        </Tag>
      ),
    },
    {
      title: t('intelligence.avg_messages'),
      dataIndex: 'avgMessagesPerConversation',
      key: 'avgMessagesPerConversation',
      render: (value: number) => value.toFixed(1),
    },
    {
      title: t('intelligence.avg_response_time'),
      dataIndex: 'avgResponseTime',
      key: 'avgResponseTime',
      render: (value: number) => (
        <Space>
          <ClockCircleOutlined />
          <Text>{value.toFixed(1)}s</Text>
        </Space>
      ),
    },
    {
      title: t('intelligence.satisfaction'),
      dataIndex: 'satisfactionScore',
      key: 'satisfactionScore',
      sorter: (a: UserBehaviorMetrics, b: UserBehaviorMetrics) => a.satisfactionScore - b.satisfactionScore,
      render: (value: number) => (
        <Space direction="vertical" size="small">
          <Text strong>{value.toFixed(1)}/5</Text>
          <Progress
            percent={value * 20}
            size="small"
            status={value >= 4 ? 'success' : value >= 3 ? 'normal' : 'exception'}
            showInfo={false}
          />
        </Space>
      ),
    },
    {
      title: t('intelligence.top_topics'),
      dataIndex: 'preferredTopics',
      key: 'preferredTopics',
      render: (topics: string[]) => (
        <Space wrap>
          {topics.slice(0, 3).map((topic, idx) => (
            <Tag key={idx} size="small">
              {topic}
            </Tag>
          ))}
          {topics.length > 3 && (
            <Tag size="small">+{topics.length - 3}</Tag>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* User Behavior Overview */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>{t('intelligence.total_users')}</Title>
              <Text strong style={{ fontSize: '24px' }}>
                {data.length}
              </Text>
            </div>
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>{t('intelligence.avg_conversations')}</Title>
              <Text strong style={{ fontSize: '24px' }}>
                {(data.reduce((sum, user) => sum + user.totalConversations, 0) / data.length).toFixed(1)}
              </Text>
            </div>
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>{t('intelligence.avg_satisfaction')}</Title>
              <Text strong style={{ fontSize: '24px' }}>
                {(data.reduce((sum, user) => sum + user.satisfactionScore, 0) / data.length).toFixed(1)}
              </Text>
            </div>
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>{t('intelligence.avg_response_time')}</Title>
              <Text strong style={{ fontSize: '24px' }}>
                {(data.reduce((sum, user) => sum + user.avgResponseTime, 0) / data.length).toFixed(1)}s
              </Text>
            </div>
          </ModernCard>
        </Col>
      </Row>

      {/* User Activity Heatmap */}
      <ModernCard title={t('intelligence.user_activity_heatmap')}>
        <Heatmap
          data={heatmapData}
          xField="hour"
          yField="user"
          colorField="activity"
          color={['#f0f0f0', '#1890ff']}
          xAxis={{
            title: {
              text: t('intelligence.hour_of_day'),
            },
            tickCount: 24,
          }}
          yAxis={{
            title: {
              text: t('intelligence.users'),
            },
          }}
          tooltip={{
            formatter: (datum) => {
              return {
                name: `${datum.user} - ${datum.hour}:00`,
                value: `${t('intelligence.activity_level')}: ${datum.activity}`,
              };
            },
          }}
        />
      </ModernCard>

      {/* Satisfaction vs Conversations Chart */}
      <ModernCard title={t('intelligence.satisfaction_vs_engagement')}>
        <Line
          data={satisfactionData}
          xField="conversations"
          yField="satisfaction"
          seriesField="user"
          point={{
            size: 4,
            shape: 'circle',
          }}
          smooth
          color="#1890ff"
          xAxis={{
            title: {
              text: t('intelligence.total_conversations'),
            },
          }}
          yAxis={{
            title: {
              text: t('intelligence.satisfaction_score'),
            },
            min: 0,
            max: 5,
          }}
          tooltip={{
            formatter: (datum) => {
              return {
                name: datum.user,
                value: `${t('intelligence.satisfaction')}: ${datum.satisfaction.toFixed(1)}, ${t('intelligence.conversations')}: ${datum.conversations}`,
              };
            },
          }}
        />
      </ModernCard>

      {/* Top Users by Engagement */}
      <ModernCard title={t('intelligence.top_users_by_engagement')}>
        <Row gutter={[16, 16]}>
          {sortedUsers.slice(0, 6).map((user, index) => (
            <Col xs={24} sm={12} lg={8} key={user.userId}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <Avatar 
                    size={48} 
                    icon={<UserOutlined />} 
                    style={{ 
                      backgroundColor: index < 3 ? '#ff4d4f' : '#1890ff',
                      marginBottom: 8
                    }} 
                  />
                  <Title level={5} style={{ marginTop: 8 }}>
                    {user.username}
                  </Title>
                  <Space direction="vertical" size="small">
                    <Tag color="blue" icon={<MessageOutlined />}>
                      {user.totalConversations} {t('intelligence.conversations')}
                    </Tag>
                    <Tag color="green" icon={<SmileOutlined />}>
                      {user.satisfactionScore.toFixed(1)}/5
                    </Tag>
                    <Tag color="orange" icon={<ClockCircleOutlined />}>
                      {user.avgResponseTime.toFixed(1)}s
                    </Tag>
                  </Space>
                  <Progress
                    percent={(user.totalConversations / sortedUsers[0].totalConversations) * 100}
                    size="small"
                    showInfo={false}
                    strokeColor={index < 3 ? '#ff4d4f' : '#1890ff'}
                    style={{ marginTop: 8 }}
                  />
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </ModernCard>

      {/* Detailed User Behavior Table */}
      <ModernCard title={t('intelligence.detailed_user_behavior')}>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="userId"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${t('intelligence.showing')} ${range[0]}-${range[1]} ${t('intelligence.of')} ${total} ${t('intelligence.users')}`,
          }}
          loading={loading}
          scroll={{ x: 800 }}
        />
      </ModernCard>

      {/* Topic Preferences Summary */}
      <ModernCard title={t('intelligence.topic_preferences_summary')}>
        <Row gutter={[16, 16]}>
          {Array.from(new Set(data.flatMap(user => user.preferredTopics)))
            .slice(0, 6)
            .map(topic => {
              const usersWithTopic = data.filter(user => user.preferredTopics.includes(topic));
              return (
                <Col xs={24} sm={12} lg={8} key={topic}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <Title level={5}>{topic}</Title>
                      <Text strong style={{ fontSize: '18px' }}>
                        {usersWithTopic.length}
                      </Text>
                      <div style={{ marginTop: 4 }}>
                        <Text type="secondary">
                          {((usersWithTopic.length / data.length) * 100).toFixed(1)}% {t('intelligence.of_users')}
                        </Text>
                      </div>
                    </div>
                  </Card>
                </Col>
              );
            })}
        </Row>
      </ModernCard>
    </Space>
  );
};

export default UserBehaviorAnalysis;