import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Tag, 
  Space, 
  Typography, 
  List, 
  Tooltip,
  Modal,
  Select,
  Input,
  Divider,
  Alert
} from 'antd';
import { 
  BookOutlined, 
  SearchOutlined, 
  FilterOutlined,
  EyeOutlined,
  LinkOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useKnowledgeStore, useTags } from '../store/knowledgeStore';
import { Document, SearchResult } from '../services/knowledge';

const { Text, Title } = Typography;
const { Option } = Select;
const { Search } = Input;

interface KnowledgeContextProps {
  onDocumentSelect?: (document: Document) => void;
  onSearch?: (query: string) => void;
  selectedDocuments?: Document[];
  searchResults?: SearchResult[];
  onToggleContext?: (enabled: boolean) => void;
  contextEnabled?: boolean;
}

const KnowledgeContext: React.FC<KnowledgeContextProps> = ({
  onDocumentSelect,
  onSearch,
  selectedDocuments = [],
  searchResults = [],
  onToggleContext,
  contextEnabled = false
}) => {
  const { tags } = useTags();
  const { search, advancedSearch } = useKnowledgeStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      search(query);
      onSearch?.(query);
    }
  };

  const handleTagFilter = (tagNames: string[]) => {
    setSelectedTags(tagNames);
    if (tagNames.length > 0) {
      const request = {
        filters: {
          tag_names: tagNames
        },
        sort_by: 'created_at',
        sort_order: 'desc' as const,
        page: 1,
        page_size: 10
      };
      advancedSearch(request);
    }
  };

  const handleDocumentClick = (document: Document) => {
    setSelectedDocument(document);
    setShowDocumentModal(true);
  };

  const handleDocumentSelect = (document: Document) => {
    onDocumentSelect?.(document);
  };

  const renderSearchResults = () => (
    <Card size="small" title="Search Results" style={{ marginBottom: 16 }}>
      {searchResults.length > 0 ? (
        <List
          size="small"
          dataSource={searchResults}
          renderItem={(result) => (
            <List.Item
              actions={[
                <Button 
                  type="text" 
                  size="small" 
                  icon={<EyeOutlined />}
                  onClick={() => handleDocumentClick(result.document)}
                >
                  View
                </Button>,
                <Button 
                  type="text" 
                  size="small" 
                  icon={<LinkOutlined />}
                  onClick={() => handleDocumentSelect(result.document)}
                >
                  Use
                </Button>
              ]}
            >
              <List.Item.Meta
                title={
                  <Tooltip title={result.document.title}>
                    <Text ellipsis style={{ maxWidth: 200 }}>
                      {result.document.title}
                    </Text>
                  </Tooltip>
                }
                description={
                  <Space direction="vertical" size="small">
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {result.snippet}
                    </Text>
                    <Space size="small">
                      {result.document.tag_names?.slice(0, 3).map((tag, index) => (
                        <Tag key={index} size="small" color="blue">{tag}</Tag>
                      ))}
                      {result.document.tag_names && result.document.tag_names.length > 3 && (
                        <Tag size="small" color="blue">+{result.document.tag_names.length - 3}</Tag>
                      )}
                    </Space>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      ) : (
        <Text type="secondary">No search results</Text>
      )}
    </Card>
  );

  const renderSelectedDocuments = () => (
    <Card size="small" title="Selected Documents" style={{ marginBottom: 16 }}>
      {selectedDocuments.length > 0 ? (
        <List
          size="small"
          dataSource={selectedDocuments}
          renderItem={(document) => (
            <List.Item
              actions={[
                <Button 
                  type="text" 
                  size="small" 
                  danger
                  onClick={() => {
                    // Remove document from selection
                    const updated = selectedDocuments.filter(d => d.id !== document.id);
                    // This would need to be handled by the parent component
                  }}
                >
                  Remove
                </Button>
              ]}
            >
              <List.Item.Meta
                title={
                  <Tooltip title={document.title}>
                    <Text ellipsis style={{ maxWidth: 200 }}>
                      {document.title}
                    </Text>
                  </Tooltip>
                }
                description={
                  <Space size="small">
                    <Tag size="small" color="green">{document.document_type}</Tag>
                    {document.author && (
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        by {document.author}
                      </Text>
                    )}
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      ) : (
        <Text type="secondary">No documents selected</Text>
      )}
    </Card>
  );

  const renderTagFilter = () => (
    <Card size="small" title="Filter by Tags" style={{ marginBottom: 16 }}>
      <Select
        mode="multiple"
        placeholder="Select tags to filter documents"
        style={{ width: '100%' }}
        value={selectedTags}
        onChange={handleTagFilter}
        maxTagCount={3}
      >
        {tags.map(tag => (
          <Option key={tag.id} value={tag.name}>
            <Space>
              <Tag color={tag.color || 'blue'} size="small">{tag.name}</Tag>
              <Text type="secondary">({tag.usage_count})</Text>
            </Space>
          </Option>
        ))}
      </Select>
    </Card>
  );

  const renderContextToggle = () => (
    <Card size="small">
      <Space style={{ width: '100%', justifyContent: 'space-between' }}>
        <Space>
          <BookOutlined />
          <Text>Knowledge Base Context</Text>
        </Space>
        <Space>
          <Button
            type={contextEnabled ? 'primary' : 'default'}
            size="small"
            onClick={() => onToggleContext?.(!contextEnabled)}
          >
            {contextEnabled ? 'Enabled' : 'Disabled'}
          </Button>
          <Button
            type="text"
            size="small"
            icon={<SettingOutlined />}
            onClick={() => setShowSettings(true)}
          />
        </Space>
      </Space>
    </Card>
  );

  return (
    <div style={{ width: '100%' }}>
      {renderContextToggle()}
      
      {contextEnabled && (
        <>
          <Divider />
          
          <Search
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
            style={{ marginBottom: 16 }}
          />
          
          {renderTagFilter()}
          {renderSelectedDocuments()}
          {searchResults.length > 0 && renderSearchResults()}
          
          <Alert
            message="Knowledge Base Context Active"
            description="Chat responses will be enhanced with information from your selected documents."
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        </>
      )}

      {/* Document Details Modal */}
      <Modal
        title="Document Details"
        open={showDocumentModal}
        onCancel={() => setShowDocumentModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowDocumentModal(false)}>
            Close
          </Button>,
          <Button 
            key="use" 
            type="primary"
            onClick={() => {
              if (selectedDocument) {
                handleDocumentSelect(selectedDocument);
                setShowDocumentModal(false);
              }
            }}
          >
            Use in Chat
          </Button>
        ]}
        width={600}
      >
        {selectedDocument && (
          <div>
            <Title level={4}>{selectedDocument.title}</Title>
            <Text type="secondary">{selectedDocument.file_name}</Text>
            
            <Divider />
            
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Type:</Text> {selectedDocument.document_type || 'Unknown'}
              </div>
              <div>
                <Text strong>Author:</Text> {selectedDocument.author || 'Unknown'}
              </div>
              <div>
                <Text strong>Language:</Text> {selectedDocument.language || 'Unknown'}
              </div>
              <div>
                <Text strong>Year:</Text> {selectedDocument.year || 'Unknown'}
              </div>
              
              {selectedDocument.description && (
                <div>
                  <Text strong>Description:</Text>
                  <p>{selectedDocument.description}</p>
                </div>
              )}
              
              {selectedDocument.tag_names && selectedDocument.tag_names.length > 0 && (
                <div>
                  <Text strong>Tags:</Text>
                  <div style={{ marginTop: 8 }}>
                    {selectedDocument.tag_names.map((tag, index) => (
                      <Tag key={index} color="blue">{tag}</Tag>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedDocument.keywords && selectedDocument.keywords.length > 0 && (
                <div>
                  <Text strong>Keywords:</Text>
                  <div style={{ marginTop: 8 }}>
                    {selectedDocument.keywords.map((keyword, index) => (
                      <Tag key={index} size="small">{keyword}</Tag>
                    ))}
                  </div>
                </div>
              )}
            </Space>
          </div>
        )}
      </Modal>

      {/* Settings Modal */}
      <Modal
        title="Knowledge Base Settings"
        open={showSettings}
        onCancel={() => setShowSettings(false)}
        footer={[
          <Button key="close" onClick={() => setShowSettings(false)}>
            Close
          </Button>
        ]}
        width={500}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>Context Mode:</Text>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                When enabled, the AI will use information from your selected documents to provide more accurate and relevant responses.
              </Text>
            </div>
          </div>
          
          <div>
            <Text strong>Document Selection:</Text>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                You can select specific documents to include in the chat context. Only selected documents will be used for responses.
              </Text>
            </div>
          </div>
          
          <div>
            <Text strong>Search Integration:</Text>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Search your knowledge base directly from the chat to find relevant documents and include them in the conversation.
              </Text>
            </div>
          </div>
        </Space>
      </Modal>
    </div>
  );
};

export default KnowledgeContext;