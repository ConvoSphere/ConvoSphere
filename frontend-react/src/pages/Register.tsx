import React, { useState } from 'react';
import { Button, Form, Input, Alert } from 'antd';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const { t } = useTranslation();
  const register = useAuthStore((s) => s.register);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  // confirmEmail und emailMismatch entfallen, Validierung erfolgt im Form
  const [success, setSuccess] = useState(false);

  const onFinish = async (values: { username: string; password: string; email: string; confirmEmail: string }) => {
    setLoading(true);
    setError(null);
    try {
      await register(values.username, values.password, values.email);
      setSuccess(true);
    } catch {
      setError(t('auth.register.failed'));
    } finally {
      setLoading(false);
    }
  };

  if (isAuthenticated) {
    navigate('/');
    return null;
  }

  return (
    <div style={{ maxWidth: 320, margin: 'auto', marginTop: 64 }}>
      <h2>{t('auth.register.title')}</h2>
      {success ? (
        <Alert
          type="success"
          message={t('auth.register.success')}
          showIcon
          style={{ marginBottom: 16 }}
        />
      ) : (
        <>
          {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
          <Form name="register" onFinish={onFinish} layout="vertical" aria-label={t('auth.register.title')}>
            <Form.Item name="username" label={t('auth.login.username')} rules={[{ required: true, message: t('validation.required') }]}> 
              <Input autoFocus aria-label={t('auth.login.username')} />
            </Form.Item>
            <Form.Item name="email" label={t('auth.register.email')} rules={[{ required: true, type: 'email', message: t('validation.email') }]}> 
              <Input aria-label={t('auth.register.email')} />
            </Form.Item>
            <Form.Item
              name="confirmEmail"
              label={t('auth.register.confirm_email')}
              dependencies={["email"]}
              rules={[{ required: true, message: t('validation.required') },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('email') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error(t('validation.confirm_password')));
                  },
                }),
              ]}
            >
              <Input aria-label={t('auth.register.confirm_email')} type="email" />
            </Form.Item>
            <Form.Item name="password" label={t('auth.login.password')} rules={[{ required: true, message: t('validation.password') }]}> 
              <Input.Password aria-label={t('auth.login.password')} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block aria-label={t('auth.register.button')}>{t('auth.register.button')}</Button>
            </Form.Item>
          </Form>
        </>
      )}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
        <a onClick={() => navigate('/login')} tabIndex={0} aria-label={t('auth.login.link')}>{t('auth.login.link')}</a>
      </div>
    </div>
  );
};

export default Register; 