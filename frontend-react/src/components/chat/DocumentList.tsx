import React from 'react';
import { List, Tag, Typography, Badge } from 'antd';
import type { Document } from '../../services/knowledge';
import { formatDate, formatFileSize, formatDocumentType } from '../../utils/formatters';

const { Text } = Typography;

interface DocumentListProps {
  documents: Document[];
  selectedDocuments: Document[];
  onDocumentClick: (document: Document) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, selectedDocuments, onDocumentClick }) => (
  <List
    dataSource={documents}
    renderItem={(document) => {
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
          onClick={() => onDocumentClick(document)}
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
              {isSelected && <Badge status="success" />}
            </div>
          </div>
        </List.Item>
      );
    }}
    size="small"
  />
);

export default DocumentList;