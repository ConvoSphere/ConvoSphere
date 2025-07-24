import React from 'react';
import { Card, List, Typography, Space, Button } from 'antd';
import { BookOutlined, ExportOutlined, ShareAltOutlined } from '@ant-design/icons';
import type { Document } from '../../services/knowledge';

const { Text } = Typography;

interface ChatEnhancementsProps {
  documents: Document[];
}

const ChatEnhancements: React.FC<ChatEnhancementsProps> = ({ documents }) => {
  const handleExportConversation = () => {
    // TODO: Implement export functionality
    console.log('Export conversation');
  };

  const handleShareConversation = () => {
    // TODO: Implement share functionality
    console.log('Share conversation');
  };

  const handleDocumentSelect = (document: Document) => {
    // TODO: Implement document selection
    console.log('Select document:', document);
  };

  return (
    <Card title="Chat Enhancements" size="small" style={{ marginBottom: 16 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text strong>Available Documents:</Text>
          <List
            size="small"
            dataSource={Array.isArray(documents) ? documents.slice(0, 3) : []}
            renderItem={(document) => (
              <List.Item
                style={{ padding: '4px 0', cursor: 'pointer' }}
                onClick={() => handleDocumentSelect(document)}
              >
                <List.Item.Meta
                  avatar={<BookOutlined />}
                  title={
                    <Text style={{ fontSize: '12px' }}>
                      {document.title}
                    </Text>
                  }
                  description={
                    <Text type="secondary" style={{ fontSize: '10px' }}>
                      {document.document_type} • {document.file_size} bytes
                    </Text>
                  }
                />
              </List.Item>
            )}
          />
        </div>
        
        <Space>
          <Button 
            size="small" 
            icon={<ExportOutlined />}
            onClick={handleExportConversation}
          >
            Export
          </Button>
          <Button 
            size="small" 
            icon={<ShareAltOutlined />}
            onClick={handleShareConversation}
          >
            Share
          </Button>
        </Space>
      </Space>
    </Card>
  );
};

export default ChatEnhancements;