import { describe, it, expect, vi, beforeEach } from 'vitest';
import { chatService } from '../../../frontend-react/src/services/chat';

// Mock fetch
global.fetch = vi.fn();

describe('Chat Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('access_token', 'test-token');
  });

  describe('sendMessage', () => {
    it('should successfully send a message', async () => {
      const mockResponse = {
        id: 1,
        content: 'Hello, how can I help you?',
        role: 'assistant',
        conversation_id: 1,
        created_at: '2024-01-01T00:00:00Z'
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const messageData = {
        content: 'Hello',
        conversation_id: 1
      };

      const result = await chatService.sendMessage(messageData);

      expect(fetch).toHaveBeenCalledWith('/api/v1/conversations/1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify(messageData),
      });

      expect(result).toEqual(mockResponse);
    });

    it('should handle send message error', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid message' })
      });

      const messageData = {
        content: '',
        conversation_id: 1
      };

      await expect(chatService.sendMessage(messageData))
        .rejects.toThrow('Invalid message');
    });
  });

  describe('getConversations', () => {
    it('should fetch conversations successfully', async () => {
      const mockResponse = {
        conversations: [
          {
            id: 1,
            title: 'Test Conversation',
            created_at: '2024-01-01T00:00:00Z'
          }
        ],
        total: 1,
        page: 1,
        size: 10
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await chatService.getConversations();

      expect(fetch).toHaveBeenCalledWith('/api/v1/conversations/?page=1&size=10', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-token'
        },
      });

      expect(result).toEqual(mockResponse);
    });

    it('should fetch conversations with pagination', async () => {
      const mockResponse = {
        conversations: [],
        total: 0,
        page: 2,
        size: 5
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      await chatService.getConversations(2, 5);

      expect(fetch).toHaveBeenCalledWith('/api/v1/conversations/?page=2&size=5', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-token'
        },
      });
    });
  });

  describe('getMessages', () => {
    it('should fetch messages for a conversation', async () => {
      const mockResponse = {
        messages: [
          {
            id: 1,
            content: 'Hello',
            role: 'user',
            created_at: '2024-01-01T00:00:00Z'
          },
          {
            id: 2,
            content: 'Hi there!',
            role: 'assistant',
            created_at: '2024-01-01T00:01:00Z'
          }
        ],
        total: 2,
        page: 1,
        size: 10
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await chatService.getMessages(1);

      expect(fetch).toHaveBeenCalledWith('/api/v1/conversations/1/messages?page=1&size=10', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-token'
        },
      });

      expect(result).toEqual(mockResponse);
    });
  });

  describe('createConversation', () => {
    it('should create a new conversation', async () => {
      const mockResponse = {
        id: 1,
        title: 'New Conversation',
        created_at: '2024-01-01T00:00:00Z'
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const conversationData = {
        title: 'New Conversation',
        assistant_id: 1
      };

      const result = await chatService.createConversation(conversationData);

      expect(fetch).toHaveBeenCalledWith('/api/v1/conversations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify(conversationData),
      });

      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteConversation', () => {
    it('should delete a conversation', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 204
      });

      await chatService.deleteConversation(1);

      expect(fetch).toHaveBeenCalledWith('/api/v1/conversations/1', {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer test-token'
        },
      });
    });
  });

  describe('streamMessage', () => {
    it('should handle streaming messages', async () => {
      const mockResponse = new Response(
        new ReadableStream({
          start(controller) {
            controller.enqueue(new TextEncoder().encode('data: {"content": "Hello"}\n\n'));
            controller.enqueue(new TextEncoder().encode('data: {"content": " World"}\n\n'));
            controller.enqueue(new TextEncoder().encode('data: [DONE]\n\n'));
            controller.close();
          }
        })
      );

      (fetch as any).mockResolvedValueOnce(mockResponse);

      const messageData = {
        content: 'Hello',
        conversation_id: 1
      };

      const stream = await chatService.streamMessage(messageData);
      const chunks: string[] = [];

      for await (const chunk of stream) {
        chunks.push(chunk);
      }

      expect(chunks).toEqual(['Hello', ' World']);
    });
  });
});