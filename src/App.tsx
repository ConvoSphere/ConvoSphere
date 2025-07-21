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

const App: React.FC = () => {
  return (
    <I18nextProvider i18n={i18n}>
      <ConfigProvider
        theme={{
          algorithm: antdTheme.defaultAlgorithm,
        }}
      >
        <Router>
          <div style={{ padding: 24, display: 'flex', gap: 16 }}>
            <ThemeSwitcher />
            <LanguageSwitcher />
            <LogoutButton />
          </div>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <Layout>
                  <Routes>
                    <Route path="/" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
                    <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                    <Route path="/assistants" element={<ProtectedRoute><Assistants /></ProtectedRoute>} />
                    <Route path="/knowledge-base" element={<ProtectedRoute><KnowledgeBase /></ProtectedRoute>} />
                    <Route path="/tools" element={<ProtectedRoute><Tools /></ProtectedRoute>} />
                    <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
                    <Route path="/admin" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
                    <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                    <Route path="/conversations" element={<ProtectedRoute><Conversations /></ProtectedRoute>} />
                    <Route path="/mcp-tools" element={<ProtectedRoute><McpTools /></ProtectedRoute>} />
                  </Routes>
                </Layout>
              }
            />
          </Routes>
        </Router>
      </ConfigProvider>
    </I18nextProvider>
  );
};

export default App; 