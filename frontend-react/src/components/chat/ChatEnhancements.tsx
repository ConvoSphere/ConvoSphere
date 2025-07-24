import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  List,
  Tag,
  Typography,
  Space,
  Tooltip,
  Modal,
  Input,
  Select,
  Divider,
  Badge,
  Progress,
  message
} from 'antd';
import {
  BookOutlined,
  LinkOutlined,
  BulbOutlined,
  SettingOutlined,
  HistoryOutlined,
  StarOutlined,
  ShareAltOutlined,
  ExportOutlined
} from '@ant-design/icons';
import { Document } from '../../services/knowledge';
import { formatDate, formatFileSize, formatDocumentType } from '../../utils/formatters';

const { Text, Title } = Typography;
const { Option } = Select;

interface ChatEnhancementsProps {
  documents: Document[];
  onDocumentSelect: (document: Document) => void;
  onExportConversation: () => void;
  onShareConversation: () => void;
  conversationHistory: any[];
  selectedDocuments: Document[];
}

const ChatEnhancements: React.FC<ChatEnhancementsProps> = ({
  documents,
  onDocumentSelect,
  onExportConversation,
  onShareConversation,
  conversationHistory,
  selectedDocuments
}) => {
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>(documents);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = documents.filter(doc =>
        doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.tags?.some(tag => tag.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
        doc.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredDocuments(filtered);
    } else {
      setFilteredDocuments(documents);
    }
  }, [documents, searchQuery]);

  const handleDocumentClick = (document: Document) => {
    setSelectedDocument(document);
    setShowDocumentModal(true);
  };

  const handleDocumentSelect = (document: Document) => {
    onDocumentSelect(document);
    setShowDocumentModal(false);
  };

  const renderDocumentItem = (document: Document) => {
    const isSelected = selectedDocuments.some(doc => doc.id === document.id);
    
    return (
      <List.Item
        key={document.id}
        style={{
          padding: '8px 12px',
          border: isSelected ? '2px solid #1890ff' : '1px solid #f0f0f0',
          borderRadius: '6px',
          marginBottom: '8px',
          cursor: 'pointer',
          backgroundColor: isSelected ? '#f6ffed' : 'white',
          transition: 'all 0.2s'
        }}
        onClick={() => handleDocumentClick(document)}
      >
        <div style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <Text strong style={{ 
                fontSize: '13px', 
                display: 'block',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                {document.title}
              </Text>
              
              <div style={{ marginTop: '4px' }}>
                <Tag size="small" color="blue">
                  {formatDocumentType(document.document_type)}
                </Tag>
                {document.language && (
                  <Tag size="small" color="green">
                    {document.language.toUpperCase()}
                  </Tag>
                )}
              </div>

              {document.tags && document.tags.length > 0 && (
                <div style={{ marginTop: '4px' }}>
                  {document.tags.slice(0, 2).map(tag => (
                    <Tag key={tag.id} size="small" color="purple">
                      {tag.name}
                    </Tag>
                  ))}
                  {document.tags.length > 2 && (
                    <Text type="secondary" style={{ fontSize: '10px' }}>
                      +{document.tags.length - 2} more
                    </Text>
                  )}
                </div>
              )}

              <div style={{ marginTop: '4px' }}>
                <Text type="secondary" style={{ fontSize: '11px' }}>
                  {formatFileSize(document.file_size)} • {formatDate(document.created_at)}
                </Text>
              </div>
            </div>

            {isSelected && (
              <Badge status="success" />
            )}
          </div>
        </div>
      </List.Item>
    );
  };

  const renderSmartSuggestions = () => {
    const suggestions = [
      {
        title: "Summarize selected documents",
        description: "Get a concise summary of all selected documents",
        icon: <BookOutlined />,
        action: () => message.info("Summarize feature coming soon")
      },
      {
        title: "Find related documents",
        description: "Discover documents similar to your selection",
        icon: <LinkOutlined />,
        action: () => message.info("Related documents feature coming soon")
      },
      {
        title: "Generate questions",
        description: "Create questions based on document content",
        icon: <BulbOutlined />,
        action: () => message.info("Question generation feature coming soon")
      }
    ];

    return (
      <Card size="small" title="Smart Suggestions" style={{ marginBottom: '16px' }}>
        <List
          size="small"
          dataSource={suggestions}
          renderItem={(suggestion) => (
            <List.Item
              style={{ padding: '8px 0', cursor: 'pointer' }}
              onClick={suggestion.action}
            >
              <List.Item.Meta
                avatar={suggestion.icon}
                title={
                  <Text style={{ fontSize: '13px', cursor: 'pointer' }}>
                    {suggestion.title}
                  </Text>
                }
                description={
                  <Text type="secondary" style={{ fontSize: '11px' }}>
                    {suggestion.description}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    );
  };

  const renderQuickActions = () => (
    <Card size="small" title="Quick Actions" style={{ marginBottom: '16px' }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Button
          type="text"
          icon={<HistoryOutlined />}
          onClick={() => setShowHistory(true)}
          style={{ textAlign: 'left', width: '100%' }}
        >
          View Conversation History
        </Button>
        <Button
          type="text"
          icon={<ExportOutlined />}
          onClick={onExportConversation}
          style={{ textAlign: 'left', width: '100%' }}
        >
          Export Conversation
        </Button>
        <Button
          type="text"
          icon={<ShareAltOutlined />}
          onClick={onShareConversation}
          style={{ textAlign: 'left', width: '100%' }}
        >
          Share Conversation
        </Button>
        <Button
          type="text"
          icon={<SettingOutlined />}
          onClick={() => setShowSettings(true)}
          style={{ textAlign: 'left', width: '100%' }}
        >
          Chat Settings
        </Button>
      </Space>
    </Card>
  );

  return (
    <div>
      {/* Smart Suggestions */}
      {selectedDocuments.length > 0 && renderSmartSuggestions()}

      {/* Quick Actions */}
      {renderQuickActions()}

      {/* Document References */}
      {documents.length > 0 && (
        <Card 
          size="small" 
          title={
            <Space>
              <BookOutlined />
              <span>Document References ({documents.length})</span>
            </Space>
          }
          extra={
            <Input.Search
              placeholder="Search documents..."
              size="small"
              style={{ width: 200 }}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          }
        >
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {filteredDocuments.length === 0 ? (
              <Text type="secondary">No documents found</Text>
            ) : (
              <List
                dataSource={filteredDocuments}
                renderItem={renderDocumentItem}
                size="small"
              />
            )}
          </div>
        </Card>
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
                <Text strong>Type:</Text> {formatDocumentType(selectedDocument.document_type)}
              </div>
              {selectedDocument.author && (
                <div>
                  <Text strong>Author:</Text> {selectedDocument.author}
                </div>
              )}
              {selectedDocument.language && (
                <div>
                  <Text strong>Language:</Text> {selectedDocument.language}
                </div>
              )}
              {selectedDocument.year && (
                <div>
                  <Text strong>Year:</Text> {selectedDocument.year}
                </div>
              )}
              {selectedDocument.page_count && (
                <div>
                  <Text strong>Pages:</Text> {selectedDocument.page_count}
                </div>
              )}
              
              {selectedDocument.description && (
                <div>
                  <Text strong>Description:</Text>
                  <p>{selectedDocument.description}</p>
                </div>
              )}
              
              {selectedDocument.tags && selectedDocument.tags.length > 0 && (
                <div>
                  <Text strong>Tags:</Text>
                  <div style={{ marginTop: 8 }}>
                    {selectedDocument.tags.map(tag => (
                      <Tag key={tag.id} color="blue">{tag.name}</Tag>
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

              <div>
                <Text strong>File Size:</Text> {formatFileSize(selectedDocument.file_size)}
              </div>
              <div>
                <Text strong>Created:</Text> {formatDate(selectedDocument.created_at)}
              </div>
            </Space>
          </div>
        )}
      </Modal>

      {/* Settings Modal */}
      <Modal
        title="Chat Settings"
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
            <Text strong>Knowledge Base Integration:</Text>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Configure how the Knowledge Base integrates with your chat experience.
              </Text>
            </div>
          </div>
          
          <div>
            <Text strong>Auto-Search:</Text>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Automatically search for relevant documents when you type messages.
              </Text>
            </div>
          </div>
          
          <div>
            <Text strong>Context Management:</Text>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                Choose how many documents to include in the chat context and how to prioritize them.
              </Text>
            </div>
          </div>
        </Space>
      </Modal>

      {/* History Modal */}
      <Modal
        title="Conversation History"
        open={showHistory}
        onCancel={() => setShowHistory(false)}
        footer={[
          <Button key="close" onClick={() => setShowHistory(false)}>
            Close
          </Button>
        ]}
        width={800}
      >
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {conversationHistory.length === 0 ? (
            <Text type="secondary">No conversation history available</Text>
          ) : (
            <List
              dataSource={conversationHistory}
              renderItem={(item, index) => (
                <List.Item>
                  <List.Item.Meta
                    title={`Message ${index + 1}`}
                    description={
                      <div>
                        <Text type="secondary">{item.timestamp}</Text>
                        <br />
                        <Text>{item.content}</Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      </Modal>
    </div>
  );
};

export default ChatEnhancements;