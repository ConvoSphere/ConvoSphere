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
  // confirmEmail und emailMismatch entfallen, Validierung erfolgt im Form
  const [success, setSuccess] = useState(false);

  const onFinish = async (values: { username: string; password: string; email: string; confirmEmail: string }) => {
    setLoading(true);
    setError(null);
    try {
      await register(values.username, values.password, values.email);
      setSuccess(true);
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
      {success ? (
        <Alert
          type="success"
          message="Registration successful! Please check your email to confirm your account or log in."
          showIcon
          style={{ marginBottom: 16 }}
        />
      ) : (
        <>
          {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
          <Form name="register" onFinish={onFinish} layout="vertical" aria-label="Register form">
            <Form.Item name="username" label="Username" rules={[{ required: true, message: 'Please enter Username' }]}> 
              <Input autoFocus aria-label="Username" />
            </Form.Item>
            <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email', message: 'Please enter Email' }]}> 
              <Input aria-label="Email" />
            </Form.Item>
            <Form.Item
              name="confirmEmail"
              label="Confirm Email"
              dependencies={["email"]}
              rules={[{ required: true, message: 'Please confirm your email' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('email') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('Email addresses do not match'));
                  },
                }),
              ]}
            >
              <Input aria-label="Confirm Email" type="email" />
            </Form.Item>
            <Form.Item name="password" label="Password" rules={[{ required: true, message: 'Please enter Password' }]}> 
              <Input.Password aria-label="Password" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block aria-label="Register">Register</Button>
            </Form.Item>
          </Form>
        </>
      )}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
        <a onClick={() => navigate('/login')} tabIndex={0} aria-label="Back to login">Zurück zum Login</a>
      </div>
    </div>
  );
};

export default Register; 