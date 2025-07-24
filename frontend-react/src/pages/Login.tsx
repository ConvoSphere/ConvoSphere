import React, { useState, useEffect } from 'react';
import { Button, Form, Input, Alert, Modal, message, Divider } from 'antd';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { getSSOProviders, ssoLogin } from '../services/auth';

interface SSOProvider {
  id: string;
  name: string;
  type: string;
  icon: string;
  login_url: string;
}

const Login: React.FC = () => {
  const { t } = useTranslation();
  const login = useAuthStore((s) => s.login);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [forgotVisible, setForgotVisible] = useState(false);
  const [ssoProviders, setSsoProviders] = useState<SSOProvider[]>([]);

  useEffect(() => {
    // Load SSO providers on component mount
    const loadSSOProviders = async () => {
      try {
        const providers = await getSSOProviders();
        setSsoProviders(providers || []); // immer ein Array setzen
          } catch {
      setSsoProviders([]); // auch im Fehlerfall ein Array
      console.log('No SSO providers configured or error loading providers');
    }
    };
    loadSSOProviders();
  }, []);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    setError(null);
    try {
      await login(values.username, values.password);
      message.success(t('auth.login.success'));
      navigate('/');
    } catch {
      setError(t('auth.login.failed'));
    } finally {
      setLoading(false);
    }
  };

  const handleSSOLogin = async (provider: string) => {
    try {
      await ssoLogin(provider);
    } catch {
      setError(t('auth.login.failed'));
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'google':
        return '🔍'; // Google icon
      case 'microsoft':
        return '🪟'; // Microsoft icon
      case 'github':
        return '🐙'; // GitHub icon
      case 'saml':
        return '🔐'; // SAML icon
      case 'oidc':
        return '🔑'; // OIDC icon
      default:
        return '🔗'; // Default SSO icon
    }
  };

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  if (isAuthenticated) {
    return null;
  }

  return (
    <div style={{ maxWidth: 400, margin: 'auto', marginTop: 64 }}>
      <h2>{t('auth.login.title')}</h2>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
      
      {/* SSO Login Buttons */}
      {ssoProviders.length > 0 && (
        <>
          <div style={{ marginBottom: 16 }}>
            {ssoProviders.map((provider) => (
              <Button
                key={provider.id}
                size="large"
                block
                style={{ marginBottom: 8 }}
                onClick={() => handleSSOLogin(provider.id)}
                icon={<span>{getProviderIcon(provider.id)}</span>}
              >
                {t('auth.login.button')} {provider.name}
              </Button>
            ))}
          </div>
          <Divider>{t('common.or')}</Divider>
        </>
      )}

      {/* Local Login Form */}
      <Form name="login" onFinish={onFinish} layout="vertical" aria-label={t('auth.login.title')}>
        <Form.Item name="username" label={t('auth.login.username')} rules={[{ required: true, message: t('validation.required') }]}>
          <Input autoFocus aria-label={t('auth.login.username')} />
        </Form.Item>
        <Form.Item name="password" label={t('auth.login.password')} rules={[{ required: true, message: t('validation.required') }]}>
          <Input.Password aria-label={t('auth.login.password')} />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block aria-label={t('auth.login.button')}>
            {t('auth.login.button')}
          </Button>
        </Form.Item>
      </Form>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <a onClick={() => navigate('/register')} tabIndex={0} aria-label={t('auth.register.title')}>
          {t('auth.register.link')}
        </a>
        <a onClick={() => setForgotVisible(true)} tabIndex={0} aria-label={t('auth.forgot_password')}>
          {t('auth.forgot_password')}
        </a>
      </div>
      
      <Modal
        open={forgotVisible}
        onCancel={() => setForgotVisible(false)}
        title={t('auth.forgot_password')}
        footer={<Button onClick={() => setForgotVisible(false)}>{t('common.close')}</Button>}
      >
        <p>{t('auth.forgot_password_message')}</p>
      </Modal>
    </div>
  );
};

export default Login; 