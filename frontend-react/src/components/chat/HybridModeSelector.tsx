import React, { useState, useEffect } from 'react';
import { Select, Tooltip, Badge, Space, Button, Modal, message } from 'antd';
import { 
  MessageOutlined, 
  RobotOutlined, 
  ThunderboltOutlined, 
  SettingOutlined,
  InfoCircleOutlined 
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

interface HybridModeSelectorProps {
  conversationId: string;
  currentMode: string;
  onModeChange: (mode: string) => void;
  disabled?: boolean;
  className?: string;
}

interface ModeInfo {
  value: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  features: string[];
  color: string;
}

const HybridModeSelector: React.FC<HybridModeSelectorProps> = ({
  conversationId,
  currentMode,
  onModeChange,
  disabled = false,
  className = '',
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [modeInfo, setModeInfo] = useState<ModeInfo[]>([]);

  useEffect(() => {
    fetchAvailableModes();
  }, []);

  const fetchAvailableModes = async () => {
    try {
      const response = await fetch('/api/v1/hybrid-mode/modes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        const modes: ModeInfo[] = data.modes.map((mode: any) => ({
          value: mode.mode,
          label: mode.name,
          icon: getModeIcon(mode.mode),
          description: mode.description,
          features: mode.features,
          color: getModeColor(mode.mode),
        }));
        setModeInfo(modes);
      }
    } catch (error) {
      console.error('Error fetching available modes:', error);
    }
  };

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'chat':
        return <MessageOutlined />;
      case 'agent':
        return <RobotOutlined />;
      case 'auto':
        return <ThunderboltOutlined />;
      default:
        return <MessageOutlined />;
    }
  };

  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'chat':
        return 'blue';
      case 'agent':
        return 'green';
      case 'auto':
        return 'purple';
      default:
        return 'default';
    }
  };

  const handleModeChange = async (newMode: string) => {
    if (newMode === currentMode) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/v1/hybrid-mode/conversations/${conversationId}/mode/change`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          target_mode: newMode,
          reason: 'User requested mode change',
          force_change: true,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        onModeChange(newMode);
        message.success(`Switched to ${getModeLabel(newMode)} mode`);
      } else {
        const error = await response.json();
        message.error(`Failed to change mode: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error changing mode:', error);
      message.error('Failed to change mode');
    } finally {
      setLoading(false);
    }
  };

  const getModeLabel = (mode: string) => {
    const modeData = modeInfo.find(m => m.value === mode);
    return modeData?.label || mode;
  };

  const getCurrentModeInfo = () => {
    return modeInfo.find(m => m.value === currentMode);
  };

  const currentModeInfo = getCurrentModeInfo();

  return (
    <div className={`hybrid-mode-selector ${className}`}>
      <Space>
        <Tooltip title={t('chat.hybridMode.selector.tooltip')}>
          <Badge 
            color={currentModeInfo?.color || 'default'}
            text={t('chat.hybridMode.selector.label')}
          />
        </Tooltip>
        
        <Select
          value={currentMode}
          onChange={handleModeChange}
          loading={loading}
          disabled={disabled}
          style={{ minWidth: 120 }}
          dropdownMatchSelectWidth={false}
        >
          {modeInfo.map((mode) => (
            <Select.Option key={mode.value} value={mode.value}>
              <Space>
                {mode.icon}
                <span>{mode.label}</span>
              </Space>
            </Select.Option>
          ))}
        </Select>

        <Tooltip title={t('chat.hybridMode.config.tooltip')}>
          <Button
            type="text"
            icon={<SettingOutlined />}
            size="small"
            onClick={() => setConfigModalVisible(true)}
            disabled={disabled}
          />
        </Tooltip>

        <Tooltip title={t('chat.hybridMode.info.tooltip')}>
          <Button
            type="text"
            icon={<InfoCircleOutlined />}
            size="small"
            onClick={() => showModeInfo()}
            disabled={disabled}
          />
        </Tooltip>
      </Space>

      {/* Configuration Modal */}
      <Modal
        title={t('chat.hybridMode.config.title')}
        open={configModalVisible}
        onCancel={() => setConfigModalVisible(false)}
        footer={null}
        width={600}
      >
        <HybridModeConfig 
          conversationId={conversationId}
          onClose={() => setConfigModalVisible(false)}
        />
      </Modal>
    </div>
  );
};

// Hybrid Mode Configuration Component
interface HybridModeConfigProps {
  conversationId: string;
  onClose: () => void;
}

const HybridModeConfig: React.FC<HybridModeConfigProps> = ({
  conversationId,
  onClose,
}) => {
  const { t } = useTranslation();
  const [config, setConfig] = useState({
    auto_mode_enabled: true,
    complexity_threshold: 0.7,
    confidence_threshold: 0.8,
    context_window_size: 10,
    memory_retention_hours: 24,
    reasoning_steps_max: 5,
    tool_relevance_threshold: 0.6,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCurrentConfig();
  }, []);

  const fetchCurrentConfig = async () => {
    try {
      const response = await fetch(`/api/v1/hybrid-mode/conversations/${conversationId}/mode/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.config) {
          setConfig(data.config);
        }
      }
    } catch (error) {
      console.error('Error fetching config:', error);
    }
  };

  const handleConfigUpdate = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/hybrid-mode/conversations/${conversationId}/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        message.success(t('chat.hybridMode.config.success'));
        onClose();
      } else {
        const error = await response.json();
        message.error(`Failed to update config: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error updating config:', error);
      message.error('Failed to update configuration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hybrid-mode-config">
      <div className="config-section">
        <h4>{t('chat.hybridMode.config.general')}</h4>
        <div className="config-item">
          <label>
            <input
              type="checkbox"
              checked={config.auto_mode_enabled}
              onChange={(e) => setConfig({ ...config, auto_mode_enabled: e.target.checked })}
            />
            {t('chat.hybridMode.config.autoMode')}
          </label>
        </div>
      </div>

      <div className="config-section">
        <h4>{t('chat.hybridMode.config.thresholds')}</h4>
        <div className="config-item">
          <label>{t('chat.hybridMode.config.complexityThreshold')}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={config.complexity_threshold}
            onChange={(e) => setConfig({ ...config, complexity_threshold: parseFloat(e.target.value) })}
          />
          <span>{config.complexity_threshold}</span>
        </div>
        
        <div className="config-item">
          <label>{t('chat.hybridMode.config.confidenceThreshold')}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={config.confidence_threshold}
            onChange={(e) => setConfig({ ...config, confidence_threshold: parseFloat(e.target.value) })}
          />
          <span>{config.confidence_threshold}</span>
        </div>
      </div>

      <div className="config-actions">
        <Button onClick={onClose}>{t('common.cancel')}</Button>
        <Button type="primary" onClick={handleConfigUpdate} loading={loading}>
          {t('common.save')}
        </Button>
      </div>
    </div>
  );
};

const showModeInfo = () => {
  Modal.info({
    title: 'Hybrid Mode Information',
    content: (
      <div>
        <h4>Chat Mode</h4>
        <p>Direct conversational responses without tool usage. Best for simple questions and casual conversation.</p>
        
        <h4>Agent Mode</h4>
        <p>Tool-enabled responses with reasoning and actions. Best for complex tasks requiring external tools or step-by-step analysis.</p>
        
        <h4>Auto Mode</h4>
        <p>Automatic mode switching based on query analysis. The system intelligently chooses the best mode for each message.</p>
      </div>
    ),
    width: 600,
  });
};

export default HybridModeSelector; 