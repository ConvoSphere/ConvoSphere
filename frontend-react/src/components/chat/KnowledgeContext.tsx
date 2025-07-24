import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  Input,
  List,
  Button,
  Switch,
  Tag,
  Typography,
  Space,
  Divider,
  Empty,
  Spin,
  Tooltip,
  Badge,
  Select,
  DatePicker,
  Row,
  Col,
  message
} from 'antd';
import {
  SearchOutlined,
  BookOutlined,
  FileTextOutlined,
  TagOutlined,
  FilterOutlined,
  ClearOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import type { Document, Tag as TagType } from '../services/knowledge';
import { useKnowledgeStore } from '../../store/knowledgeStore';
import { formatFileSize, formatDate, formatDocumentType } from '../../utils/formatters';

const { Text, Title } = Typography;
const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface KnowledgeContextProps {
  onDocumentSelect: (document: Document) => void;
  onSearch: (query: string) => Promise<Document[]>;
  selectedDocuments: Document[];
  searchResults: Document[];
  onToggleContext: (enabled: boolean) => void;
  contextEnabled: boolean;
}

const KnowledgeContext: React.FC<KnowledgeContextProps> = ({
  onDocumentSelect,
  onSearch,
  selectedDocuments,
  searchResults,
  onToggleContext,
  contextEnabled
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [debouncedQuery, setDebouncedQuery] = useState('');

  const { tags, documentTypes, getTags, getDocuments } = useKnowledgeStore();

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Auto-search when query changes
  useEffect(() => {
    if (debouncedQuery.trim()) {
      handleSearch(debouncedQuery);
    }
  }, [debouncedQuery]);

  // Load tags and document types on mount
  useEffect(() => {
    getTags();
  }, [getTags]);

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    try {
      await onSearch(query);
    } catch (error) {
      message.error('Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  const handleDocumentClick = (document: Document) => {
    onDocumentSelect(document);
  };

  const isDocumentSelected = (document: Document) => {
    return selectedDocuments.some(doc => doc.id === document.id);
  };

  const clearFilters = () => {
    setSelectedTags([]);
    setSelectedTypes([]);
    setDateRange(null);
    setSearchQuery('');
  };

  const getFilteredDocuments = useMemo(() => {
    let filtered = searchResults;

    if (selectedTags.length > 0) {
      filtered = filtered.filter(doc => 
        doc.tags?.some(tag => selectedTags.includes(tag.name))
      );
    }

    if (selectedTypes.length > 0) {
      filtered = filtered.filter(doc => 
        selectedTypes.includes(doc.document_type)
      );
    }

    if (dateRange) {
      const [startDate, endDate] = dateRange;
      filtered = filtered.filter(doc => {
        const docDate = new Date(doc.created_at);
        return docDate >= new Date(startDate) && docDate <= new Date(endDate);
      });
    }

    return filtered;
  }, [searchResults, selectedTags, selectedTypes, dateRange]);

  const renderDocumentItem = (document: Document) => {
    const isSelected = isDocumentSelected(document);
    
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
                <Tag color="blue">
                  {formatDocumentType(document.document_type)}
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

              {document.tags && document.tags.length > 0 && (
                <div style={{ marginTop: '4px' }}>
                  {document.tags.slice(0, 2).map(tag => (
                    <Tag key={tag.id} color="purple">
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

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <Title level={5} style={{ margin: 0 }}>
            <BookOutlined /> Knowledge Context
          </Title>
          <Switch
            checked={contextEnabled}
            onChange={onToggleContext}
            size="small"
          />
        </div>
        
        {contextEnabled && (
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {selectedDocuments.length} document(s) selected for context
          </Text>
        )}
      </div>

      {!contextEnabled ? (
        <Empty
          description="Enable Knowledge Base to search and select documents for chat context"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      ) : (
        <>
          {/* Search */}
          <div style={{ marginBottom: '16px' }}>
            <Search
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={handleSearch}
              loading={isSearching}
              enterButton={<SearchOutlined />}
              size="small"
            />
          </div>

          {/* Filters */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Button
                type="text"
                size="small"
                icon={<FilterOutlined />}
                onClick={() => setShowFilters(!showFilters)}
              >
                Filters
              </Button>
              {(selectedTags.length > 0 || selectedTypes.length > 0 || dateRange) && (
                <Button
                  type="text"
                  size="small"
                  icon={<ClearOutlined />}
                  onClick={clearFilters}
                >
                  Clear
                </Button>
              )}
            </div>

            {showFilters && (
              <div style={{ marginTop: '8px', padding: '12px', backgroundColor: '#fafafa', borderRadius: '6px' }}>
                <Row gutter={[8, 8]}>
                  <Col span={12}>
                    <Text strong style={{ fontSize: '12px' }}>Tags:</Text>
                    <Select
                      mode="multiple"
                      placeholder="Select tags"
                      value={selectedTags}
                      onChange={setSelectedTags}
                      size="small"
                      style={{ width: '100%', marginTop: '4px' }}
                      maxTagCount={2}
                    >
                      {tags.map(tag => (
                        <Option key={tag.id} value={tag.name}>
                          {tag.name}
                        </Option>
                      ))}
                    </Select>
                  </Col>
                  <Col span={12}>
                    <Text strong style={{ fontSize: '12px' }}>Types:</Text>
                    <Select
                      mode="multiple"
                      placeholder="Select types"
                      value={selectedTypes}
                      onChange={setSelectedTypes}
                      size="small"
                      style={{ width: '100%', marginTop: '4px' }}
                      maxTagCount={2}
                    >
                      {documentTypes.map(type => (
                        <Option key={type} value={type}>
                          {formatDocumentType(type)}
                        </Option>
                      ))}
                    </Select>
                  </Col>
                  <Col span={24}>
                    <Text strong style={{ fontSize: '12px' }}>Date Range:</Text>
                    <RangePicker
                      size="small"
                      style={{ width: '100%', marginTop: '4px' }}
                      onChange={(dates) => {
                        if (dates) {
                          setDateRange([
                            dates[0]?.toISOString() || '',
                            dates[1]?.toISOString() || ''
                          ]);
                        } else {
                          setDateRange(null);
                        }
                      }}
                    />
                  </Col>
                </Row>
              </div>
            )}
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
                  onClick={() => selectedDocuments.forEach(doc => onDocumentSelect(doc))}
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
                        onDocumentSelect(doc);
                      }}
                    >
                      ×
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Divider style={{ margin: '8px 0' }} />

          {/* Search Results */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <Text strong style={{ fontSize: '12px' }}>
                Search Results ({getFilteredDocuments.length})
              </Text>
              {isSearching && <Spin size="small" />}
            </div>

            <div style={{ height: 'calc(100% - 30px)', overflowY: 'auto' }}>
              {getFilteredDocuments.length === 0 ? (
                <Empty
                  description={searchQuery ? "No documents found" : "Search for documents to add to context"}
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  style={{ padding: '20px 0' }}
                />
              ) : (
                <List
                  dataSource={getFilteredDocuments}
                  renderItem={renderDocumentItem}
                  size="small"
                />
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default KnowledgeContext;