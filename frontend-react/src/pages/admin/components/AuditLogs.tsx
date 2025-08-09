import React from 'react';
import {
  Table,
  Tag,
  Space,
  Button,
  Tooltip,
  Popconfirm,
} from 'antd';
import {
  DownloadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useAuditLogs } from '../hooks/useAuditLogs';
import { AuditLog } from '../types/admin.types';
import ModernCard from '../../../components/ModernCard';
import ModernButton from '../../../components/ModernButton';

const AuditLogs: React.FC = () => {
  const { t } = useTranslation();
  const {
    auditLogs,
    loading,
    pagination,
    handleTableChange,
    exportLogs,
    clearLogs,
  } = useAuditLogs();

  const getStatusColor = (status: string) => {
    return status === 'success' ? 'green' : 'red';
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'CREATE':
        return 'blue';
      case 'UPDATE':
        return 'orange';
      case 'DELETE':
        return 'red';
      case 'LOGIN':
        return 'green';
      case 'LOGOUT':
        return 'purple';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const columns = [
    {
      title: t('admin.audit.timestamp'),
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => formatDate(timestamp),
      sorter: (a: AuditLog, b: AuditLog) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      defaultSortOrder: 'descend' as const,
    },
    {
      title: t('admin.audit.user'),
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: AuditLog) => (
        <Space>
          <span>{username}</span>
          <Tag size="small">ID: {record.userId}</Tag>
        </Space>
      ),
    },
    {
      title: t('admin.audit.action'),
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => (
        <Tag color={getActionColor(action)}>{action}</Tag>
      ),
      filters: [
        { text: 'CREATE', value: 'CREATE' },
        { text: 'UPDATE', value: 'UPDATE' },
        { text: 'DELETE', value: 'DELETE' },
        { text: 'LOGIN', value: 'LOGIN' },
        { text: 'LOGOUT', value: 'LOGOUT' },
      ],
      onFilter: (value: string, record: AuditLog) => record.action === value,
    },
    {
      title: t('admin.audit.resource'),
      dataIndex: 'resource',
      key: 'resource',
      render: (resource: string) => (
        <Tag color="blue">{resource}</Tag>
      ),
    },
    {
      title: t('admin.audit.details'),
      dataIndex: 'details',
      key: 'details',
      ellipsis: true,
      render: (details: string) => (
        <Tooltip title={details}>
          <span>{details}</span>
        </Tooltip>
      ),
    },
    {
      title: t('admin.audit.ip_address'),
      dataIndex: 'ipAddress',
      key: 'ipAddress',
      render: (ipAddress: string) => (
        <Tag color="geekblue">{ipAddress}</Tag>
      ),
    },
    {
      title: t('admin.audit.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'Success', value: 'success' },
        { text: 'Failed', value: 'failed' },
      ],
      onFilter: (value: string, record: AuditLog) => record.status === value,
    },
    {
      title: t('admin.audit.actions'),
      key: 'actions',
      width: 80,
      render: (record: AuditLog) => (
        <Space size="small">
          <Tooltip title={t('admin.audit.view_details')}>
            <Button
              type="text"
              icon={<EyeOutlined />}
              size="small"
              onClick={() => console.log('View details:', record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <ModernCard
        title={t('admin.audit.title')}
        extra={
          <Space>
            <ModernButton
              icon={<ReloadOutlined />}
              onClick={() => handleTableChange(pagination)}
              loading={loading}
            >
              {t('common.refresh')}
            </ModernButton>
            <ModernButton
              icon={<DownloadOutlined />}
              onClick={exportLogs}
            >
              {t('admin.audit.export')}
            </ModernButton>
            <Popconfirm
              title={t('admin.audit.clear_confirm')}
              onConfirm={clearLogs}
              okText={t('common.yes')}
              cancelText={t('common.no')}
            >
              <ModernButton
                danger
                icon={<DeleteOutlined />}
              >
                {t('admin.audit.clear')}
              </ModernButton>
            </Popconfirm>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={auditLogs}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${t('admin.audit.showing')} ${range[0]}-${range[1]} ${t('admin.audit.of')} ${total} ${t('admin.audit.entries')}`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </ModernCard>
    </div>
  );
};

export default AuditLogs;