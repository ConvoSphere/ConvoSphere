import React from 'react';
import { Row, Col, Card, Progress, Typography, Space, Statistic, Tooltip } from 'antd';
import { 
  DesktopOutlined, 
  HddOutlined, 
  MemoryOutlined, 
  WifiOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined 
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { SystemMetrics } from '../../services/monitoring';
import ModernCard from '../ModernCard';

const { Title, Text } = Typography;

interface SystemMetricsProps {
  data: SystemMetrics | null;
  loading?: boolean;
}

const SystemMetrics: React.FC<SystemMetricsProps> = ({ 
  data, 
  loading = false 
}) => {
  const { t } = useTranslation();

  if (!data) {
    return (
      <ModernCard>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Text type="secondary">{t('monitoring.no_system_metrics')}</Text>
        </div>
      </ModernCard>
    );
  }

  const getUsageColor = (usage: number) => {
    if (usage < 50) return '#52c41a';
    if (usage < 80) return '#faad14';
    return '#ff4d4f';
  };

  const getUsageStatus = (usage: number) => {
    if (usage < 50) return 'success';
    if (usage < 80) return 'normal';
    return 'exception';
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* CPU Metrics */}
      <ModernCard title={t('monitoring.cpu_metrics')}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.cpu_usage')}
                value={data.cpu.usage}
                suffix="%"
                valueStyle={{ color: getUsageColor(data.cpu.usage) }}
              />
              <Progress
                percent={data.cpu.usage}
                status={getUsageStatus(data.cpu.usage)}
                strokeColor={getUsageColor(data.cpu.usage)}
                showInfo={false}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.cpu_cores')}
                value={data.cpu.cores}
                prefix={<DesktopOutlined />}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.cpu_temperature')}
                value={data.cpu.temperature}
                suffix="°C"
                valueStyle={{ 
                  color: data.cpu.temperature > 80 ? '#ff4d4f' : 
                         data.cpu.temperature > 60 ? '#faad14' : '#52c41a' 
                }}
              />
            </div>
          </Col>
        </Row>
      </ModernCard>

      {/* Memory Metrics */}
      <ModernCard title={t('monitoring.memory_metrics')}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.memory_usage')}
                value={data.memory.usage}
                suffix="%"
                valueStyle={{ color: getUsageColor(data.memory.usage) }}
              />
              <Progress
                percent={data.memory.usage}
                status={getUsageStatus(data.memory.usage)}
                strokeColor={getUsageColor(data.memory.usage)}
                showInfo={false}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.memory_used')}
                value={formatBytes(data.memory.used)}
                prefix={<MemoryOutlined />}
              />
              <Text type="secondary">
                {t('monitoring.of')} {formatBytes(data.memory.total)}
              </Text>
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.memory_available')}
                value={formatBytes(data.memory.available)}
                prefix={<MemoryOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </div>
          </Col>
        </Row>
      </ModernCard>

      {/* Disk Metrics */}
      <ModernCard title={t('monitoring.disk_metrics')}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.disk_usage')}
                value={data.disk.usage}
                suffix="%"
                valueStyle={{ color: getUsageColor(data.disk.usage) }}
              />
              <Progress
                percent={data.disk.usage}
                status={getUsageStatus(data.disk.usage)}
                strokeColor={getUsageColor(data.disk.usage)}
                showInfo={false}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.disk_used')}
                value={formatBytes(data.disk.used)}
                prefix={<HddOutlined />}
              />
              <Text type="secondary">
                {t('monitoring.of')} {formatBytes(data.disk.total)}
              </Text>
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.disk_available')}
                value={formatBytes(data.disk.available)}
                prefix={<HddOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </div>
          </Col>
        </Row>
      </ModernCard>

      {/* Network Metrics */}
      <ModernCard title={t('monitoring.network_metrics')}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.network_in')}
                value={formatBytes(data.network.bytesIn)}
                prefix={<WifiOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.network_out')}
                value={formatBytes(data.network.bytesOut)}
                prefix={<WifiOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.packets_in')}
                value={data.network.packetsIn.toLocaleString()}
                prefix={<WifiOutlined />}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.packets_out')}
                value={data.network.packetsOut.toLocaleString()}
                prefix={<WifiOutlined />}
              />
            </div>
          </Col>
        </Row>
      </ModernCard>

      {/* System Info */}
      <ModernCard title={t('monitoring.system_info')}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.uptime')}
                value={formatUptime(data.uptime)}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.load_average_1m')}
                value={data.loadAverage.oneMin}
                prefix={<ThunderboltOutlined />}
                precision={2}
                valueStyle={{ 
                  color: data.loadAverage.oneMin > 2 ? '#ff4d4f' : 
                         data.loadAverage.oneMin > 1 ? '#faad14' : '#52c41a' 
                }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <div style={{ textAlign: 'center' }}>
              <Statistic
                title={t('monitoring.load_average_5m')}
                value={data.loadAverage.fiveMin}
                prefix={<ThunderboltOutlined />}
                precision={2}
                valueStyle={{ 
                  color: data.loadAverage.fiveMin > 2 ? '#ff4d4f' : 
                         data.loadAverage.fiveMin > 1 ? '#faad14' : '#52c41a' 
                }}
              />
            </div>
          </Col>
        </Row>
      </ModernCard>
    </Space>
  );
};

export default SystemMetrics;