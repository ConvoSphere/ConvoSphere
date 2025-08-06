import React from 'react';
import { Row, Col, Card, Typography, Space, Tag, List, Avatar, Progress, Tooltip } from 'antd';
import { 
  TagOutlined, 
  MessageOutlined, 
  SmileOutlined,
  MehOutlined,
  FrownOutlined,
  FireOutlined 
} from '@ant-design/icons';
import { Scatter, WordCloud } from '@ant-design/plots';
import { useTranslation } from 'react-i18next';
import type { TopicCluster } from '../../services/conversationIntelligence';
import ModernCard from '../ModernCard';

const { Title, Text } = Typography;

interface TopicClusteringProps {
  data: TopicCluster[];
  loading?: boolean;
}

const TopicClustering: React.FC<TopicClusteringProps> = ({ 
  data, 
  loading = false 
}) => {
  const { t } = useTranslation();

  if (!data || data.length === 0) {
    return (
      <ModernCard>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Text type="secondary">{t('intelligence.no_topic_data')}</Text>
        </div>
      </ModernCard>
    );
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <SmileOutlined style={{ color: '#52c41a' }} />;
      case 'neutral':
        return <MehOutlined style={{ color: '#faad14' }} />;
      case 'negative':
        return <FrownOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <MehOutlined />;
    }
  };

  const getSentimentTag = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <Tag color="success">{t('intelligence.positive')}</Tag>;
      case 'neutral':
        return <Tag color="warning">{t('intelligence.neutral')}</Tag>;
      case 'negative':
        return <Tag color="error">{t('intelligence.negative')}</Tag>;
      default:
        return <Tag>{t('intelligence.unknown')}</Tag>;
    }
  };

  // Prepare data for bubble chart
  const bubbleData = data.map(topic => ({
    x: topic.frequency,
    y: topic.conversations.length,
    size: topic.keywords.length,
    name: topic.name,
    sentiment: topic.sentiment,
  }));

  // Prepare data for word cloud
  const wordCloudData = data.flatMap(topic => 
    topic.keywords.map(keyword => ({
      word: keyword,
      weight: topic.frequency,
      sentiment: topic.sentiment,
    }))
  );

  // Sort topics by frequency
  const sortedTopics = [...data].sort((a, b) => b.frequency - a.frequency);

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* Topic Overview */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <ModernCard>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>{t('intelligence.total_topics')}</Title>
              <Text strong style={{ fontSize: '24px' }}>
                {data.length}
              </Text>
            </div>
          </ModernCard>
        </Col>
        <Col xs={24} md={8}>
          <ModernCard>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>{t('intelligence.total_keywords')}</Title>
              <Text strong style={{ fontSize: '24px' }}>
                {data.reduce((sum, topic) => sum + topic.keywords.length, 0)}
              </Text>
            </div>
          </ModernCard>
        </Col>
        <Col xs={24} md={8}>
          <ModernCard>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>{t('intelligence.avg_frequency')}</Title>
              <Text strong style={{ fontSize: '24px' }}>
                {(data.reduce((sum, topic) => sum + topic.frequency, 0) / data.length).toFixed(1)}
              </Text>
            </div>
          </ModernCard>
        </Col>
      </Row>

      {/* Topic Scatter Chart */}
      <ModernCard title={t('intelligence.topic_distribution')}>
        <Scatter
          data={bubbleData}
          xField="x"
          yField="y"
          sizeField="size"
          colorField="sentiment"
          color={['#52c41a', '#faad14', '#ff4d4f']}
          pointStyle={{
            fillOpacity: 0.8,
            stroke: '#fff',
            lineWidth: 1,
          }}
          xAxis={{
            title: {
              text: t('intelligence.frequency'),
            },
          }}
          yAxis={{
            title: {
              text: t('intelligence.conversation_count'),
            },
          }}
          tooltip={{
            formatter: (datum) => {
              return {
                name: datum.name,
                value: `${t('intelligence.frequency')}: ${datum.x}, ${t('intelligence.conversations')}: ${datum.y}, ${t('intelligence.keywords')}: ${datum.size}`,
              };
            },
          }}
        />
      </ModernCard>

      {/* Word Cloud */}
      <ModernCard title={t('intelligence.keyword_cloud')}>
        <WordCloud
          data={wordCloudData}
          wordField="word"
          weightField="weight"
          colorField="sentiment"
          color={['#52c41a', '#faad14', '#ff4d4f']}
          wordStyle={{
            fontFamily: 'Verdana',
            fontSize: [12, 60],
            rotation: 0,
          }}
          random={() => 0.5}
          tooltip={{
            formatter: (datum) => {
              return {
                name: datum.word,
                value: `${t('intelligence.weight')}: ${datum.weight}`,
              };
            },
          }}
        />
      </ModernCard>

      {/* Top Topics List */}
      <ModernCard title={t('intelligence.top_topics')}>
        <List
          dataSource={sortedTopics.slice(0, 10)}
          renderItem={(topic, index) => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <Avatar 
                    icon={<FireOutlined />} 
                    style={{ 
                      backgroundColor: index < 3 ? '#ff4d4f' : '#1890ff' 
                    }} 
                  />
                }
                title={
                  <Space>
                    <Text strong>{topic.name}</Text>
                    {getSentimentTag(topic.sentiment)}
                    <Tag color="blue">{t('intelligence.rank')} #{index + 1}</Tag>
                  </Space>
                }
                description={
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Space>
                      <Text type="secondary">
                        {t('intelligence.frequency')}: {topic.frequency}
                      </Text>
                      <Text type="secondary">
                        {t('intelligence.conversations')}: {topic.conversations.length}
                      </Text>
                      <Text type="secondary">
                        {t('intelligence.keywords')}: {topic.keywords.length}
                      </Text>
                    </Space>
                    <div>
                      <Text type="secondary">{t('intelligence.keywords')}: </Text>
                      <Space wrap>
                        {topic.keywords.slice(0, 5).map((keyword, idx) => (
                          <Tag key={idx} size="small" icon={<TagOutlined />}>
                            {keyword}
                          </Tag>
                        ))}
                        {topic.keywords.length > 5 && (
                          <Tag size="small">+{topic.keywords.length - 5} more</Tag>
                        )}
                      </Space>
                    </div>
                    <Progress
                      percent={(topic.frequency / sortedTopics[0].frequency) * 100}
                      size="small"
                      showInfo={false}
                      strokeColor={index < 3 ? '#ff4d4f' : '#1890ff'}
                    />
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </ModernCard>

      {/* Sentiment Distribution by Topic */}
      <ModernCard title={t('intelligence.sentiment_by_topic')}>
        <Row gutter={[16, 16]}>
          {['positive', 'neutral', 'negative'].map(sentiment => {
            const topicsWithSentiment = data.filter(topic => topic.sentiment === sentiment);
            return (
              <Col xs={24} md={8} key={sentiment}>
                <Card size="small">
                  <div style={{ textAlign: 'center' }}>
                    {getSentimentIcon(sentiment)}
                    <Title level={5} style={{ marginTop: 8 }}>
                      {t(`intelligence.${sentiment}`)}
                    </Title>
                    <Text strong style={{ fontSize: '18px' }}>
                      {topicsWithSentiment.length}
                    </Text>
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary">
                        {((topicsWithSentiment.length / data.length) * 100).toFixed(1)}%
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

export default TopicClustering;