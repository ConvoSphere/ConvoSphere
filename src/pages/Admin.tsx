import React from 'react';
import { Card, Table, Tag } from 'antd';

const dummyUsers = [
  { id: 1, username: 'admin', role: 'admin', status: 'active' },
  { id: 2, username: 'user1', role: 'user', status: 'active' },
  { id: 3, username: 'user2', role: 'user', status: 'inactive' },
];

const columns = [
  { title: 'Username', dataIndex: 'username', key: 'username' },
  { title: 'Role', dataIndex: 'role', key: 'role', render: (role: string) => <Tag color={role === 'admin' ? 'red' : 'blue'}>{role}</Tag> },
  { title: 'Status', dataIndex: 'status', key: 'status', render: (status: string) => <Tag color={status === 'active' ? 'green' : 'gray'}>{status}</Tag> },
];

const Admin: React.FC = () => {
  return (
    <Card title="Admin Panel" style={{ maxWidth: 800, margin: 'auto' }}>
      <h3>User Management</h3>
      <Table dataSource={dummyUsers} columns={columns} rowKey="id" pagination={false} style={{ marginBottom: 32 }} />
      <h3>System Status</h3>
      <p>All systems operational (Platzhalter)</p>
    </Card>
  );
};

export default Admin; 