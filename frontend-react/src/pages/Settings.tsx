import React, { useState } from 'react';
import { Card, Switch, Select, Form, message } from 'antd';
import { useAuthStore } from '../store/authStore';
import { useTranslation } from 'react-i18next';

const Settings: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const updateProfile = useAuthStore((s) => s.updateProfile);
  const { i18n, t } = useTranslation();
  const [saving, setSaving] = useState(false);

  const handleLanguageChange = async (lng: string) => {
    if (!user) return;
    setSaving(true);
    try {
      await updateProfile({ language: lng });
      i18n.changeLanguage(lng);
      message.success(t('settings.language_updated', 'Language updated'));
    } catch {
      message.error(t('settings.language_update_failed', 'Failed to update language'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card title={t('settings.title', 'Settings')} style={{ maxWidth: 500, margin: 'auto' }}>
      <Form layout="vertical">
        <Form.Item label={t('settings.language', 'Language')}>
          <Select
            value={user?.language || i18n.language}
            onChange={handleLanguageChange}
            style={{ width: 160 }}
            loading={saving}
            disabled={saving}
          >
            <Select.Option value="en">{t('language.en')}</Select.Option>
            <Select.Option value="de">{t('language.de')}</Select.Option>
            <Select.Option value="fr">{t('language.fr')}</Select.Option>
            <Select.Option value="es">{t('language.es')}</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item label={t('settings.theme', 'Theme')}>
          <Switch checkedChildren="Dark" unCheckedChildren="Light" defaultChecked={false} />
        </Form.Item>
        <Form.Item label={t('settings.notifications', 'Notifications')}>
          <Switch defaultChecked />
        </Form.Item>
      </Form>
    </Card>
  );
};

export default Settings; 