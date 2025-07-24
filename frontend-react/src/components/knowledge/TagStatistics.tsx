import React from 'react';
import { Row, Col, Card, Statistic } from 'antd';
import { TagOutlined, BarChartOutlined } from '@ant-design/icons';

interface TagStatisticsProps {
  totalTags: number;
  systemTags: number;
  userTags: number;
  totalUsage: number;
}

const TagStatistics: React.FC<TagStatisticsProps> = ({ totalTags, systemTags, userTags, totalUsage }) => (
  <Row gutter={16} style={{ marginBottom: 24 }}>
    <Col span={6}>
      <Card>
        <Statistic
          title="Total Tags"
          value={totalTags}
          prefix={<TagOutlined />}
        />
      </Card>
    </Col>
    <Col span={6}>
      <Card>
        <Statistic
          title="System Tags"
          value={systemTags}
          valueStyle={{ color: '#cf1322' }}
        />
      </Card>
    </Col>
    <Col span={6}>
      <Card>
        <Statistic
          title="User Tags"
          value={userTags}
          valueStyle={{ color: '#3f8600' }}
        />
      </Card>
    </Col>
    <Col span={6}>
      <Card>
        <Statistic
          title="Total Usage"
          value={totalUsage}
          prefix={<BarChartOutlined />}
        />
      </Card>
    </Col>
  </Row>
);

export default TagStatistics;