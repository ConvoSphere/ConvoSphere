import React from 'react';
import { Row, Col, Statistic, Card, Progress, Typography, Space } from 'antd';
import { 
  MessageOutlined, 
  UserOutlined, 
  ClockCircleOutlined, 
  SmileOutlined,
  RiseOutlined 
} from '@ant-design/icons';
import { Line, Bar } from '@ant-design/plots';
import { useTranslation } from 'react-i18next';
import type { ConversationAnalytics } from '../../services/conversationIntelligence';
import ModernCard from '../ModernCard';

const { Title, Text } = Typography;

interface ConversationAnalyticsProps {
  data: ConversationAnalytics | null;
  loading?: boolean;
}

const ConversationAnalytics: React.FC<ConversationAnalyticsProps> = ({ 
  data, 
  loading = false 
}) => {
  const { t } = useTranslation();

  if (!data) {
    return (
      <ModernCard>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Text type="secondary">{t('intelligence.no_data_available')}</Text>
        </div>
      </ModernCard>
    );
  }

  const satisfactionTrendData = data.satisfactionTrend.map(item => ({
    date: item.date,
    score: item.score,
  }));

  const topicData = data.topTopics.map(topic => ({
    topic: topic.name,
    frequency: topic.frequency,
    sentiment: topic.sentiment,
  }));

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* Key Metrics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t('intelligence.total_conversations')}
              value={data.totalConversations}
              prefix={<MessageOutlined />}
              loading={loading}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t('intelligence.total_messages')}
              value={data.totalMessages}
              prefix={<UserOutlined />}
              loading={loading}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t('intelligence.avg_conversation_length')}
              value={data.avgConversationLength}
              prefix={<ClockCircleOutlined />}
              suffix={t('intelligence.messages')}
              loading={loading}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t('intelligence.avg_response_time')}
              value={data.avgResponseTime}
              prefix={<TrendingUpOutlined />}
              suffix={t('intelligence.seconds')}
              loading={loading}
            />
          </ModernCard>
        </Col>
      </Row>

      {/* Satisfaction Trend Chart */}
      <ModernCard title={t('intelligence.satisfaction_trend')}>
        <Line
          data={satisfactionTrendData}
          xField="date"
          yField="score"
          smooth
          point={{
            size: 4,
            shape: 'circle',
          }}
          color="#1890ff"
          yAxis={{
            min: 0,
            max: 5,
            title: {
              text: t('intelligence.satisfaction_score'),
            },
          }}
          xAxis={{
            title: {
              text: t('intelligence.date'),
            },
          }}
          tooltip={{
            formatter: (datum) => {
              return {
                name: t('intelligence.satisfaction_score'),
                value: datum.score.toFixed(2),
              };
            },
          }}
        />
      </ModernCard>

      {/* Top Topics Chart */}
      <ModernCard title={t('intelligence.top_topics')}>
        <Bar
          data={topicData}
          xField="frequency"
          yField="topic"
          seriesField="sentiment"
          isGroup={true}
          columnStyle={{
            radius: [4, 4, 0, 0],
          }}
          color={['#52c41a', '#faad14', '#ff4d4f']}
          legend={{
            position: 'top',
          }}
          xAxis={{
            title: {
              text: t('intelligence.frequency'),
            },
          }}
          yAxis={{
            title: {
              text: t('intelligence.topics'),
            },
          }}
        />
      </ModernCard>

      {/* User Engagement Summary */}
      <ModernCard title={t('intelligence.user_engagement_summary')}>
        <Row gutter={[16, 16]}>
          {data.userEngagement.slice(0, 4).map((user, index) => (
            <Col xs={24} sm={12} lg={6} key={user.userId}>
              <Card size="small">
                <Statistic
                  title={user.username}
                  value={user.satisfactionScore}
                  prefix={<SmileOutlined />}
                  suffix="/5"
                  precision={1}
                />
                <Progress
                  percent={user.satisfactionScore * 20}
                  size="small"
                  status={user.satisfactionScore >= 4 ? 'success' : user.satisfactionScore >= 3 ? 'normal' : 'exception'}
                />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {t('intelligence.conversations')}: {user.totalConversations}
                </Text>
              </Card>
            </Col>
          ))}
        </Row>
      </ModernCard>
    </Space>
  );
};

export default ConversationAnalytics;