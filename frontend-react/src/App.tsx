import React from 'react';
import { ConfigProvider, theme as antdTheme } from 'antd';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import ThemeSwitcher from './components/ThemeSwitcher';
import LanguageSwitcher from './components/LanguageSwitcher';
import LogoutButton from './components/LogoutButton';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Assistants from './pages/Assistants';
import KnowledgeBase from './pages/KnowledgeBase';
import Tools from './pages/Tools';
import Settings from './pages/Settings';
import Admin from './pages/Admin';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import Conversations from './pages/Conversations';
import McpTools from './pages/McpTools';
import SystemStatus from './pages/SystemStatus';

const App: React.FC = () => {
  return (
    <I18nextProvider i18n={i18n}>
      <ConfigProvider
        theme={{
          algorithm: antdTheme.defaultAlgorithm,
        }}
      >
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ThemeSwitcher />
                    <LanguageSwitcher />
                    <LogoutButton />
                    <Routes>
                      <Route path="/" element={<Chat />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/assistants" element={<Assistants />} />
                      <Route path="/knowledge-base" element={<KnowledgeBase />} />
                      <Route path="/tools" element={<Tools />} />
                      <Route path="/settings" element={<Settings />} />
                      <Route path="/admin" element={<Admin />} />
                      <Route path="/profile" element={<Profile />} />
                      <Route path="/conversations" element={<Conversations />} />
                      <Route path="/mcp-tools" element={<McpTools />} />
                      <Route path="/admin/system-status" element={<SystemStatus />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </ConfigProvider>
    </I18nextProvider>
  );
};

export default App; 