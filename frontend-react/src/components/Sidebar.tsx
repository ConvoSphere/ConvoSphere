import React from 'react';
import { Menu, Avatar } from 'antd';
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
  ApiOutlined,
  BarChartOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');

  const menuStyle: React.CSSProperties = {
    height: '100%',
    borderRight: 0,
    backgroundColor: colors.colorBgContainer,
    color: colors.colorTextBase,
  };

  const logoStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '20px 16px',
    borderBottom: `1px solid ${colors.colorBorder}`,
    backgroundColor: colors.colorBgElevated,
  };

  const userSectionStyle: React.CSSProperties = {
    padding: '16px',
    borderTop: `1px solid ${colors.colorBorder}`,
    backgroundColor: colors.colorBgElevated,
  };

  const items = [
    { 
      key: '/', 
      icon: <DashboardOutlined style={{ color: colors.colorPrimary }} />, 
      label: 'Dashboard' 
    },
    { 
      key: '/chat', 
      icon: <MessageOutlined style={{ color: colors.colorSecondary }} />, 
      label: 'Chat' 
    },
    { 
      key: '/assistants', 
      icon: <TeamOutlined style={{ color: colors.colorAccent }} />, 
      label: 'Assistants' 
    },
    { 
      key: '/knowledge-base', 
      icon: <BookOutlined style={{ color: colors.colorPrimary }} />, 
      label: 'Knowledge Base' 
    },
    { 
      key: '/tools', 
      icon: <ToolOutlined style={{ color: colors.colorSecondary }} />, 
      label: 'Tools' 
    },
    { 
      key: '/conversations', 
      icon: <AppstoreOutlined style={{ color: colors.colorAccent }} />, 
      label: 'Conversations' 
    },
    { 
      key: '/mcp-tools', 
      icon: <ApiOutlined style={{ color: colors.colorPrimary }} />, 
      label: 'MCP Tools' 
    },
    { 
      key: '/settings', 
      icon: <SettingOutlined style={{ color: colors.colorSecondary }} />, 
      label: 'Settings' 
    },
    { 
      key: '/profile', 
      icon: <UserOutlined style={{ color: colors.colorAccent }} />, 
      label: 'Profile' 
    },
    ...(isAdmin ? [
      { 
        key: '/admin', 
        icon: <TeamOutlined style={{ color: colors.colorPrimary }} />, 
        label: 'Admin' 
      },
      { 
        key: '/admin/system-status', 
        icon: <BarChartOutlined style={{ color: colors.colorSecondary }} />, 
        label: 'System Status' 
      }
    ] : []),
  ];

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo Section */}
      <div style={logoStyle}>
        <Avatar 
          icon={<RobotOutlined />} 
          size="large"
          style={{ 
            backgroundColor: colors.colorPrimary,
            color: colors.colorTextBase,
          }}
        />
        <div style={{ flex: 1 }}>
          <div style={{ 
            fontWeight: 600, 
            fontSize: '16px',
            color: colors.colorTextBase,
          }}>
            AI Assistant
          </div>
          <div style={{ 
            fontSize: '12px',
            color: colors.colorTextSecondary,
          }}>
            {user?.role || 'User'}
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          style={menuStyle}
          items={items}
          onClick={({ key }) => navigate(key)}
          theme="light"
        />
      </div>

      {/* User Section */}
      <div style={userSectionStyle}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px',
          marginBottom: '8px',
        }}>
          <Avatar 
            icon={<UserOutlined />} 
            size="small"
            style={{ 
              backgroundColor: colors.colorSecondary,
              color: colors.colorTextBase,
            }}
          />
          <div style={{ flex: 1 }}>
            <div style={{ 
              fontSize: '14px',
              fontWeight: 500,
              color: colors.colorTextBase,
            }}>
              {user?.username || 'User'}
            </div>
            <div style={{ 
              fontSize: '12px',
              color: colors.colorTextSecondary,
            }}>
              {user?.email || 'user@example.com'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 