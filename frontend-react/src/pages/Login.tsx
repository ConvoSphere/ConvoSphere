import React, { useState } from 'react';
import { Button, Form, Input, Alert, Modal, message } from 'antd';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const login = useAuthStore((s) => s.login);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [forgotVisible, setForgotVisible] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    setError(null);
    try {
      await login(values.username, values.password);
      message.success('Login successful');
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
      <Form name="login" onFinish={onFinish} layout="vertical" aria-label="Login form">
        <Form.Item name="username" label="Username" rules={[{ required: true }]}> <Input autoFocus aria-label="Username" /> </Form.Item>
        <Form.Item name="password" label="Password" rules={[{ required: true }]}> <Input.Password aria-label="Password" /> </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block aria-label="Login">Login</Button>
        </Form.Item>
      </Form>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <a onClick={() => navigate('/register')} tabIndex={0} aria-label="Register">Noch keinen Account? Jetzt registrieren</a>
        <a onClick={() => setForgotVisible(true)} tabIndex={0} aria-label="Forgot password?">Passwort vergessen?</a>
      </div>
      <Modal
        open={forgotVisible}
        onCancel={() => setForgotVisible(false)}
        title="Passwort zurücksetzen"
        footer={<Button onClick={() => setForgotVisible(false)}>Schließen</Button>}
      >
        <p>Bitte kontaktiere den Support oder nutze die Passwort-Reset-Funktion (noch nicht implementiert).</p>
      </Modal>
    </div>
  );
};

export default Login; 