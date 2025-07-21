import React, { useState } from 'react';
import { Layout as AntLayout } from 'antd';
import Sidebar from './Sidebar';
import HeaderBar from './HeaderBar';
import { useAuthStore } from '../store/authStore';

const { Sider, Header, Content } = AntLayout;

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const [collapsed, setCollapsed] = useState(false);

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {isAuthenticated && (
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          breakpoint="md"
          collapsedWidth={60}
          style={{ background: '#fff' }}
        >
          <Sidebar />
        </Sider>
      )}
      <AntLayout>
        <Header style={{ padding: 0, background: '#fff' }}>
          <HeaderBar />
        </Header>
        <Content style={{ margin: 0, padding: 24 }}>{children}</Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout; 