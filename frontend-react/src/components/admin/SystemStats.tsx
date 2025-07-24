import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Typography, 
  Table, 
  Progress, 
  Space, 
  Button, 
  DatePicker, 
  Select,
  Alert,
  Divider,
  List,
  Tag,
  Tooltip
} from 'antd';
import { 
  BarChartOutlined, 
  FileTextOutlined, 
  UserOutlined, 
  DatabaseOutlined,
  CloudOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  DownloadOutlined,
  PieChartOutlined,
  LineChartOutlined
} from '@ant-design/icons';
import { useKnowledgeStore, useStats } from '../../store/knowledgeStore';
import { KnowledgeStats, DocumentProcessingJob } from '../../services/knowledge';
import { formatFileSize, formatDate, formatRelativeTime } from '../../utils/formatters';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface SystemStatsProps {
  showDetailedStats?: boolean;
  showCharts?: boolean;
  refreshInterval?: number; // in seconds
}

const SystemStats: React.FC<SystemStatsProps> = ({
  showDetailedStats = true,
  showCharts = true,
  refreshInterval = 30
}) => {
  const { stats, loading, fetchStats } = useStats();
  const { processingJobs, fetchProcessingJobs } = useKnowledgeStore();
  
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | 'custom'>('7d');
  const [customRange, setCustomRange] = useState<[Date, Date] | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('documents');

  useEffect(() => {
    fetchStats();
    fetchProcessingJobs();
    
    if (refreshInterval > 0) {
      const interval = setInterval(() => {
        fetchStats();
        fetchProcessingJobs();
      }, refreshInterval * 1000);
      
      return () => clearInterval(interval);
    }
  }, [fetchStats, fetchProcessingJobs, refreshInterval]);

  const getStorageUsagePercentage = () => {
    if (!stats?.storage_used) return 0;
    // Assuming 1GB total storage for demo purposes
    const totalStorage = 1024 * 1024 * 1024; // 1GB
    return Math.min((stats.storage_used / totalStorage) * 100, 100);
  };

  const getProcessingStatus = () => {
    if (!processingJobs.length) return { pending: 0, running: 0, completed: 0, failed: 0 };
    
    return processingJobs.reduce((acc, job) => {
      switch (job.status) {
        case 'pending':
          acc.pending++;
          break;
        case 'running':
          acc.running++;
          break;
        case 'completed':
          acc.completed++;
          break;
        case 'failed':
          acc.failed++;
          break;
      }
      return acc;
    }, { pending: 0, running: 0, completed: 0, failed: 0 });
  };

  const getDocumentTypeDistribution = () => {
    if (!stats?.documents_by_type) return [];
    
    return Object.entries(stats.documents_by_type).map(([type, count]) => ({
      type,
      count,
      percentage: (count / stats.total_documents) * 100
    }));
  };

  const getDocumentStatusDistribution = () => {
    if (!stats?.documents_by_status) return [];
    
    return Object.entries(stats.documents_by_status).map(([status, count]) => ({
      status,
      count,
      percentage: (count / stats.total_documents) * 100
    }));
  };

  const renderMainStats = () => (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col span={6}>
        <Card>
          <Statistic
            title="Total Documents"
            value={stats?.total_documents || 0}
            prefix={<FileTextOutlined />}
            loading={loading}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="Total Chunks"
            value={stats?.total_chunks || 0}
            prefix={<DatabaseOutlined />}
            loading={loading}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="Total Tokens"
            value={stats?.total_tokens || 0}
            formatter={(value) => `${(Number(value) / 1000).toFixed(1)}K`}
            prefix={<BarChartOutlined />}
            loading={loading}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="Storage Used"
            value={stats?.storage_used || 0}
            formatter={(value) => formatFileSize(Number(value))}
            prefix={<CloudOutlined />}
            loading={loading}
          />
          <Progress 
            percent={getStorageUsagePercentage()} 
            size="small" 
            status={getStorageUsagePercentage() > 80 ? 'exception' : 'normal'}
            style={{ marginTop: 8 }}
          />
        </Card>
      </Col>
    </Row>
  );

  const renderProcessingStats = () => {
    const processingStatus = getProcessingStatus();
    const totalJobs = processingJobs.length;
    
    return (
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Pending Jobs"
              value={processingStatus.pending}
              valueStyle={{ color: '#faad14' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Running Jobs"
              value={processingStatus.running}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ReloadOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Completed Jobs"
              value={processingStatus.completed}
              valueStyle={{ color: '#52c41a' }}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Failed Jobs"
              value={processingStatus.failed}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  const renderDocumentTypeChart = () => {
    const distribution = getDocumentTypeDistribution();
    
    return (
      <Card title="Document Type Distribution" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {distribution.map((item) => (
            <div key={item.type}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text>{item.type}</Text>
                <Text strong>{item.count} ({item.percentage.toFixed(1)}%)</Text>
              </div>
              <Progress 
                percent={item.percentage} 
                size="small" 
                showInfo={false}
                strokeColor="#1890ff"
              />
            </div>
          ))}
        </Space>
      </Card>
    );
  };

  const renderDocumentStatusChart = () => {
    const distribution = getDocumentStatusDistribution();
    
    const getStatusColor = (status: string) => {
      switch (status.toLowerCase()) {
        case 'processed': return '#52c41a';
        case 'processing': return '#1890ff';
        case 'error': return '#ff4d4f';
        case 'uploaded': return '#faad14';
        default: return '#8c8c8c';
      }
    };
    
    return (
      <Card title="Document Status Distribution" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {distribution.map((item) => (
            <div key={item.status}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Tag color={getStatusColor(item.status)}>{item.status}</Tag>
                <Text strong>{item.count} ({item.percentage.toFixed(1)}%)</Text>
              </div>
              <Progress 
                percent={item.percentage} 
                size="small" 
                showInfo={false}
                strokeColor={getStatusColor(item.status)}
              />
            </div>
          ))}
        </Space>
      </Card>
    );
  };

  const renderRecentJobs = () => {
    const recentJobs = processingJobs
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10);

    const columns = [
      {
        title: 'Job Type',
        dataIndex: 'job_type',
        key: 'job_type',
        render: (type: string) => (
          <Tag color="blue">{type}</Tag>
        ),
      },
      {
        title: 'Status',
        dataIndex: 'status',
        key: 'status',
        render: (status: string) => {
          const colorMap: Record<string, string> = {
            pending: 'orange',
            running: 'blue',
            completed: 'green',
            failed: 'red'
          };
          return <Tag color={colorMap[status] || 'default'}>{status}</Tag>;
        },
      },
      {
        title: 'Progress',
        key: 'progress',
        render: (record: DocumentProcessingJob) => (
          <Progress 
            percent={record.progress} 
            size="small" 
            status={record.status === 'failed' ? 'exception' : 'normal'}
          />
        ),
      },
      {
        title: 'Created',
        dataIndex: 'created_at',
        key: 'created_at',
        render: (date: string) => formatRelativeTime(date),
      },
      {
        title: 'Actions',
        key: 'actions',
        render: (record: DocumentProcessingJob) => (
          <Space>
            {record.status === 'failed' && (
              <Button size="small" type="link">
                Retry
              </Button>
            )}
            <Button size="small" type="link">
              View
            </Button>
          </Space>
        ),
      },
    ];

    return (
      <Card title="Recent Processing Jobs" style={{ marginBottom: 16 }}>
        <Table
          columns={columns}
          dataSource={recentJobs}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>
    );
  };

  const renderSystemHealth = () => {
    const storageUsage = getStorageUsagePercentage();
    const failedJobs = getProcessingStatus().failed;
    const totalJobs = processingJobs.length;
    const failureRate = totalJobs > 0 ? (failedJobs / totalJobs) * 100 : 0;
    
    const getHealthStatus = () => {
      if (storageUsage > 90 || failureRate > 20) return 'critical';
      if (storageUsage > 70 || failureRate > 10) return 'warning';
      return 'healthy';
    };
    
    const healthStatus = getHealthStatus();
    const statusColor = healthStatus === 'critical' ? '#ff4d4f' : 
                       healthStatus === 'warning' ? '#faad14' : '#52c41a';
    
    return (
      <Card title="System Health" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>Storage Usage: </Text>
            <Text style={{ color: statusColor }}>
              {storageUsage.toFixed(1)}% ({formatFileSize(stats?.storage_used || 0)})
            </Text>
          </div>
          <div>
            <Text strong>Job Failure Rate: </Text>
            <Text style={{ color: statusColor }}>
              {failureRate.toFixed(1)}% ({failedJobs} of {totalJobs})
            </Text>
          </div>
          <div>
            <Text strong>Last Updated: </Text>
            <Text>{stats?.last_processed ? formatRelativeTime(stats.last_processed) : 'Never'}</Text>
          </div>
          
          <Alert
            message={`System Status: ${healthStatus.toUpperCase()}`}
            type={healthStatus === 'critical' ? 'error' : healthStatus === 'warning' ? 'warning' : 'success'}
            showIcon
          />
        </Space>
      </Card>
    );
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3}>System Statistics</Title>
        <Space>
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Option value="24h">Last 24 Hours</Option>
            <Option value="7d">Last 7 Days</Option>
            <Option value="30d">Last 30 Days</Option>
            <Option value="custom">Custom Range</Option>
          </Select>
          {timeRange === 'custom' && (
            <RangePicker
              value={customRange}
              onChange={(dates) => setCustomRange(dates)}
            />
          )}
          <Button 
            icon={<ReloadOutlined />} 
            onClick={() => {
              fetchStats();
              fetchProcessingJobs();
            }}
          >
            Refresh
          </Button>
          <Button 
            icon={<DownloadOutlined />}
            onClick={() => {
              // TODO: Implement export functionality
            }}
          >
            Export
          </Button>
        </Space>
      </div>

      {renderMainStats()}
      {renderProcessingStats()}
      
      <Row gutter={16}>
        <Col span={12}>
          {renderDocumentTypeChart()}
        </Col>
        <Col span={12}>
          {renderDocumentStatusChart()}
        </Col>
      </Row>
      
      <Row gutter={16}>
        <Col span={16}>
          {renderRecentJobs()}
        </Col>
        <Col span={8}>
          {renderSystemHealth()}
        </Col>
      </Row>

      {showDetailedStats && (
        <Card title="Detailed Statistics" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title="Average Documents per User"
                value={stats?.total_documents ? Math.round(stats.total_documents / 10) : 0}
                suffix="docs"
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Average Chunks per Document"
                value={stats?.total_documents && stats?.total_chunks ? 
                  Math.round(stats.total_chunks / stats.total_documents) : 0}
                suffix="chunks"
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Average Tokens per Chunk"
                value={stats?.total_chunks && stats?.total_tokens ? 
                  Math.round(stats.total_tokens / stats.total_chunks) : 0}
                suffix="tokens"
              />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
};

export default SystemStats;