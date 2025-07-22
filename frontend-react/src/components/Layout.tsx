import React, { useState } from 'react';
import { Layout as AntLayout } from 'antd';
import Sidebar from './Sidebar';
import HeaderBar from './HeaderBar';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';

const { Sider, Header, Content } = AntLayout;

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const [collapsed, setCollapsed] = useState(false);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return (
    <AntLayout 
      style={{ 
        minHeight: '100vh',
        backgroundColor: colors.colorBgBase,
      }}
    >
      {isAuthenticated && (
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          breakpoint="md"
          collapsedWidth={60}
          style={{ 
            background: colors.colorBgContainer,
            borderRight: `1px solid ${colors.colorBorder}`,
            boxShadow: colors.boxShadow,
          }}
          theme="light"
        >
          <Sidebar />
        </Sider>
      )}
      <AntLayout style={{ backgroundColor: colors.colorBgBase }}>
        <Header 
          style={{ 
            padding: 0, 
            background: colors.colorBgContainer,
            borderBottom: `1px solid ${colors.colorBorder}`,
            boxShadow: colors.boxShadow,
            position: 'sticky',
            top: 0,
            zIndex: 1000,
          }}
        >
          <HeaderBar />
        </Header>
        <Content 
          style={{ 
            margin: 0, 
            padding: '24px',
            backgroundColor: colors.colorBgBase,
            minHeight: 'calc(100vh - 64px)', // 64px ist die Header-Höhe
          }}
        >
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout; 