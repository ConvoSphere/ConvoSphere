import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Card, Spin, Alert, message, Avatar, Row, Col, Drawer, Typography, Badge, Tooltip } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined, BookOutlined, SearchOutlined, LoadingOutlined } from '@ant-design/icons';
import { chatWebSocket } from '../services/chat';
import type { ChatMessage, KnowledgeContext } from '../services/chat';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';
import { useKnowledgeStore } from '../store/knowledgeStore';
import KnowledgeContextComponent from '../components/chat/KnowledgeContext';
import type { Document } from '../services/knowledge';
import type { InputRef } from 'antd';

const { Title, Text } = Typography;

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [showKnowledgeDrawer, setShowKnowledgeDrawer] = useState(false);
  const [knowledgeContextEnabled, setKnowledgeContextEnabled] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<Document[]>([]);
  const [searchResults, setSearchResults] = useState<Document[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingTimeout, setTypingTimeout] = useState<NodeJS.Timeout | null>(null);
  
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const { searchDocuments, getDocuments } = useKnowledgeStore();
  const colors = getCurrentColors();
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<InputRef>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      chatWebSocket.connect(
        token,
        handleMessage,
        handleKnowledgeUpdate,
        handleProcessingJobUpdate
      );
    } catch {
      setError('WebSocket connection failed');
      setLoading(false);
    }
    return () => chatWebSocket.disconnect();
  }, [token]);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const handleMessage = (msg: ChatMessage) => {
    setMessages((prev) => [...prev, { ...msg, timestamp: msg.timestamp || new Date() }]);
    setLoading(false);
    setIsTyping(false);
  };

  const handleKnowledgeUpdate = (documents: Document[], searchQuery: string) => {
    setSearchResults(documents);
    // Add a system message about knowledge search
    const searchMessage: ChatMessage = {
      sender: 'System',
      text: `Found ${documents.length} relevant documents for "${searchQuery}"`,
      messageType: 'system',
      timestamp: new Date(),
      documents
    };
    setMessages((prev) => [...prev, searchMessage]);
  };

  const handleProcessingJobUpdate = (jobId: string, status: string, progress: number) => {
    // Update processing job status in knowledge store
    // This could be used to show upload progress or processing status
    console.log(`Job ${jobId}: ${status} (${progress}%)`);
  };

  const handleSend = () => {
    if (input.trim()) {
      setSending(true);
      try {
        // Create knowledge context if enabled
        const knowledgeContext: KnowledgeContext | undefined = knowledgeContextEnabled ? {
          enabled: true,
          documentIds: selectedDocuments.map(doc => doc.id),
          searchQuery: input,
          maxChunks: 5,
          filters: {
            tags: selectedDocuments.flatMap(doc => doc.tags?.map(tag => tag.name) || []),
            documentTypes: [...new Set(selectedDocuments.map(doc => doc.document_type))]
          }
        } : undefined;
        
        // Send message via WebSocket
        chatWebSocket.sendMessage(input, knowledgeContext);
        
        // Add user message to local state
        setMessages((prev) => [...prev, { 
          sender: 'You', 
          text: input, 
          timestamp: new Date() 
        }]);
        
        setInput('');
        setSelectedDocuments([]); // Clear selected documents after sending
        message.success('Message sent');
        setTimeout(() => inputRef.current?.focus(), 100);
      } catch {
        message.error('Failed to send message');
      } finally {
        setSending(false);
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);
    
    // Send typing indicator
    if (typingTimeout) {
      clearTimeout(typingTimeout);
    }
    
    setIsTyping(true);
    chatWebSocket.sendTypingIndicator(true);
    
    const timeout = setTimeout(() => {
      setIsTyping(false);
      chatWebSocket.sendTypingIndicator(false);
    }, 1000);
    
    setTypingTimeout(timeout);
  };

  const handleKnowledgeSearch = async (query: string) => {
    try {
      const results = await searchDocuments(query);
      setSearchResults(results.documents || []);
      
      // Send knowledge search via WebSocket for real-time updates
      chatWebSocket.sendKnowledgeSearch(query);
      
      return results.documents || [];
    } catch (error) {
      console.error('Knowledge search failed:', error);
      message.error('Search failed');
      return [];
    }
  };

  const handleDocumentSelect = (document: Document) => {
    setSelectedDocuments(prev => {
      const exists = prev.find(doc => doc.id === document.id);
      if (exists) {
        return prev.filter(doc => doc.id !== document.id);
      } else {
        return [...prev, document];
      }
    });
  };

  const handleToggleKnowledgeContext = (enabled: boolean) => {
    setKnowledgeContextEnabled(enabled);
    if (!enabled) {
      setSelectedDocuments([]);
      setSearchResults([]);
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessage = (msg: ChatMessage, index: number) => {
    const isUser = msg.sender === 'You';
    const isSystem = msg.messageType === 'system';
    const isError = msg.messageType === 'error';
    
    const messageStyle: React.CSSProperties = {
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems: 'flex-start',
      gap: '12px',
      marginBottom: '16px',
      maxWidth: '80%',
      marginLeft: isUser ? 'auto' : '0',
      marginRight: isUser ? '0' : 'auto',
    };

    const bubbleStyle: React.CSSProperties = {
      background: isError ? '#ff4d4f' : 
                  isSystem ? '#f0f0f0' :
                  isUser ? colors.colorChatUserBubble : colors.colorChatAIBubble,
      color: isError ? '#fff' :
             isSystem ? '#666' :
             isUser ? colors.colorChatUserText : colors.colorChatAIText,
      padding: '12px 16px',
      borderRadius: '18px',
      boxShadow: colors.boxShadow,
      position: 'relative',
      wordWrap: 'break-word',
      maxWidth: '100%',
      border: isSystem ? '1px dashed #d9d9d9' : 'none',
    };

    const avatarStyle: React.CSSProperties = {
      backgroundColor: isError ? '#ff4d4f' :
                      isSystem ? '#d9d9d9' :
                      isUser ? colors.colorPrimary : colors.colorSecondary,
      flexShrink: 0,
    };

    return (
      <div key={index} style={messageStyle}>
        <Avatar 
          icon={isUser ? <UserOutlined /> : 
                isSystem ? <SearchOutlined /> :
                <RobotOutlined />} 
          style={avatarStyle}
        />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={bubbleStyle}>
            {msg.text}
            {msg.metadata && (
              <div style={{ 
                fontSize: '10px', 
                marginTop: '8px', 
                opacity: 0.7,
                borderTop: '1px solid rgba(0,0,0,0.1)',
                paddingTop: '4px'
              }}>
                {msg.metadata.contextChunks && `Context: ${msg.metadata.contextChunks} chunks`}
                {msg.metadata.confidence && ` | Confidence: ${(msg.metadata.confidence * 100).toFixed(1)}%`}
                {msg.metadata.processingTime && ` | Time: ${msg.metadata.processingTime}ms`}
              </div>
            )}
          </div>
          
          {msg.documents && msg.documents.length > 0 && (
            <div style={{ 
              fontSize: '12px', 
              color: colors.colorSecondary,
              marginTop: '4px',
              padding: '8px',
              background: 'rgba(0,0,0,0.05)',
              borderRadius: '8px',
              maxWidth: '300px'
            }}>
              <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>
                Sources ({msg.documents.length}):
              </Text>
              <div style={{ marginTop: '4px' }}>
                {msg.documents.slice(0, 3).map((doc, idx) => (
                  <div key={idx} style={{ 
                    fontSize: '11px', 
                    marginBottom: '2px',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    • {doc.title}
                  </div>
                ))}
                {msg.documents.length > 3 && (
                  <div style={{ fontSize: '11px', color: colors.colorSecondary }}>
                    +{msg.documents.length - 3} more
                  </div>
                )}
              </div>
            </div>
          )}
          
          <div style={{ 
            fontSize: '11px', 
            color: colors.colorSecondary,
            marginLeft: isUser ? 'auto' : '0',
            marginRight: isUser ? '0' : 'auto',
          }}>
            {msg.timestamp && formatTime(msg.timestamp)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <Row style={{ height: '100vh' }}>
      <Col span={showKnowledgeDrawer ? 18 : 24} style={{ height: '100%' }}>
        <Card 
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>Chat Assistant</span>
              {!chatWebSocket.isConnected() && (
                <Badge status="error" text="Disconnected" />
              )}
              {isTyping && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <LoadingOutlined style={{ fontSize: '12px' }} />
                  <span style={{ fontSize: '12px', color: colors.colorSecondary }}>Assistant is typing...</span>
                </div>
              )}
            </div>
          }
          style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
          extra={
            <Tooltip title={knowledgeContextEnabled ? "Knowledge Base enabled" : "Enable Knowledge Base"}>
              <Button
                icon={<BookOutlined />}
                type={knowledgeContextEnabled ? 'primary' : 'default'}
                onClick={() => setShowKnowledgeDrawer(!showKnowledgeDrawer)}
              >
                Knowledge Base
                {selectedDocuments.length > 0 && (
                  <Badge count={selectedDocuments.length} style={{ marginLeft: '8px' }} />
                )}
              </Button>
            </Tooltip>
          }
        >
          {error && (
            <Alert
              message="Connection Error"
              description={error}
              type="error"
              showIcon
              closable
              style={{ marginBottom: 16 }}
            />
          )}

          <div
            ref={listRef}
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '16px',
              marginBottom: '16px',
              border: '1px solid #f0f0f0',
              borderRadius: '8px',
              background: colors.colorBackground
            }}
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>Connecting to chat...</div>
              </div>
            ) : messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: colors.colorSecondary }}>
                <RobotOutlined style={{ fontSize: '48px', marginBottom: 16 }} />
                <Title level={4}>Welcome to Chat Assistant</Title>
                <Text type="secondary">
                  Start a conversation or enable Knowledge Base context for enhanced responses.
                </Text>
                {knowledgeContextEnabled && (
                  <div style={{ marginTop: '16px' }}>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      Knowledge Base is enabled. Your messages will be enhanced with relevant document context.
                    </Text>
                  </div>
                )}
              </div>
            ) : (
              messages.map(renderMessage)
            )}
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <Input
              ref={inputRef}
              value={input}
              onChange={handleInputChange}
              onPressEnter={handleSend}
              placeholder={knowledgeContextEnabled ? 
                "Type your message (Knowledge Base enabled)..." : 
                "Type your message..."}
              disabled={sending}
              style={{ flex: 1 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={sending}
              disabled={!input.trim()}
            >
              Send
            </Button>
          </div>
        </Card>
      </Col>

      {showKnowledgeDrawer && (
        <Col span={6} style={{ height: '100%' }}>
          <Card 
            title="Knowledge Base Context" 
            style={{ height: '100%', overflowY: 'auto' }}
            size="small"
          >
            <KnowledgeContextComponent
              onDocumentSelect={handleDocumentSelect}
              onSearch={handleKnowledgeSearch}
              selectedDocuments={selectedDocuments}
              searchResults={searchResults}
              onToggleContext={handleToggleKnowledgeContext}
              contextEnabled={knowledgeContextEnabled}
            />
          </Card>
        </Col>
      )}
    </Row>
  );
};

export default Chat; 