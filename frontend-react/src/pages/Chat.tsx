import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, List, Card } from 'antd';
import { chatWebSocket } from '../services/chat';
import { useAuthStore } from '../store/authStore';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState('');
  const token = useAuthStore((s) => s.token);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!token) return;
    chatWebSocket.connect(token, (msg) => setMessages((prev) => [...prev, msg]));
    return () => chatWebSocket.disconnect();
  }, [token]);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      chatWebSocket.send(input);
      setMessages((prev) => [...prev, { sender: 'You', text: input }]);
      setInput('');
    }
  };

  return (
    <Card title="Chat" style={{ maxWidth: 600, margin: 'auto' }}>
      <div ref={listRef} style={{ minHeight: 200, maxHeight: 300, overflowY: 'auto', marginBottom: 16 }}>
        <List
          dataSource={messages}
          renderItem={msg => (
            <List.Item>
              <b>{msg.sender}:</b> {msg.text}
            </List.Item>
          )}
        />
      </div>
      <Input.Group compact>
        <Input
          style={{ width: '80%' }}
          value={input}
          onChange={e => setInput(e.target.value)}
          onPressEnter={handleSend}
          placeholder="Type your message..."
        />
        <Button type="primary" onClick={handleSend}>Send</Button>
      </Input.Group>
    </Card>
  );
};

export default Chat; 