import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { Button, Form, Input, Alert, Spin } from 'antd';

const Profile: React.FC = () => {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const fetchProfile = useAuthStore((s) => s.fetchProfile);
  const updateProfile = useAuthStore((s) => s.updateProfile);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) fetchProfile();
     
  }, []);

  if (!user) return <Spin style={{ marginTop: 64 }} />;

  const onFinish = async (values: { username: string; email: string }) => {
    setLoading(true);
    setError(null);
    try {
      await updateProfile(values);
      setEditing(false);
          } catch {
      setError('Update failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', marginTop: 64 }}>
      <h2>{t('profile.title')}</h2>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
      {!editing ? (
        <div>
          <p><b>{t('profile.username')}:</b> {user.username}</p>
          <p><b>{t('profile.email')}:</b> {user.email}</p>
          <Button onClick={() => setEditing(true)}>{t('profile.edit')}</Button>
        </div>
      ) : (
        <Form initialValues={user} onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label={t('profile.username')} rules={[{ required: true }]}> <Input /> </Form.Item>
          <Form.Item name="email" label={t('profile.email')} rules={[{ required: true, type: 'email' }]}> <Input /> </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>{t('profile.save')}</Button>
            <Button style={{ marginLeft: 8 }} onClick={() => setEditing(false)}>{t('profile.cancel')}</Button>
          </Form.Item>
        </Form>
      )}
    </div>
  );
};

export default Profile; 