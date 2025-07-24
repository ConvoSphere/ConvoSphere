import React, { useEffect, useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Space, 
  Button, 
  Input, 
  Select, 
  DatePicker, 
  Typography,
  Alert,
  Tabs,
  Statistic,
  Modal,
  message
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  UploadOutlined, 
  ReloadOutlined,
  PlusOutlined
} from '@ant-design/icons';
import { useKnowledgeStore } from '../store/knowledgeStore';
import DocumentList from '../components/knowledge/DocumentList';
import UploadArea from '../components/knowledge/UploadArea';
import TagManager from '../components/knowledge/TagManager';
import BulkActions from '../components/knowledge/BulkActions';
import SystemStats from '../components/admin/SystemStats';
import { useAuthStore } from '../store/authStore';

const { Search } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

const KnowledgeBase: React.FC = () => {
  const { user } = useAuthStore();
  const { 
    documents, 
    documentsLoading: loading, 
    documentsError: error, 
    fetchDocuments, 
    search, 
    applyFilters, 
    clearFilters,
    currentFilters,
    setFilters,
    refreshDocuments
  } = useKnowledgeStore();
  const { stats, statsLoading } = useKnowledgeStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [showUploadArea, setShowUploadArea] = useState(false);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    if (value.trim()) {
      search(value);
    } else {
      refreshDocuments();
    }
  };

  const handleApplyFilters = () => {
    applyFilters();
  };

  const handleClearFilters = () => {
    setFilters({});
    clearFilters();
  };

  const handleViewDocument = () => {
    // TODO: Implement view functionality
    message.info('View functionality coming soon');
  };

  const handleEditDocument = () => {
    // TODO: Implement edit functionality
    message.info('Edit functionality coming soon');
  };

  const handleDeleteDocument = async () => {
    try {
      // TODO: Implement delete functionality
      message.success('Document deleted successfully');
      refreshDocuments();
    } catch (error) {
      message.error('Failed to delete document');
    }
  };

  const handleDownloadDocument = () => {
    // TODO: Implement download functionality
    message.info('Download functionality coming soon');
  };

  const handleReprocessDocument = async () => {
    try {
      // TODO: Implement reprocess functionality
      message.success('Document reprocessing started');
      refreshDocuments();
    } catch (error) {
      message.error('Failed to reprocess document');
    }
  };

  const handleBulkDelete = async (documentIds: string[]) => {
    try {
      // TODO: Implement bulk delete API call
      message.success(`${documentIds.length} documents deleted successfully`);
      setSelectedRowKeys([]);
      refreshDocuments();
    } catch (error) {
      message.error('Failed to delete documents');
    }
  };

  const handleBulkTag = async (documentIds: string[]) => {
    try {
      // TODO: Implement bulk tag API call
      message.success(`Tags applied to ${documentIds.length} documents`);
      refreshDocuments();
    } catch (error) {
      message.error('Failed to apply tags');
    }
  };

  const handleBulkReprocess = async (documentIds: string[]) => {
    try {
      // TODO: Implement bulk reprocess API call
      message.success(`${documentIds.length} documents queued for reprocessing`);
      refreshDocuments();
    } catch (error) {
      message.error('Failed to queue documents for reprocessing');
    }
  };

  const handleBulkDownload = async (documentIds: string[]) => {
    try {
      // TODO: Implement bulk download API call
      message.success(`Download started for ${documentIds.length} documents`);
    } catch (error) {
      message.error('Failed to start download');
    }
  };

  const renderStats = () => (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col span={6}>
        <Card>
          <Statistic
            title="Total Documents"
            value={stats?.total_documents || 0}
            loading={statsLoading}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="Total Chunks"
            value={stats?.total_chunks || 0}
            loading={statsLoading}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="Total Tokens"
            value={stats?.total_tokens || 0}
            loading={statsLoading}
            formatter={(value) => `${(Number(value) / 1000).toFixed(1)}K`}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="Storage Used"
            value={stats?.storage_used || 0}
            loading={statsLoading}
            formatter={(value) => `${(Number(value) / 1024 / 1024).toFixed(1)} MB`}
          />
        </Card>
      </Col>
    </Row>
  );

  const renderFilters = () => (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Row gutter={16} align="middle">
        <Col span={6}>
          <Select
            placeholder="Document Type"
            allowClear
            style={{ width: '100%' }}
            value={currentFilters.document_type}
            onChange={(value) => setFilters({ ...currentFilters, document_type: value })}
          >
            <Option value="PDF">PDF</Option>
            <Option value="DOCUMENT">Word Document</Option>
            <Option value="TEXT">Text File</Option>
            <Option value="SPREADSHEET">Spreadsheet</Option>
          </Select>
        </Col>
        <Col span={6}>
          <Input
            placeholder="Author"
            value={currentFilters.author}
            onChange={(e) => setFilters({ ...currentFilters, author: e.target.value })}
          />
        </Col>
        <Col span={4}>
          <Input
            placeholder="Year"
            type="number"
            value={currentFilters.year}
            onChange={(e) => setFilters({ ...currentFilters, year: e.target.value ? parseInt(e.target.value) : undefined })}
          />
        </Col>
        <Col span={4}>
          <Select
            placeholder="Language"
            allowClear
            style={{ width: '100%' }}
            value={currentFilters.language}
            onChange={(value) => setFilters({ ...currentFilters, language: value })}
          >
            <Option value="en">English</Option>
            <Option value="de">German</Option>
            <Option value="fr">French</Option>
            <Option value="es">Spanish</Option>
          </Select>
        </Col>
        <Col span={4}>
          <Space>
            <Button 
              type="primary" 
              icon={<FilterOutlined />}
              onClick={handleApplyFilters}
            >
              Apply
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={handleClearFilters}
            >
              Clear
            </Button>
          </Space>
        </Col>
      </Row>
    </Card>
  );

  const renderActions = () => (
    <Row gutter={16} style={{ marginBottom: 16 }}>
      <Col span={12}>
        <Space>
          <Button 
            type="primary" 
            icon={<UploadOutlined />}
            onClick={() => setShowUploadArea(true)}
          >
            Upload Documents
          </Button>
          {user?.role === 'premium' && (
            <Button 
              icon={<PlusOutlined />}
              onClick={() => setShowUploadArea(true)}
            >
              Bulk Import
            </Button>
          )}
          <Button 
            icon={<ReloadOutlined />}
            onClick={refreshDocuments}
          >
            Refresh
          </Button>
        </Space>
      </Col>
      <Col span={12} style={{ textAlign: 'right' }}>
        <Space>
          {selectedRowKeys.length > 0 && (
            <>
              <Text type="secondary">
                {selectedRowKeys.length} selected
              </Text>
              <Button 
                icon={<ReloadOutlined />}
                onClick={() => setShowBulkActions(true)}
              >
                Bulk Actions
              </Button>
            </>
          )}
        </Space>
      </Col>
    </Row>
  );

  const renderSearch = () => (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Row gutter={16} align="middle">
        <Col span={16}>
          <Search
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
            size="large"
          />
        </Col>
        <Col span={8}>
          <Space>
            <Button 
              type={false ? 'primary' : 'default'}
              icon={<FilterOutlined />}
              onClick={() => {}}
            >
              Advanced Search
            </Button>
            {false && (
              <Button onClick={() => search(searchQuery)}>
                Search
              </Button>
            )}
          </Space>
        </Col>
      </Row>
    </Card>
  );

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>Knowledge Base</Title>
      
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      <Tabs defaultActiveKey="documents">
        <Tabs.TabPane tab="Documents" key="documents">
          {renderStats()}
          {renderSearch()}
          {false && renderFilters()}
          {renderActions()}
          
          <DocumentList
            documents={Array.isArray(documents) ? documents : []}
            loading={loading}
            onView={handleViewDocument}
            onEdit={handleEditDocument}
            onDelete={handleDeleteDocument}
            onDownload={handleDownloadDocument}
            onReprocess={handleReprocessDocument}
            selectedRowKeys={selectedRowKeys}
            onSelectionChange={setSelectedRowKeys}
          />
        </Tabs.TabPane>
        
        <Tabs.TabPane tab="Tags" key="tags">
          <TagManager 
            showCreateButton={user?.role === 'premium'}
            showStatistics={true}
            mode="management"
          />
        </Tabs.TabPane>
        
        {user?.role === 'admin' && (
          <Tabs.TabPane tab="Statistics" key="stats">
            <SystemStats />
          </Tabs.TabPane>
        )}
        
        {user?.role === 'admin' && (
          <Tabs.TabPane tab="Settings" key="settings">
            <Card>
              <Title level={4}>Knowledge Base Settings</Title>
              <Text type="secondary">
                Configure system settings and preferences
              </Text>
              {/* TODO: Implement Settings component */}
            </Card>
          </Tabs.TabPane>
        )}
      </Tabs>

      {/* Upload Modal */}
      <Modal
        title="Upload Documents"
        open={showUploadArea}
        onCancel={() => setShowUploadArea(false)}
        footer={null}
        width={800}
      >
        <UploadArea
          onUploadComplete={() => {
            setShowUploadArea(false);
            refreshDocuments();
          }}
          maxFiles={user?.role === 'premium' ? 50 : 10}
          maxFileSize={100 * 1024 * 1024} // 100MB
          allowedTypes={['pdf', 'doc', 'docx', 'txt', 'md', 'xls', 'xlsx', 'ppt', 'pptx']}
          showQueue={true}
        />
      </Modal>

      {/* Bulk Actions Modal */}
      <BulkActions
        visible={showBulkActions}
        onCancel={() => setShowBulkActions(false)}
        selectedDocuments={Array.isArray(documents) ? documents.filter(doc => selectedRowKeys.includes(doc.id)) : []}
        onBulkDelete={handleBulkDelete}
        onBulkTag={handleBulkTag}
        onBulkReprocess={handleBulkReprocess}
        onBulkDownload={handleBulkDownload}
      />
    </div>
  );
};

export default KnowledgeBase; 