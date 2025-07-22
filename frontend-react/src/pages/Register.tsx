import React, { useState } from 'react';
import { Button, Form, Input, Alert, message } from 'antd';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const register = useAuthStore((s) => s.register);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string; email: string }) => {
    setLoading(true);
    setError(null);
    try {
      await register(values.username, values.password, values.email);
      message.success('Registration successful');
      navigate('/');
          } catch {
      setError('Registration failed.');
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
      <h2>Register</h2>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
      <Form name="register" onFinish={onFinish} layout="vertical" aria-label="Register form">
        <Form.Item name="username" label="Username" rules={[{ required: true }]}> <Input autoFocus aria-label="Username" /> </Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}> <Input aria-label="Email" /> </Form.Item>
        <Form.Item name="password" label="Password" rules={[{ required: true }]}> <Input.Password aria-label="Password" /> </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block aria-label="Register">Register</Button>
        </Form.Item>
      </Form>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
        <a onClick={() => navigate('/login')} tabIndex={0} aria-label="Back to login">Zurück zum Login</a>
      </div>
    </div>
  );
};

export default Register; 