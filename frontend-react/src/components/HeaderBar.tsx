import React from 'react';
import { Avatar, Typography, Badge } from 'antd';
import { BellOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import ThemeSwitcher from './ThemeSwitcher';
import LanguageSwitcher from './LanguageSwitcher';
import LogoutButton from './LogoutButton';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';

const { Text, Title } = Typography;

const HeaderBar: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '64px',
    padding: '0 24px',
    backgroundColor: colors.colorBgContainer,
    borderBottom: `1px solid ${colors.colorBorder}`,
    boxShadow: colors.boxShadow,
    backdropFilter: 'blur(10px)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
  };

  const logoStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  };

  const controlsStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  };

  const userInfoStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '8px 16px',
    backgroundColor: colors.colorBgElevated,
    borderRadius: '12px',
    border: `1px solid ${colors.colorBorder}`,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    cursor: 'pointer',
  };

  return (
    <div style={headerStyle}>
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
        <div>
          <Title 
            level={4} 
            style={{ 
              margin: 0,
              color: colors.colorTextBase,
              fontWeight: 600,
            }}
          >
            ConvoSphere
          </Title>
          <Text 
            style={{ 
              fontSize: '12px',
              color: colors.colorTextSecondary,
            }}
          >
            AI Assistant Platform
          </Text>
        </div>
      </div>

      {/* Controls Section */}
      <div style={controlsStyle}>
        {/* Notifications */}
        <Badge count={3} size="small">
          <Avatar 
            icon={<BellOutlined />} 
            size="small"
            style={{ 
              backgroundColor: colors.colorSecondary,
              color: colors.colorTextBase,
              cursor: 'pointer',
            }}
          />
        </Badge>

        {/* Theme Switcher */}
        <ThemeSwitcher />

        {/* Language Switcher */}
        <LanguageSwitcher />

        {/* User Info */}
        {user && (
          <div style={userInfoStyle}>
            <Avatar 
              icon={<UserOutlined />} 
              size="small"
              style={{ 
                backgroundColor: colors.colorAccent,
                color: colors.colorTextBase,
              }}
            />
            <div>
              <Text 
                style={{ 
                  fontSize: '14px',
                  fontWeight: 500,
                  color: colors.colorTextBase,
                  display: 'block',
                }}
              >
                {user.username}
              </Text>
              <Text 
                style={{ 
                  fontSize: '12px',
                  color: colors.colorTextSecondary,
                }}
              >
                {user.role}
              </Text>
            </div>
          </div>
        )}

        {/* Logout Button */}
        <LogoutButton />
      </div>
    </div>
  );
};

export default HeaderBar; 