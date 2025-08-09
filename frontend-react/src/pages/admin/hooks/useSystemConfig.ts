import { useState, useCallback, useEffect } from 'react';
import { message } from 'antd';
import { SystemConfig, SystemConfigFormData } from '../types/admin.types';

export const useSystemConfig = () => {
  const [systemConfig, setSystemConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);

  const loadSystemConfig = useCallback(async () => {
    setLoading(true);
    try {
      // Mock data for now - replace with actual API call
      const mockConfig: SystemConfig = {
        defaultLanguage: 'en',
        maxFileSize: 10 * 1024 * 1024, // 10MB
        maxUsers: 1000,
        enableRegistration: true,
        enableEmailVerification: true,
        maintenanceMode: false,
        debugMode: false,
      };
      setSystemConfig(mockConfig);
    } catch (error) {
      message.error('Failed to load system configuration');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleConfigChange = useCallback(async (key: keyof SystemConfig, value: any) => {
    try {
      if (systemConfig) {
        const updatedConfig = { ...systemConfig, [key]: value };
        setSystemConfig(updatedConfig);
        
        // Mock API call - replace with actual API call
        console.log('Updating config:', key, value);
        
        message.success('Configuration updated successfully');
      }
    } catch (error) {
      message.error('Failed to update configuration');
    }
  }, [systemConfig]);

  const handleConfigSave = useCallback(async (configData: SystemConfigFormData) => {
    try {
      setSystemConfig(configData);
      setConfigModalVisible(false);
      message.success('System configuration saved successfully');
    } catch (error) {
      message.error('Failed to save system configuration');
    }
  }, []);

  const openConfigModal = useCallback(() => {
    setConfigModalVisible(true);
  }, []);

  const closeConfigModal = useCallback(() => {
    setConfigModalVisible(false);
  }, []);

  useEffect(() => {
    loadSystemConfig();
  }, [loadSystemConfig]);

  return {
    systemConfig,
    loading,
    configModalVisible,
    loadSystemConfig,
    handleConfigChange,
    handleConfigSave,
    openConfigModal,
    closeConfigModal,
  };
};