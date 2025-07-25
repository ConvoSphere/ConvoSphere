import React, { Suspense, useState } from 'react';
import { ConfigProvider, theme as antdTheme, Spin, Button } from 'antd';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import { DashboardOutlined } from '@ant-design/icons';
import i18n from './i18n';
import { useThemeStore } from './store/themeStore';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import PerformanceMonitor from './components/PerformanceMonitor';
import performanceMonitor from './utils/performance';

// Import modern UI styles
import './styles/animations.css';
import './styles/chat.css';

import {
  LazyChatPage,
  LazyDashboardPage,
  LazyAssistantsPage,
  LazyKnowledgeBasePage,
  LazyToolsPage,
  LazySettingsPage,
  LazyAdminPage,
  LazyLoginPage,
  LazyRegisterPage,
  LazyProfilePage,
  LazyConversationsPage,
  LazyMcpToolsPage,
  LazySystemStatusPage,
} from './components/LazyComponents';

// Loading component with theme-aware styling
const LoadingSpinner: React.FC = () => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      backgroundColor: colors.colorBgBase,
    }}>
      <div style={{ textAlign: 'center' }}>
        <Spin size="large" style={{ color: colors.colorPrimary }} />
        <div style={{ 
          marginTop: '16px', 
          color: colors.colorTextSecondary,
          fontSize: '14px',
        }}>
          Loading ConvoSphere...
        </div>
      </div>
    </div>
  );
};

// Error fallback component
const ErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({ 
  error, 
  resetErrorBoundary 
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      backgroundColor: colors.colorBgBase,
      padding: '20px',
    }}>
      <div style={{
        maxWidth: '500px',
        textAlign: 'center',
        backgroundColor: colors.colorBgContainer,
        padding: '32px',
        borderRadius: '12px',
        border: `1px solid ${colors.colorBorder}`,
        boxShadow: colors.boxShadow,
      }}>
        <h2 style={{ color: colors.colorError, marginBottom: '16px' }}>
          Something went wrong
        </h2>
        <p style={{ color: colors.colorTextSecondary, marginBottom: '24px' }}>
          We're sorry, but something unexpected happened while loading the application.
        </p>
        <button
          onClick={resetErrorBoundary}
          style={{
            backgroundColor: colors.colorPrimary,
            color: colors.colorTextBase,
            border: 'none',
            padding: '12px 24px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          Try Again
        </button>
        {process.env.NODE_ENV === 'development' && (
          <details style={{ marginTop: '16px', textAlign: 'left' }}>
            <summary style={{ cursor: 'pointer', color: colors.colorTextSecondary }}>
              Error Details
            </summary>
            <pre style={{
              marginTop: '8px',
              padding: '12px',
              backgroundColor: colors.colorBgElevated,
              borderRadius: '4px',
              fontSize: '12px',
              color: colors.colorTextSecondary,
              overflow: 'auto',
              maxHeight: '200px',
            }}>
              {error.message}
              {'\n'}
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const { mode, getCurrentTheme } = useThemeStore();
  const currentTheme = getCurrentTheme();
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);

  // Initialize performance monitoring
  React.useEffect(() => {
    performanceMonitor.init();
    
    // Mark app initialization
    performanceMonitor.mark('app-init-start');
    
    return () => {
      performanceMonitor.mark('app-init-end');
      performanceMonitor.measure('App Initialization', 'app-init-start', 'app-init-end');
    };
  }, []);

  return (
    <ErrorBoundary
      fallback={<ErrorFallback error={new Error('App failed to load')} resetErrorBoundary={() => window.location.reload()} />}
      onError={(error, errorInfo) => {
        console.error('App Error:', error, errorInfo);
        // Send to error reporting service
        performanceMonitor.logError('App Error', { error: error.message, errorInfo });
      }}
    >
      <I18nextProvider i18n={i18n}>
        <ConfigProvider
          theme={{
            algorithm: mode === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
            token: currentTheme.token,
          }}
        >
          <Router>
            <ErrorBoundary
              onError={(error, errorInfo) => {
                console.error('Router Error:', error, errorInfo);
                performanceMonitor.logError('Router Error', { error: error.message, errorInfo });
              }}
            >
              <Routes>
                <Route 
                  path="/login" 
                  element={
                    <ErrorBoundary>
                      <Suspense fallback={<LoadingSpinner />}>
                        <LazyLoginPage />
                      </Suspense>
                    </ErrorBoundary>
                  } 
                />
                <Route 
                  path="/register" 
                  element={
                    <ErrorBoundary>
                      <Suspense fallback={<LoadingSpinner />}>
                        <LazyRegisterPage />
                      </Suspense>
                    </ErrorBoundary>
                  } 
                />
                <Route
                  path="/*"
                  element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <Layout>
                          <ErrorBoundary>
                            <Suspense fallback={<LoadingSpinner />}>
                              <Routes>
                                <Route path="/" element={<LazyChatPage />} />
                                <Route path="/dashboard" element={<LazyDashboardPage />} />
                                <Route path="/assistants" element={<LazyAssistantsPage />} />
                                <Route path="/knowledge-base" element={<LazyKnowledgeBasePage />} />
                                <Route path="/tools" element={<LazyToolsPage />} />
                                <Route path="/settings" element={<LazySettingsPage />} />
                                <Route path="/admin" element={<LazyAdminPage />} />
                                <Route path="/profile" element={<LazyProfilePage />} />
                                <Route path="/conversations" element={<LazyConversationsPage />} />
                                <Route path="/mcp-tools" element={<LazyMcpToolsPage />} />
                                <Route path="/admin/system-status" element={<LazySystemStatusPage />} />
                              </Routes>
                            </Suspense>
                          </ErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    </ErrorBoundary>
                  }
                />
              </Routes>
            </ErrorBoundary>
          </Router>

          {/* Performance Monitor Toggle (Development Only) */}
          {process.env.NODE_ENV === 'development' && (
            <Button
              type="primary"
              icon={<DashboardOutlined />}
              size="small"
              onClick={() => setShowPerformanceMonitor(!showPerformanceMonitor)}
              style={{
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                zIndex: 1001,
                borderRadius: '50%',
                width: '48px',
                height: '48px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              }}
            />
          )}

          {/* Performance Monitor */}
          <PerformanceMonitor
            visible={showPerformanceMonitor}
            onClose={() => setShowPerformanceMonitor(false)}
          />
        </ConfigProvider>
      </I18nextProvider>
    </ErrorBoundary>
  );
};

export default App; 