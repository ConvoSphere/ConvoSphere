import React, { useState } from 'react';
import {
  Button,
  Space,
  Dropdown,
  Menu,
  Tooltip,
  Modal,
  Form,
  Select,
  InputNumber,
  Switch,
  message,
  Divider,
} from 'antd';
import {
  SaveOutlined,
  DownloadOutlined,
  ClearOutlined,
  SettingOutlined,
  MoreOutlined,
  ExportOutlined,
  ImportOutlined,
  ShareAltOutlined,
  BookOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { ChatSettings, ChatExportOptions } from '../types/chat.types';

const { Option } = Select;

interface ChatToolbarProps {
  onSave?: () => void;
  onExport?: (options: ChatExportOptions) => void;
  onClear?: () => void;
  onSettings?: (settings: ChatSettings) => void;
  onImport?: (file: File) => void;
  onShare?: () => void;
  settings?: ChatSettings;
  hasMessages?: boolean;
  isLoading?: boolean;
  disabled?: boolean;
}

const ChatToolbar: React.FC<ChatToolbarProps> = ({
  onSave,
  onExport,
  onClear,
  onSettings,
  onImport,
  onShare,
  settings,
  hasMessages = false,
  isLoading = false,
  disabled = false,
}) => {
  const { t } = useTranslation();
  const [settingsModalVisible, setSettingsModalVisible] = useState(false);
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [form] = Form.useForm();

  const handleSave = () => {
    if (onSave) {
      onSave();
    }
  };

  const handleClear = () => {
    if (onClear) {
      onClear();
    }
  };

  const handleSettings = () => {
    setSettingsModalVisible(true);
  };

  const handleExport = () => {
    setExportModalVisible(true);
  };

  const handleImport = (file: File) => {
    if (onImport) {
      onImport(file);
    }
  };

  const handleShare = () => {
    if (onShare) {
      onShare();
    }
  };

  const handleSettingsSubmit = (values: ChatSettings) => {
    if (onSettings) {
      onSettings(values);
    }
    setSettingsModalVisible(false);
    message.success(t('chat.settings_updated'));
  };

  const handleExportSubmit = (values: ChatExportOptions) => {
    if (onExport) {
      onExport(values);
    }
    setExportModalVisible(false);
  };

  const exportMenu = (
    <Menu>
      <Menu.Item key="json" icon={<ExportOutlined />} onClick={() => handleExport()}>
        {t('chat.export_json')}
      </Menu.Item>
      <Menu.Item key="txt" icon={<ExportOutlined />} onClick={() => handleExport()}>
        {t('chat.export_txt')}
      </Menu.Item>
      <Menu.Item key="md" icon={<ExportOutlined />} onClick={() => handleExport()}>
        {t('chat.export_md')}
      </Menu.Item>
      <Menu.Item key="pdf" icon={<ExportOutlined />} onClick={() => handleExport()}>
        {t('chat.export_pdf')}
      </Menu.Item>
    </Menu>
  );

  const moreMenu = (
    <Menu>
      <Menu.Item key="import" icon={<ImportOutlined />} onClick={() => document.getElementById('import-input')?.click()}>
        {t('chat.import')}
      </Menu.Item>
      <Menu.Item key="share" icon={<ShareAltOutlined />} onClick={handleShare}>
        {t('chat.share')}
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="settings" icon={<SettingOutlined />} onClick={handleSettings}>
        {t('chat.settings')}
      </Menu.Item>
    </Menu>
  );

  return (
    <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', backgroundColor: '#fafafa' }}>
      <Space>
        {/* Save Button */}
        {onSave && (
          <Tooltip title={t('chat.save_thread')}>
            <Button
              icon={<SaveOutlined />}
              onClick={handleSave}
              disabled={disabled || isLoading || !hasMessages}
              size="small"
            />
          </Tooltip>
        )}

        {/* Export Dropdown */}
        {onExport && hasMessages && (
          <Dropdown overlay={exportMenu} trigger={['click']}>
            <Tooltip title={t('chat.export')}>
              <Button
                icon={<DownloadOutlined />}
                disabled={disabled || isLoading}
                size="small"
              />
            </Tooltip>
          </Dropdown>
        )}

        <Divider type="vertical" />

        {/* Knowledge Base Toggle */}
        {settings?.use_knowledge_base !== undefined && (
          <Tooltip title={t('chat.knowledge_base')}>
            <Button
              icon={<BookOutlined />}
              type={settings.use_knowledge_base ? 'primary' : 'default'}
              onClick={() => onSettings?.({
                ...settings,
                use_knowledge_base: !settings.use_knowledge_base
              })}
              disabled={disabled || isLoading}
              size="small"
            />
          </Tooltip>
        )}

        {/* Tools Toggle */}
        {settings?.use_tools !== undefined && (
          <Tooltip title={t('chat.tools')}>
            <Button
              icon={<ToolOutlined />}
              type={settings.use_tools ? 'primary' : 'default'}
              onClick={() => onSettings?.({
                ...settings,
                use_tools: !settings.use_tools
              })}
              disabled={disabled || isLoading}
              size="small"
            />
          </Tooltip>
        )}

        <Divider type="vertical" />

        {/* Clear Button */}
        {onClear && hasMessages && (
          <Tooltip title={t('chat.clear_messages')}>
            <Button
              icon={<ClearOutlined />}
              onClick={handleClear}
              disabled={disabled || isLoading}
              size="small"
            />
          </Tooltip>
        )}

        {/* More Actions Dropdown */}
        <Dropdown overlay={moreMenu} trigger={['click']}>
          <Tooltip title={t('chat.more_actions')}>
            <Button
              icon={<MoreOutlined />}
              disabled={disabled || isLoading}
              size="small"
            />
          </Tooltip>
        </Dropdown>

        {/* Hidden file input for import */}
        <input
          id="import-input"
          type="file"
          accept=".json,.txt,.md"
          style={{ display: 'none' }}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              handleImport(file);
            }
          }}
        />
      </Space>

      {/* Settings Modal */}
      <Modal
        title={t('chat.settings')}
        open={settingsModalVisible}
        onCancel={() => setSettingsModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={settings}
          onFinish={handleSettingsSubmit}
        >
          <Form.Item
            name="model"
            label={t('chat.model')}
            rules={[{ required: true, message: t('chat.model_required') }]}
          >
            <Select>
              <Option value="gpt-3.5-turbo">GPT-3.5 Turbo</Option>
              <Option value="gpt-4">GPT-4</Option>
              <Option value="gpt-4-turbo">GPT-4 Turbo</Option>
              <Option value="claude-3-sonnet">Claude 3 Sonnet</Option>
              <Option value="claude-3-opus">Claude 3 Opus</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="temperature"
            label={t('chat.temperature')}
            rules={[{ required: true, message: t('chat.temperature_required') }]}
          >
            <InputNumber
              min={0}
              max={2}
              step={0.1}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="max_tokens"
            label={t('chat.max_tokens')}
            rules={[{ required: true, message: t('chat.max_tokens_required') }]}
          >
            <InputNumber
              min={1}
              max={8192}
              step={1}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="use_knowledge_base"
            label={t('chat.use_knowledge_base')}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="use_tools"
            label={t('chat.use_tools')}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="system_prompt"
            label={t('chat.system_prompt')}
          >
            <Input.TextArea
              rows={4}
              placeholder={t('chat.system_prompt_placeholder')}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {t('common.save')}
              </Button>
              <Button onClick={() => setSettingsModalVisible(false)}>
                {t('common.cancel')}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Export Modal */}
      <Modal
        title={t('chat.export_options')}
        open={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        footer={null}
        width={400}
      >
        <Form
          layout="vertical"
          onFinish={handleExportSubmit}
          initialValues={{
            format: 'json',
            include_metadata: true,
            include_sources: true,
          }}
        >
          <Form.Item
            name="format"
            label={t('chat.export_format')}
            rules={[{ required: true, message: t('chat.format_required') }]}
          >
            <Select>
              <Option value="json">JSON</Option>
              <Option value="txt">Plain Text</Option>
              <Option value="md">Markdown</Option>
              <Option value="pdf">PDF</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="include_metadata"
            label={t('chat.include_metadata')}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="include_sources"
            label={t('chat.include_sources')}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {t('chat.export')}
              </Button>
              <Button onClick={() => setExportModalVisible(false)}>
                {t('common.cancel')}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ChatToolbar;