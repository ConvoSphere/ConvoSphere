import React, { useState } from 'react';
import { Button, Form, Input, Alert } from 'antd';
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
      navigate('/');
    } catch (e) {
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
      <Form name="register" onFinish={onFinish} layout="vertical">
        <Form.Item name="username" label="Username" rules={[{ required: true }]}> <Input autoFocus /> </Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}> <Input /> </Form.Item>
        <Form.Item name="password" label="Password" rules={[{ required: true }]}> <Input.Password /> </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>Register</Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Register; 