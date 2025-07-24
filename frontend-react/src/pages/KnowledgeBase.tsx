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
  Tag,
  Typography,
  Divider,
  Alert,
  Tabs,
  Statistic,
  Tooltip,
  Modal,
  message
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  UploadOutlined, 
  ReloadOutlined,
  PlusOutlined,
  DeleteOutlined,
  TagOutlined,
  BarChartOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useKnowledgeStore, useDocuments, useTags, useStats } from '../store/knowledgeStore';
import DocumentList from '../components/knowledge/DocumentList';
import UploadArea from '../components/knowledge/UploadArea';
import TagManager from '../components/knowledge/TagManager';
import BulkActions from '../components/knowledge/BulkActions';
import SystemStats from '../components/admin/SystemStats';
import { Document, DocumentFilter } from '../services/knowledge';
import { useAuthStore } from '../store/authStore';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

const KnowledgeBase: React.FC = () => {
  const { user } = useAuthStore();
  const { documents, loading, error } = useDocuments();
  const { tags, loading: tagsLoading } = useTags();
  const { stats, loading: statsLoading } = useStats();
  
  const {
    fetchDocuments,
    fetchTags,
    fetchStats,
    search,
    advancedSearch,
    setFilters,
    applyFilters,
    clearFilters,
    refreshDocuments,
    clearSearchResults
  } = useKnowledgeStore();

  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentFilters, setCurrentFilters] = useState<DocumentFilter>({});
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [showBulkActionsModal, setShowBulkActionsModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);

  // Check user permissions
  const isPremium = user?.role === 'premium' || user?.role === 'admin';
  const isAdmin = user?.role === 'admin';
  const isModerator = user?.role === 'moderator' || user?.role === 'admin';

  useEffect(() => {
    fetchDocuments();
    fetchTags();
    fetchStats();
  }, [fetchDocuments, fetchTags, fetchStats]);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    if (value.trim()) {
      search(value);
    } else {
      clearSearchResults();
    }
  };

  const handleAdvancedSearch = () => {
    const request = {
      query: searchQuery,
      filters: currentFilters,
      sort_by: 'created_at',
      sort_order: 'desc' as const,
      page: 1,
      page_size: 20
    };
    advancedSearch(request);
  };

  const handleFilterChange = (key: keyof DocumentFilter, value: any) => {
    const newFilters = { ...currentFilters, [key]: value };
    setCurrentFilters(newFilters);
    setFilters(newFilters);
  };

  const handleApplyFilters = () => {
    applyFilters();
  };

  const handleClearFilters = () => {
    setCurrentFilters({});
    clearFilters();
  };

  const handleViewDocument = (document: Document) => {
    setSelectedDocument(document);
    setShowDocumentModal(true);
  };

  const handleEditDocument = (document: Document) => {
    // TODO: Implement edit functionality
    message.info('Edit functionality coming soon');
  };

  const handleDeleteDocument = async (documentId: string) => {
    try {
      // TODO: Implement delete functionality
      message.success('Document deleted successfully');
      refreshDocuments();
    } catch (error) {
      message.error('Failed to delete document');
    }
  };

  const handleDownloadDocument = (document: Document) => {
    // TODO: Implement download functionality
    message.info('Download functionality coming soon');
  };

  const handleReprocessDocument = async (documentId: string) => {
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

  const handleBulkTag = async (documentIds: string[], tagNames: string[]) => {
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
            onChange={(value) => handleFilterChange('document_type', value)}
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
            onChange={(e) => handleFilterChange('author', e.target.value)}
          />
        </Col>
        <Col span={4}>
          <Input
            placeholder="Year"
            type="number"
            value={currentFilters.year}
            onChange={(e) => handleFilterChange('year', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </Col>
        <Col span={4}>
          <Select
            placeholder="Language"
            allowClear
            style={{ width: '100%' }}
            value={currentFilters.language}
            onChange={(value) => handleFilterChange('language', value)}
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
            onClick={() => setShowUploadModal(true)}
          >
            Upload Documents
          </Button>
          {isPremium && (
            <Button 
              icon={<PlusOutlined />}
              onClick={() => setShowUploadModal(true)}
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
                icon={<DeleteOutlined />}
                danger
                onClick={() => setShowBulkActionsModal(true)}
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
              type={showAdvancedSearch ? 'primary' : 'default'}
              icon={<FilterOutlined />}
              onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
            >
              Advanced Search
            </Button>
            {showAdvancedSearch && (
              <Button onClick={handleAdvancedSearch}>
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
        <TabPane tab="Documents" key="documents">
          {renderStats()}
          {renderSearch()}
          {showAdvancedSearch && renderFilters()}
          {renderActions()}
          
          <DocumentList
            documents={documents}
            loading={loading}
            onView={handleViewDocument}
            onEdit={handleEditDocument}
            onDelete={handleDeleteDocument}
            onDownload={handleDownloadDocument}
            onReprocess={handleReprocessDocument}
            selectedRowKeys={selectedRowKeys}
            onSelectionChange={setSelectedRowKeys}
          />
        </TabPane>
        
        <TabPane tab="Tags" key="tags">
          <TagManager 
            showCreateButton={isPremium}
            showStatistics={true}
            mode="management"
          />
        </TabPane>
        
        {isAdmin && (
          <TabPane tab="Statistics" key="stats">
            <SystemStats 
              showDetailedStats={true}
              showCharts={true}
              refreshInterval={30}
            />
          </TabPane>
        )}
        
        {isAdmin && (
          <TabPane tab="Settings" key="settings">
            <Card>
              <Title level={4}>Knowledge Base Settings</Title>
              <Text type="secondary">
                Configure system settings and preferences
              </Text>
              {/* TODO: Implement Settings component */}
            </Card>
          </TabPane>
        )}
      </Tabs>

      {/* Upload Modal */}
      <Modal
        title="Upload Documents"
        open={showUploadModal}
        onCancel={() => setShowUploadModal(false)}
        footer={null}
        width={800}
      >
        <UploadArea
          onUploadComplete={() => {
            setShowUploadModal(false);
            refreshDocuments();
          }}
          maxFiles={isPremium ? 50 : 10}
          maxFileSize={100 * 1024 * 1024} // 100MB
          allowedTypes={['pdf', 'doc', 'docx', 'txt', 'md', 'xls', 'xlsx', 'ppt', 'pptx']}
          showQueue={true}
        />
      </Modal>

      {/* Document Details Modal */}
      <Modal
        title="Document Details"
        open={showDocumentModal}
        onCancel={() => {
          setShowDocumentModal(false);
          setSelectedDocument(null);
        }}
        footer={[
          <Button key="close" onClick={() => setShowDocumentModal(false)}>
            Close
          </Button>,
          <Button 
            key="edit" 
            type="primary"
            onClick={() => {
              if (selectedDocument) {
                handleEditDocument(selectedDocument);
              }
            }}
          >
            Edit
          </Button>
        ]}
        width={800}
      >
        {selectedDocument && (
          <div>
            <Title level={4}>{selectedDocument.title}</Title>
            <Text type="secondary">{selectedDocument.file_name}</Text>
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>Type:</Text> {selectedDocument.document_type || 'Unknown'}
              </Col>
              <Col span={12}>
                <Text strong>Size:</Text> {(selectedDocument.file_size / 1024 / 1024).toFixed(2)} MB
              </Col>
            </Row>
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>Author:</Text> {selectedDocument.author || 'Unknown'}
              </Col>
              <Col span={12}>
                <Text strong>Language:</Text> {selectedDocument.language || 'Unknown'}
              </Col>
            </Row>
            
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>Year:</Text> {selectedDocument.year || 'Unknown'}
              </Col>
              <Col span={12}>
                <Text strong>Status:</Text> {selectedDocument.status}
              </Col>
            </Row>
            
            {selectedDocument.description && (
              <>
                <Divider />
                <Text strong>Description:</Text>
                <p>{selectedDocument.description}</p>
              </>
            )}
            
            {selectedDocument.tag_names && selectedDocument.tag_names.length > 0 && (
              <>
                <Divider />
                <Text strong>Tags:</Text>
                <div style={{ marginTop: 8 }}>
                  {selectedDocument.tag_names.map((tag, index) => (
                    <Tag key={index} color="blue">{tag}</Tag>
                  ))}
                </div>
              </>
            )}
            
            {selectedDocument.keywords && selectedDocument.keywords.length > 0 && (
              <>
                <Divider />
                <Text strong>Keywords:</Text>
                <div style={{ marginTop: 8 }}>
                  {selectedDocument.keywords.map((keyword, index) => (
                    <Tag key={index} size="small">{keyword}</Tag>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </Modal>

      {/* Bulk Actions Modal */}
      <BulkActions
        visible={showBulkActionsModal}
        onCancel={() => setShowBulkActionsModal(false)}
        selectedDocuments={documents.filter(doc => selectedRowKeys.includes(doc.id))}
        onBulkDelete={handleBulkDelete}
        onBulkTag={handleBulkTag}
        onBulkReprocess={handleBulkReprocess}
        onBulkDownload={handleBulkDownload}
      />
    </div>
  );
};

export default KnowledgeBase; 