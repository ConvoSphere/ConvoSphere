import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Avatar, Spin } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import { useThemeStore } from '../store/themeStore';
import Icon from './icons/Icon';

interface ChatMessage {
  id: string;
  sender: string;
  text: string;
  timestamp: Date;
  type: 'user' | 'ai';
}

interface VirtualizedChatProps {
  messages: ChatMessage[];
  loading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
  height?: number;
  itemHeight?: number;
}

const VirtualizedChat: React.FC<VirtualizedChatProps> = ({
  messages,
  loading = false,
  onLoadMore,
  hasMore = false,
  height = 400,
  itemHeight = 80,
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const listRef = useRef<HTMLDivElement>(null);
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 20 });

  // Berechne sichtbare Nachrichten basierend auf Scroll-Position
  const calculateVisibleRange = useCallback(() => {
    if (!listRef.current) return;

    const scrollTop = listRef.current.scrollTop;
    const containerHeight = listRef.current.clientHeight;
    
    const start = Math.floor(scrollTop / itemHeight);
    const end = Math.min(
      start + Math.ceil(containerHeight / itemHeight) + 5, // Buffer für smooth scrolling
      messages.length
    );

    setVisibleRange({ start: Math.max(0, start - 5), end });
  }, [itemHeight, messages.length]);

  // Scroll Event Handler
  const handleScroll = useCallback(() => {
    calculateVisibleRange();
    
    // Load more wenn am Ende
    if (listRef.current && hasMore && onLoadMore) {
      const { scrollTop, scrollHeight, clientHeight } = listRef.current;
      if (scrollTop + clientHeight >= scrollHeight - 100) {
        onLoadMore();
      }
    }
  }, [calculateVisibleRange, hasMore, onLoadMore]);

  // Sichtbare Nachrichten
  const visibleMessages = useMemo(() => {
    return messages.slice(visibleRange.start, visibleRange.end);
  }, [messages, visibleRange]);

  // Padding für korrekte Scroll-Höhe
  const topPadding = visibleRange.start * itemHeight;
  const bottomPadding = (messages.length - visibleRange.end) * itemHeight;

  // Render einzelne Nachricht
  const renderMessage = useCallback((message: ChatMessage) => {
    const isUser = message.type === 'user';
    
    const messageStyle: React.CSSProperties = {
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems: 'flex-start',
      gap: '12px',
      marginBottom: '16px',
      maxWidth: '80%',
      marginLeft: isUser ? 'auto' : '0',
      marginRight: isUser ? '0' : 'auto',
      minHeight: itemHeight - 16, // Abzüglich margin
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
      flex: 1,
    };

    const avatarStyle: React.CSSProperties = {
      backgroundColor: isUser ? colors.colorPrimary : colors.colorSecondary,
      flexShrink: 0,
    };

    const formatTime = (timestamp: Date) => {
      return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
      <div key={message.id} style={messageStyle}>
        <Avatar 
          icon={isUser ? <UserOutlined /> : <RobotOutlined />} 
          style={avatarStyle}
          size="small"
        />
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start', flex: 1 }}>
          <div style={bubbleStyle}>
            <div style={{ fontWeight: 500, marginBottom: '4px' }}>
              {message.sender}
            </div>
            <div>{message.text}</div>
          </div>
          <div style={{ 
            fontSize: '12px', 
            color: colors.colorTextSecondary, 
            marginTop: '4px',
            marginLeft: isUser ? '0' : '8px',
            marginRight: isUser ? '8px' : '0',
          }}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    );
  }, [colors, itemHeight]);

  // Auto-scroll zum Ende bei neuen Nachrichten
  useEffect(() => {
    if (listRef.current && messages.length > 0) {
      const isAtBottom = listRef.current.scrollTop + listRef.current.clientHeight >= listRef.current.scrollHeight - 10;
      if (isAtBottom) {
        listRef.current.scrollTop = listRef.current.scrollHeight;
      }
    }
  }, [messages.length]);

  // Initial visible range
  useEffect(() => {
    calculateVisibleRange();
  }, [calculateVisibleRange]);

  const containerStyle: React.CSSProperties = {
    height,
    overflow: 'auto',
    backgroundColor: colors.colorBgBase,
    borderRadius: '8px',
    border: `1px solid ${colors.colorBorderSecondary}`,
    position: 'relative',
  };

  const contentStyle: React.CSSProperties = {
    paddingTop: topPadding,
    paddingBottom: bottomPadding,
    minHeight: '100%',
  };

  const loadingStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px',
    color: colors.colorTextSecondary,
  };

  const emptyStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100%',
    color: colors.colorTextSecondary,
  };

  return (
    <div style={containerStyle} ref={listRef} onScroll={handleScroll}>
      <div style={contentStyle}>
        {/* Loading Indicator am Anfang */}
        {loading && hasMore && (
          <div style={loadingStyle}>
            <Spin size="small" />
            <span style={{ marginLeft: '8px' }}>Loading more messages...</span>
          </div>
        )}

        {/* Nachrichten */}
        {visibleMessages.length > 0 ? (
          visibleMessages.map(renderMessage)
        ) : !loading ? (
          <div style={emptyStyle}>
            <Icon name="message" size="xl" variant="muted" />
            <p style={{ marginTop: '16px' }}>No messages yet</p>
            <p style={{ fontSize: '14px', opacity: 0.7 }}>Start a conversation</p>
          </div>
        ) : (
          <div style={loadingStyle}>
            <Spin size="large" />
          </div>
        )}

        {/* Loading Indicator am Ende */}
        {loading && !hasMore && (
          <div style={loadingStyle}>
            <Spin size="small" />
            <span style={{ marginLeft: '8px' }}>Sending message...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VirtualizedChat;