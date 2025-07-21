import React from 'react';
import { Card, Row, Col } from 'antd';

const Dashboard: React.FC = () => (
  <div>
    <h2>Dashboard</h2>
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col span={8}><Card title="Conversations">Coming soon</Card></Col>
      <Col span={8}><Card title="Knowledge Base">Coming soon</Card></Col>
      <Col span={8}><Card title="System Status">Coming soon</Card></Col>
    </Row>
    <Card title="Quicklinks">
      <ul>
        <li>Chat starten</li>
        <li>Dokument hochladen</li>
        <li>Assistenten verwalten</li>
      </ul>
    </Card>
  </div>
);

export default Dashboard; 