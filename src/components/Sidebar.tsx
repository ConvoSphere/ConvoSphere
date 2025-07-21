import React from 'react';
import { Menu } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  DashboardOutlined,
  MessageOutlined,
  TeamOutlined,
  BookOutlined,
  ToolOutlined,
  SettingOutlined,
  UserOutlined,
  AppstoreOutlined,
  ApiOutlined
} from '@ant-design/icons';

const items = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/chat', icon: <MessageOutlined />, label: 'Chat' },
  { key: '/assistants', icon: <TeamOutlined />, label: 'Assistants' },
  { key: '/knowledge-base', icon: <BookOutlined />, label: 'Knowledge Base' },
  { key: '/tools', icon: <ToolOutlined />, label: 'Tools' },
  { key: '/conversations', icon: <AppstoreOutlined />, label: 'Conversations' },
  { key: '/mcp-tools', icon: <ApiOutlined />, label: 'MCP Tools' },
  { key: '/settings', icon: <SettingOutlined />, label: 'Settings' },
  { key: '/profile', icon: <UserOutlined />, label: 'Profile' },
  { key: '/admin', icon: <TeamOutlined />, label: 'Admin' },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  return (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      style={{ height: '100%', borderRight: 0 }}
      items={items}
      onClick={({ key }) => navigate(key)}
    />
  );
};

export default Sidebar; 