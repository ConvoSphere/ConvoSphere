import React, { useState, useEffect } from 'react';
import { Card, Statistic, Progress, Button, Space, Typography, Divider } from 'antd';
import { 
  DashboardOutlined, 
  ReloadOutlined, 
  CloseOutlined,
  InfoCircleOutlined 
} from '@ant-design/icons';
import { useThemeStore } from '../store/themeStore';
import performanceMonitor from '../utils/performance';
import cacheManager from '../utils/cacheManager';
import networkOptimizer from '../utils/networkOptimizer';
import workerManager from '../utils/workerManager';
import resourceOptimizer from '../utils/resourceOptimizer';
import accessibilityManager from '../utils/accessibilityManager';

const { Title, Text } = Typography;

interface PerformanceMonitorProps {
  visible?: boolean;
  onClose?: () => void;
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  visible = false,
  onClose,
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const [metrics, setMetrics] = useState<any>({});
  const [stats, setStats] = useState<any>({});
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const updateMetrics = () => {
    setMetrics(performanceMonitor.getMetrics());
    setStats({
      cache: cacheManager.getStats(),
      network: networkOptimizer.getNetworkStatus(),
      workers: workerManager.getStats(),
      resources: resourceOptimizer.getResourceStats(),
      accessibility: accessibilityManager.getAccessibilityStatus(),
    });
    setLastUpdate(new Date());
  };

  useEffect(() => {
    if (visible) {
      updateMetrics();
      const interval = setInterval(updateMetrics, 2000);
      return () => clearInterval(interval);
    }
  }, [visible]);

  if (!visible) return null;

  const cardStyle: React.CSSProperties = {
    position: 'fixed',
    top: '20px',
    right: '20px',
    width: '400px',
    maxHeight: '80vh',
    overflow: 'auto',
    backgroundColor: colors.colorBgContainer,
    border: `1px solid ${colors.colorBorder}`,
    boxShadow: colors.boxShadow,
    zIndex: 1000,
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px',
    borderBottom: `1px solid ${colors.colorBorder}`,
  };

  const contentStyle: React.CSSProperties = {
    padding: '16px',
  };

  const getMetricColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value <= thresholds.good) return colors.colorSuccess;
    if (value <= thresholds.warning) return colors.colorWarning;
    return colors.colorError;
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <Card style={cardStyle} bodyStyle={{ padding: 0 }}>
      {/* Header */}
      <div style={headerStyle}>
        <Space>
          <DashboardOutlined style={{ color: colors.colorPrimary }} />
          <Title level={5} style={{ margin: 0, color: colors.colorTextBase }}>
            Performance Monitor
          </Title>
        </Space>
        <Space>
          <Button
            type="text"
            size="small"
            icon={<ReloadOutlined />}
            onClick={updateMetrics}
            style={{ color: colors.colorTextSecondary }}
          />
          <Button
            type="text"
            size="small"
            icon={<CloseOutlined />}
            onClick={onClose}
            style={{ color: colors.colorTextSecondary }}
          />
        </Space>
      </div>

      {/* Content */}
      <div style={contentStyle}>
        {/* Web Vitals */}
        <div style={{ marginBottom: '20px' }}>
          <Title level={5} style={{ color: colors.colorTextBase, marginBottom: '12px' }}>
            Web Vitals
          </Title>
          
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            {metrics.fcp && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <Text style={{ color: colors.colorTextSecondary }}>FCP</Text>
                  <Text style={{ 
                    color: getMetricColor(metrics.fcp, { good: 1800, warning: 3000 }),
                    fontWeight: 500 
                  }}>
                    {formatTime(metrics.fcp)}
                  </Text>
                </div>
                <Progress
                  percent={Math.min((metrics.fcp / 3000) * 100, 100)}
                  strokeColor={getMetricColor(metrics.fcp, { good: 1800, warning: 3000 })}
                  showInfo={false}
                  size="small"
                />
              </div>
            )}

            {metrics.lcp && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <Text style={{ color: colors.colorTextSecondary }}>LCP</Text>
                  <Text style={{ 
                    color: getMetricColor(metrics.lcp, { good: 2500, warning: 4000 }),
                    fontWeight: 500 
                  }}>
                    {formatTime(metrics.lcp)}
                  </Text>
                </div>
                <Progress
                  percent={Math.min((metrics.lcp / 4000) * 100, 100)}
                  strokeColor={getMetricColor(metrics.lcp, { good: 2500, warning: 4000 })}
                  showInfo={false}
                  size="small"
                />
              </div>
            )}

            {metrics.cls && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <Text style={{ color: colors.colorTextSecondary }}>CLS</Text>
                  <Text style={{ 
                    color: getMetricColor(metrics.cls, { good: 0.1, warning: 0.25 }),
                    fontWeight: 500 
                  }}>
                    {metrics.cls.toFixed(3)}
                  </Text>
                </div>
                <Progress
                  percent={Math.min((metrics.cls / 0.25) * 100, 100)}
                  strokeColor={getMetricColor(metrics.cls, { good: 0.1, warning: 0.25 })}
                  showInfo={false}
                  size="small"
                />
              </div>
            )}
          </Space>
        </div>

        <Divider style={{ margin: '16px 0', borderColor: colors.colorBorder }} />

        {/* Memory Usage */}
        {metrics.jsHeapUsed && (
          <div style={{ marginBottom: '20px' }}>
            <Title level={5} style={{ color: colors.colorTextBase, marginBottom: '12px' }}>
              Memory Usage
            </Title>
            
            <Statistic
              title="Heap Used"
              value={formatBytes(metrics.jsHeapUsed)}
              valueStyle={{ 
                color: getMetricColor(metrics.jsHeapUsed / 1024 / 1024, { good: 50, warning: 100 }),
                fontSize: '16px' 
              }}
            />
          </div>
        )}

        <Divider style={{ margin: '16px 0', borderColor: colors.colorBorder }} />

        {/* Cache Stats */}
        <div style={{ marginBottom: '20px' }}>
          <Title level={5} style={{ color: colors.colorTextBase, marginBottom: '12px' }}>
            Cache Performance
          </Title>
          
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Entries</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {stats.cache?.entryCount || 0} / {stats.cache?.maxEntries || 0}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Size</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {formatBytes(stats.cache?.size || 0)}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Hit Rate</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {((stats.cache?.hitRate || 0) * 100).toFixed(1)}%
              </Text>
            </div>
          </Space>
        </div>

        <Divider style={{ margin: '16px 0', borderColor: colors.colorBorder }} />

        {/* Network Status */}
        <div style={{ marginBottom: '20px' }}>
          <Title level={5} style={{ color: colors.colorTextBase, marginBottom: '12px' }}>
            Network Status
          </Title>
          
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Status</Text>
              <Text style={{ 
                color: stats.network?.isOnline ? colors.colorSuccess : colors.colorError,
                fontWeight: 500 
              }}>
                {stats.network?.isOnline ? 'Online' : 'Offline'}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Quality</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {stats.network?.connectionQuality || 'Unknown'}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Queue</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {stats.network?.queueLength || 0}
              </Text>
            </div>
          </Space>
        </div>

        <Divider style={{ margin: '16px 0', borderColor: colors.colorBorder }} />

        {/* Worker Stats */}
        <div style={{ marginBottom: '20px' }}>
          <Title level={5} style={{ color: colors.colorTextBase, marginBottom: '12px' }}>
            Workers
          </Title>
          
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Active</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {stats.workers?.busyWorkers || 0} / {stats.workers?.totalWorkers || 0}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Tasks</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {stats.workers?.activeTasks || 0}
              </Text>
            </div>
          </Space>
        </div>

        <Divider style={{ margin: '16px 0', borderColor: colors.colorBorder }} />

        {/* Resource Stats */}
        <div style={{ marginBottom: '20px' }}>
          <Title level={5} style={{ color: colors.colorTextBase, marginBottom: '12px' }}>
            Resources
          </Title>
          
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Loaded</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {stats.resources?.loadedResources || 0}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.colorTextSecondary }}>Active Loads</Text>
              <Text style={{ color: colors.colorTextBase, fontWeight: 500 }}>
                {stats.resources?.activeLoads || 0}
              </Text>
            </div>
          </Space>
        </div>

        {/* Last Update */}
        <div style={{ 
          textAlign: 'center', 
          marginTop: '16px',
          padding: '8px',
          backgroundColor: colors.colorBgElevated,
          borderRadius: '4px'
        }}>
          <Text style={{ color: colors.colorTextSecondary, fontSize: '12px' }}>
            Last update: {lastUpdate.toLocaleTimeString()}
          </Text>
        </div>
      </div>
    </Card>
  );
};

export default PerformanceMonitor;