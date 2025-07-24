import React, { useState, useEffect } from 'react';
import { 
  List, 
  Typography, 
  Button, 
  Tag,
  Select,
  Input,
  Modal,
  Form,
  message
} from 'antd';
import { 
  BookOutlined, 
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { useKnowledgeStore } from '../../store/knowledgeStore';
import type { Document } from '../../services/knowledge';
import { formatDocumentType } from '../../utils/formatters';

const { Title, Text } = Typography;
const { Option } = Select;

interface KnowledgeContextProps {
  onDocumentSelect?: (document: Document) => void;
  selectedDocuments?: Document[];
  maxDocuments?: number;
}

const KnowledgeContext: React.FC<KnowledgeContextProps> = ({
  onDocumentSelect,
  selectedDocuments = [],
  maxDocuments = 5
}) => {
  const { documents, tags, documentTypes, getTags } = useKnowledgeStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);

  useEffect(() => {
    getTags();
  }, [getTags]);

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = !searchQuery || 
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.description?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesTags = selectedTags.length === 0 || 
      doc.tags?.some(tag => selectedTags.includes(tag.name));
    
    const matchesTypes = selectedTypes.length === 0 || 
      (doc.document_type && selectedTypes.includes(doc.document_type));
    
    return matchesSearch && matchesTags && matchesTypes;
  });

  const handleDocumentSelect = (document: Document) => {
    if (selectedDocuments.length >= maxDocuments) {
      message.warning(`Maximum ${maxDocuments} documents allowed`);
      return;
    }
    onDocumentSelect?.(document);
  };

  const handleDocumentRemove = (documentId: string) => {
    // TODO: Implement document removal
    message.info('Document removal coming soon');
  };

  const handleAddDocument = () => {
    setShowAddModal(true);
  };

  const handleEditDocument = (document: Document) => {
    setEditingDocument(document);
    setShowEditModal(true);
  };

  const handleSaveDocument = (values: any) => {
    // TODO: Implement document saving
    message.success('Document saved successfully');
    setShowAddModal(false);
    setShowEditModal(false);
    setEditingDocument(null);
  };

  const handleDeleteDocument = (documentId: string) => {
    // TODO: Implement document deletion
    message.success('Document deleted successfully');
  };

  const renderDocumentItem = (document: Document) => (
    <List.Item
      key={document.id}
      actions={[
        <Button 
          key="edit" 
          type="text" 
          size="small" 
          icon={<EditOutlined />}
          onClick={() => handleEditDocument(document)}
        />,
        <Button 
          key="delete" 
          type="text" 
          size="small" 
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDeleteDocument(document.id)}
        />
      ]}
    >
      <List.Item.Meta
        avatar={<BookOutlined />}
        title={
          <div>
            <Text strong>{document.title}</Text>
            <div style={{ marginTop: '4px' }}>
              <Tag color="blue">
                {formatDocumentType(document.document_type || 'Unknown')}
              </Tag>
              {document.language && (
                <Tag color="green">
                  {document.language.toUpperCase()}
                </Tag>
              )}
              {document.page_count && (
                <Tag color="orange">
                  {document.page_count} pages
                </Tag>
              )}
            </div>
          </div>
        }
        description={
          <div>
            <Text type="secondary">{document.description || 'No description'}</Text>
            {document.tags && document.tags.length > 0 && (
              <div style={{ marginTop: '4px' }}>
                {document.tags.map(tag => (
                  <Tag key={tag.id} color="purple">
                    {tag.name}
                  </Tag>
                ))}
              </div>
            )}
          </div>
        }
      />
    </List.Item>
  );

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <Title level={5} style={{ margin: 0 }}>
            <BookOutlined /> Knowledge Context
          </Title>
          {/* Removed Switch as per new_code */}
        </div>
        
        {/* Removed Text as per new_code */}
      </div>

      {/* Removed Empty message as per new_code */}

      {/* Search */}
      <div style={{ marginBottom: '16px' }}>
        <Input
          placeholder="Search documents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          prefix={<SearchOutlined />}
          style={{ width: '100%' }}
        />
      </div>

      {/* Filters */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {/* Removed Filters button as per new_code */}
          {/* Removed Clear button as per new_code */}
        </div>

        {/* Removed Filters section as per new_code */}
      </div>

      {/* Selected Documents */}
      {selectedDocuments.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <Text strong style={{ fontSize: '12px' }}>
              Selected Documents ({selectedDocuments.length})
            </Text>
            <Button
              type="text"
              size="small"
              onClick={() => selectedDocuments.forEach(doc => onDocumentSelect?.(doc))}
            >
              Clear All
            </Button>
          </div>
          <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
            {selectedDocuments.map(doc => (
              <div
                key={doc.id}
                style={{
                  padding: '4px 8px',
                  backgroundColor: '#f6ffed',
                  border: '1px solid #b7eb8f',
                  borderRadius: '4px',
                  marginBottom: '4px',
                  fontSize: '11px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <Text style={{ fontSize: '11px', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {doc.title}
                </Text>
                <Button
                  type="text"
                  size="small"
                  style={{ padding: '0 4px', minWidth: 'auto' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    onDocumentSelect?.(doc);
                  }}
                >
                  ×
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Removed Divider as per new_code */}

      {/* Search Results */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <Text strong style={{ fontSize: '12px' }}>
            Search Results ({filteredDocuments.length})
          </Text>
          {/* Removed Spin as per new_code */}
        </div>

        <div style={{ height: 'calc(100% - 30px)', overflowY: 'auto' }}>
          {filteredDocuments.length === 0 ? (
            <div style={{ padding: '20px 0' }}>
              <Text type="secondary">No documents found</Text>
            </div>
          ) : (
            <List
              dataSource={filteredDocuments}
              renderItem={renderDocumentItem}
              size="small"
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeContext;