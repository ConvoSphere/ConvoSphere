import React, { useState, useEffect } from 'react';
import { Card, Input, Space, Typography } from 'antd';
import { BookOutlined } from '@ant-design/icons';
import { Document } from '../../services/knowledge';
import SmartSuggestions from './SmartSuggestions';
import QuickActions from './QuickActions';
import DocumentList from './DocumentList';
import DocumentDetailsModal from './DocumentDetailsModal';
import SettingsModal from './SettingsModal';
import HistoryModal from './HistoryModal';

const { Text } = Typography;

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

  return (
    <div>
      {/* Smart Suggestions */}
      {selectedDocuments.length > 0 && <SmartSuggestions />}

      {/* Quick Actions */}
      <QuickActions
        onShowHistory={() => setShowHistory(true)}
        onExportConversation={onExportConversation}
        onShareConversation={onShareConversation}
        onShowSettings={() => setShowSettings(true)}
      />

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
              <DocumentList
                documents={filteredDocuments}
                selectedDocuments={selectedDocuments}
                onDocumentClick={handleDocumentClick}
              />
            )}
          </div>
        </Card>
      )}

      {/* Document Details Modal */}
      <DocumentDetailsModal
        open={showDocumentModal}
        document={selectedDocument}
        onClose={() => setShowDocumentModal(false)}
        onUse={handleDocumentSelect}
      />

      {/* Settings Modal */}
      <SettingsModal
        open={showSettings}
        onClose={() => setShowSettings(false)}
      />

      {/* History Modal */}
      <HistoryModal
        open={showHistory}
        conversationHistory={conversationHistory}
        onClose={() => setShowHistory(false)}
      />
    </div>
  );
};

export default ChatEnhancements;