import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, List, Card, Spin, Alert, message } from 'antd';
import { chatWebSocket } from '../services/chat';
import { useAuthStore } from '../store/authStore';
import type { InputRef } from 'antd';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const token = useAuthStore((s) => s.token);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<InputRef>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      chatWebSocket.connect(token, (msg) => {
        setMessages((prev) => [...prev, msg]);
        setLoading(false);
      });
    } catch (e) {
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
        setMessages((prev) => [...prev, { sender: 'You', text: input }]);
        setInput('');
        message.success('Message sent');
        setTimeout(() => inputRef.current?.focus(), 100);
      } catch (e) {
        message.error('Failed to send message');
      } finally {
        setSending(false);
      }
    }
  };

  return (
    <Card title="Chat" style={{ maxWidth: 600, margin: 'auto' }} aria-label="Chat">
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}
      <div
        ref={listRef}
        style={{ minHeight: 200, maxHeight: 300, overflowY: 'auto', marginBottom: 16 }}
        aria-live="polite"
        aria-label="Chat messages"
        tabIndex={0}
      >
        {loading ? (
          <Spin style={{ marginTop: 32 }} />
        ) : (
          <List
            dataSource={messages}
            locale={{ emptyText: <span style={{ color: '#888' }}>No messages yet</span> }}
            renderItem={msg => (
              <List.Item>
                <b>{msg.sender}:</b> {msg.text}
              </List.Item>
            )}
          />
        )}
      </div>
      <Input.Group compact style={{ display: 'flex' }}>
        <Input
          ref={inputRef}
          style={{ flex: 1, minWidth: 0 }}
          value={input}
          onChange={e => setInput(e.target.value)}
          onPressEnter={handleSend}
          placeholder="Type your message..."
          aria-label="Type your message"
          disabled={loading || sending}
        />
        <Button
          type="primary"
          onClick={handleSend}
          loading={sending}
          disabled={loading || sending || !input.trim()}
          aria-label="Send message"
        >
          Send
        </Button>
      </Input.Group>
    </Card>
  );
};

export default Chat; 