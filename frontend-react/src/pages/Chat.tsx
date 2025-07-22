import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Card, Spin, Alert, message, Avatar } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import { chatWebSocket } from '../services/chat';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';
import type { InputRef } from 'antd';

interface ChatMessage {
  sender: string;
  text: string;
  timestamp?: Date;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const token = useAuthStore((s) => s.token);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<InputRef>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      chatWebSocket.connect(token, (msg) => {
        setMessages((prev) => [...prev, { ...msg, timestamp: new Date() }]);
        setLoading(false);
      });
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

  const handleSend = () => {
    if (input.trim()) {
      setSending(true);
      try {
        chatWebSocket.send(input);
        setMessages((prev) => [...prev, { 
          sender: 'You', 
          text: input, 
          timestamp: new Date() 
        }]);
        setInput('');
        message.success('Message sent');
        setTimeout(() => inputRef.current?.focus(), 100);
      } catch {
        message.error('Failed to send message');
      } finally {
        setSending(false);
      }
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessage = (msg: ChatMessage, index: number) => {
    const isUser = msg.sender === 'You';
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
      background: isUser ? colors.colorChatUserBubble : colors.colorChatAIBubble,
      color: isUser ? colors.colorChatUserText : colors.colorChatAIText,
      padding: '12px 16px',
      borderRadius: '18px',
      boxShadow: colors.boxShadow,
      position: 'relative',
      wordWrap: 'break-word',
      maxWidth: '100%',
    };

    const avatarStyle: React.CSSProperties = {
      backgroundColor: isUser ? colors.colorPrimary : colors.colorSecondary,
      flexShrink: 0,
    };

    return (
      <div key={index} style={messageStyle}>
        <Avatar 
          icon={isUser ? <UserOutlined /> : <RobotOutlined />} 
          style={avatarStyle}
          size="small"
        />
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
          <div style={bubbleStyle}>
            <div style={{ fontWeight: 500, marginBottom: '4px' }}>
              {msg.sender}
            </div>
            <div>{msg.text}</div>
          </div>
          {msg.timestamp && (
            <div style={{ 
              fontSize: '12px', 
              color: colors.colorTextSecondary, 
              marginTop: '4px',
              marginLeft: isUser ? '0' : '8px',
              marginRight: isUser ? '8px' : '0',
            }}>
              {formatTime(msg.timestamp)}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ 
      maxWidth: '800px', 
      margin: '0 auto', 
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      padding: '20px',
      backgroundColor: colors.colorBgBase,
    }}>
      <Card 
        title={
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            color: colors.colorTextBase,
          }}>
            <RobotOutlined style={{ color: colors.colorPrimary }} />
            AI Chat Assistant
          </div>
        }
        style={{ 
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: colors.colorBgContainer,
          border: `1px solid ${colors.colorBorder}`,
          borderRadius: '12px',
          boxShadow: colors.boxShadow,
        }}
        bodyStyle={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          padding: '20px',
        }}
      >
        {error && (
          <Alert 
            type="error" 
            message={error} 
            showIcon 
            style={{ 
              marginBottom: '16px',
              backgroundColor: colors.colorError + '10',
              borderColor: colors.colorError,
            }} 
          />
        )}
        
        <div
          ref={listRef}
          style={{ 
            flex: 1,
            overflowY: 'auto', 
            marginBottom: '16px',
            padding: '8px',
            backgroundColor: colors.colorBgBase,
            borderRadius: '8px',
            border: `1px solid ${colors.colorBorderSecondary}`,
          }}
          aria-live="polite"
          aria-label="Chat messages"
          tabIndex={0}
        >
          {loading ? (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '200px' 
            }}>
              <Spin size="large" />
            </div>
          ) : messages.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              color: colors.colorTextSecondary,
              padding: '40px 20px',
            }}>
              <RobotOutlined style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }} />
              <p>Start a conversation with the AI assistant</p>
            </div>
          ) : (
            <div>
              {messages.map((msg, index) => renderMessage(msg, index))}
            </div>
          )}
        </div>
        
        <div style={{ 
          display: 'flex', 
          gap: '8px',
          alignItems: 'flex-end',
        }}>
          <Input
            ref={inputRef}
            style={{ 
              flex: 1,
              borderRadius: '24px',
              border: `1px solid ${colors.colorBorder}`,
              backgroundColor: colors.colorBgContainer,
              color: colors.colorTextBase,
            }}
            value={input}
            onChange={e => setInput(e.target.value)}
            onPressEnter={handleSend}
            placeholder="Type your message..."
            aria-label="Type your message"
            disabled={loading || sending}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={sending}
            disabled={loading || sending || !input.trim()}
            aria-label="Send message"
            style={{
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: colors.colorPrimary,
              borderColor: colors.colorPrimary,
            }}
          />
        </div>
      </Card>
    </div>
  );
};

export default Chat; 