import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Select, Button, message, Spin } from 'antd';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import { Link } from 'react-router-dom';

const dummyUsers = [
  { id: 1, username: 'admin', role: 'admin', status: 'active' },
  { id: 2, username: 'user1', role: 'user', status: 'active' },
  { id: 3, username: 'user2', role: 'user', status: 'inactive' },
];

const columns = [
  { title: 'Username', dataIndex: 'username', key: 'username' },
  { title: 'Role', dataIndex: 'role', key: 'role', render: (role: string) => <Tag color={role === 'admin' ? 'red' : 'blue'}>{role}</Tag> },
  { title: 'Status', dataIndex: 'status', key: 'status', render: (status: string) => <Tag color={status === 'active' ? 'green' : 'gray'}>{status}</Tag> },
];

const Admin: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const [defaultLang, setDefaultLang] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');

  useEffect(() => {
    if (!isAdmin) return;
    setLoading(true);
    api.get('/users/admin/default-language')
      .then(res => setDefaultLang(res.data))
      .catch(() => message.error('Failed to load default language'))
      .finally(() => setLoading(false));
  }, [isAdmin]);

  const handleChange = async (lang: string) => {
    setSaving(true);
    try {
      await api.put('/users/admin/default-language', { language: lang });
      setDefaultLang(lang);
      message.success('Default language updated');
    } catch {
      message.error('Failed to update default language');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card title="Admin Panel" style={{ maxWidth: 800, margin: 'auto' }}>
      <h3>User Management</h3>
      <Table dataSource={dummyUsers} columns={columns} rowKey="id" pagination={false} style={{ marginBottom: 32 }} />
      <h3>System Status</h3>
      <p>All systems operational (Platzhalter)</p>
      {isAdmin && (
        <div style={{ marginTop: 32 }}>
          <h3>Globale Spracheinstellung</h3>
          {loading ? <Spin /> : (
            <>
              <span>Aktuelle Default-Sprache: </span>
              <Select
                value={defaultLang}
                onChange={handleChange}
                style={{ width: 160, marginRight: 16 }}
                disabled={saving}
              >
                <Select.Option value="de">Deutsch</Select.Option>
                <Select.Option value="en">Englisch</Select.Option>
              </Select>
              <Button type="primary" onClick={() => handleChange(defaultLang)} loading={saving} disabled={saving}>
                Speichern
              </Button>
            </>
          )}
          <div style={{ marginTop: 32 }}>
            <Link to="/admin/system-status">
              <Button type="default">Systemstatus & Performance anzeigen</Button>
            </Link>
          </div>
        </div>
      )}
    </Card>
  );
};

export default Admin; 