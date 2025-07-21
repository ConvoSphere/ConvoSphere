import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Button, Form, Input, Alert, Spin } from 'antd';

const Profile: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const fetchProfile = useAuthStore((s) => s.fetchProfile);
  const updateProfile = useAuthStore((s) => s.updateProfile);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) fetchProfile();
    // eslint-disable-next-line
  }, []);

  if (!user) return <Spin style={{ marginTop: 64 }} />;

  const onFinish = async (values: { username: string; email: string }) => {
    setLoading(true);
    setError(null);
    try {
      await updateProfile(values);
      setEditing(false);
    } catch (e) {
      setError('Update failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', marginTop: 64 }}>
      <h2>Profile</h2>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
      {!editing ? (
        <div>
          <p><b>Username:</b> {user.username}</p>
          <p><b>Email:</b> {user.email}</p>
          <Button onClick={() => setEditing(true)}>Edit</Button>
        </div>
      ) : (
        <Form initialValues={user} onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label="Username" rules={[{ required: true }]}> <Input /> </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}> <Input /> </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>Save</Button>
            <Button style={{ marginLeft: 8 }} onClick={() => setEditing(false)}>Cancel</Button>
          </Form.Item>
        </Form>
      )}
    </div>
  );
};

export default Profile; 