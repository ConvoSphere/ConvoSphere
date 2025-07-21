import React, { useState } from 'react';
import { Button, Form, Input, Alert } from 'antd';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const login = useAuthStore((s) => s.login);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    setError(null);
    try {
      await login(values.username, values.password);
      navigate('/');
    } catch (e) {
      setError('Login failed.');
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
      <h2>Login</h2>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
      <Form name="login" onFinish={onFinish} layout="vertical">
        <Form.Item name="username" label="Username" rules={[{ required: true }]}> <Input autoFocus /> </Form.Item>
        <Form.Item name="password" label="Password" rules={[{ required: true }]}> <Input.Password /> </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>Login</Button>
        </Form.Item>
      </Form>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <a onClick={() => navigate('/register')}>Noch keinen Account? Jetzt registrieren</a>
        <a style={{ color: '#888', cursor: 'not-allowed' }}>Passwort vergessen?</a>
      </div>
    </div>
  );
};

export default Login; 