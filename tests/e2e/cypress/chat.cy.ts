describe('Chat E2E Tests', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
    cy.visit('/chat');
  });

  describe('Chat Interface', () => {
    it('should display chat interface', () => {
      cy.get('[data-testid="chat-container"]').should('be.visible');
      cy.get('[data-testid="message-input"]').should('be.visible');
      cy.get('[data-testid="send-button"]').should('be.visible');
      cy.get('[data-testid="chat-messages"]').should('be.visible');
    });

    it('should display welcome message', () => {
      cy.get('[data-testid="welcome-message"]').should('contain', 'Welcome to the chat');
    });

    it('should show user information', () => {
      cy.get('[data-testid="user-menu"]').should('contain', 'testuser');
    });

    it('should display chat sidebar', () => {
      cy.get('[data-testid="chat-sidebar"]').should('be.visible');
      cy.get('[data-testid="conversation-list"]').should('be.visible');
    });
  });

  describe('Message Sending', () => {
    it('should send message successfully', () => {
      cy.intercept('POST', '/api/v1/chat/messages', {
        statusCode: 200,
        body: {
          id: '1',
          content: 'Hello, how are you?',
          role: 'user',
          timestamp: new Date().toISOString()
        }
      }).as('sendMessage');

      cy.get('[data-testid="message-input"]').type('Hello, how are you?');
      cy.get('[data-testid="send-button"]').click();

      cy.wait('@sendMessage');
      cy.get('[data-testid="chat-messages"]').should('contain', 'Hello, how are you?');
    });

    it('should send message with Enter key', () => {
      cy.intercept('POST', '/api/v1/chat/messages', {
        statusCode: 200,
        body: {
          id: '1',
          content: 'Message sent with Enter',
          role: 'user',
          timestamp: new Date().toISOString()
        }
      }).as('sendMessage');

      cy.get('[data-testid="message-input"]').type('Message sent with Enter{enter}');

      cy.wait('@sendMessage');
      cy.get('[data-testid="chat-messages"]').should('contain', 'Message sent with Enter');
    });

    it('should not send empty message', () => {
      cy.get('[data-testid="send-button"]').click();
      cy.get('[data-testid="chat-messages"]').should('not.contain', '');
    });

    it('should clear input after sending message', () => {
      cy.intercept('POST', '/api/v1/chat/messages', {
        statusCode: 200,
        body: { id: '1', content: 'Test message', role: 'user', timestamp: new Date().toISOString() }
      }).as('sendMessage');

      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.wait('@sendMessage');
      cy.get('[data-testid="message-input"]').should('have.value', '');
    });

    it('should show loading state while sending', () => {
      cy.intercept('POST', '/api/v1/chat/messages', {
        delay: 1000,
        statusCode: 200,
        body: { id: '1', content: 'Test message', role: 'user', timestamp: new Date().toISOString() }
      }).as('sendMessage');

      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="send-button"]').should('be.disabled');
      cy.get('[data-testid="loading-spinner"]').should('be.visible');
    });

    it('should handle message sending error', () => {
      cy.intercept('POST', '/api/v1/chat/messages', {
        statusCode: 500,
        body: { message: 'Failed to send message' }
      }).as('sendMessage');

      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.wait('@sendMessage');
      cy.get('[data-testid="error-message"]').should('contain', 'Failed to send message');
    });
  });

  describe('Message Display', () => {
    it('should display user messages', () => {
      cy.get('[data-testid="message-input"]').type('User message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="user-message"]').should('contain', 'User message');
    });

    it('should display assistant messages', () => {
      cy.intercept('POST', '/api/v1/chat/messages', {
        statusCode: 200,
        body: {
          id: '1',
          content: 'User message',
          role: 'user',
          timestamp: new Date().toISOString()
        }
      }).as('userMessage');

      cy.intercept('POST', '/api/v1/chat/assistant-response', {
        statusCode: 200,
        body: {
          id: '2',
          content: 'Assistant response',
          role: 'assistant',
          timestamp: new Date().toISOString()
        }
      }).as('assistantResponse');

      cy.get('[data-testid="message-input"]').type('User message');
      cy.get('[data-testid="send-button"]').click();

      cy.wait('@userMessage');
      cy.wait('@assistantResponse');

      cy.get('[data-testid="assistant-message"]').should('contain', 'Assistant response');
    });

    it('should display message timestamps', () => {
      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="message-timestamp"]').should('be.visible');
    });

    it('should display message status indicators', () => {
      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="message-status"]').should('be.visible');
    });
  });

  describe('WebSocket Integration', () => {
    it('should connect to WebSocket', () => {
      cy.window().its('WebSocket').should('be.called');
    });

    it('should receive real-time messages', () => {
      // Mock WebSocket message
      cy.window().then((win) => {
        const ws = win.WebSocket.mock.instances[0];
        ws.onmessage({
          data: JSON.stringify({
            content: 'Real-time message',
            role: 'assistant',
            timestamp: new Date().toISOString()
          })
        });
      });

      cy.get('[data-testid="assistant-message"]').should('contain', 'Real-time message');
    });

    it('should handle WebSocket connection error', () => {
      cy.window().then((win) => {
        const ws = win.WebSocket.mock.instances[0];
        ws.onerror(new Error('Connection failed'));
      });

      cy.get('[data-testid="error-message"]').should('contain', 'WebSocket connection failed');
    });

    it('should handle WebSocket disconnection', () => {
      cy.window().then((win) => {
        const ws = win.WebSocket.mock.instances[0];
        ws.onclose();
      });

      cy.get('[data-testid="error-message"]').should('contain', 'WebSocket connection closed');
    });
  });

  describe('File Upload', () => {
    it('should upload file successfully', () => {
      cy.intercept('POST', '/api/v1/chat/upload', {
        statusCode: 200,
        body: {
          id: '1',
          filename: 'test.txt',
          url: 'https://example.com/test.txt'
        }
      }).as('uploadFile');

      cy.get('[data-testid="file-input"]').attachFile('test.txt');
      cy.get('[data-testid="upload-button"]').click();

      cy.wait('@uploadFile');
      cy.get('[data-testid="file-message"]').should('contain', 'test.txt');
    });

    it('should handle file upload error', () => {
      cy.intercept('POST', '/api/v1/chat/upload', {
        statusCode: 400,
        body: { message: 'File upload failed' }
      }).as('uploadFile');

      cy.get('[data-testid="file-input"]').attachFile('test.txt');
      cy.get('[data-testid="upload-button"]').click();

      cy.wait('@uploadFile');
      cy.get('[data-testid="error-message"]').should('contain', 'File upload failed');
    });

    it('should validate file type', () => {
      cy.get('[data-testid="file-input"]').attachFile('test.exe');
      cy.get('[data-testid="upload-button"]').click();

      cy.get('[data-testid="error-message"]').should('contain', 'Invalid file type');
    });

    it('should validate file size', () => {
      cy.get('[data-testid="file-input"]').attachFile('large-file.txt');
      cy.get('[data-testid="upload-button"]').click();

      cy.get('[data-testid="error-message"]').should('contain', 'File too large');
    });
  });

  describe('Voice Input', () => {
    it('should start voice recording', () => {
      cy.get('[data-testid="voice-button"]').click();
      cy.get('[data-testid="recording-indicator"]').should('be.visible');
    });

    it('should stop voice recording', () => {
      cy.get('[data-testid="voice-button"]').click();
      cy.get('[data-testid="stop-recording-button"]').click();
      cy.get('[data-testid="recording-indicator"]').should('not.be.visible');
    });

    it('should transcribe voice to text', () => {
      cy.intercept('POST', '/api/v1/chat/transcribe', {
        statusCode: 200,
        body: { text: 'Transcribed voice message' }
      }).as('transcribe');

      cy.get('[data-testid="voice-button"]').click();
      cy.get('[data-testid="stop-recording-button"]').click();

      cy.wait('@transcribe');
      cy.get('[data-testid="message-input"]').should('have.value', 'Transcribed voice message');
    });
  });

  describe('Message Formatting', () => {
    it('should apply bold formatting', () => {
      cy.get('[data-testid="bold-button"]').click();
      cy.get('[data-testid="message-input"]').type('Bold text');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="formatted-message"]').should('contain', '**Bold text**');
    });

    it('should apply italic formatting', () => {
      cy.get('[data-testid="italic-button"]').click();
      cy.get('[data-testid="message-input"]').type('Italic text');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="formatted-message"]').should('contain', '*Italic text*');
    });

    it('should apply code formatting', () => {
      cy.get('[data-testid="code-button"]').click();
      cy.get('[data-testid="message-input"]').type('console.log("Hello")');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="formatted-message"]').should('contain', '`console.log("Hello")`');
    });
  });

  describe('Message Reactions', () => {
    it('should add reaction to message', () => {
      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="reaction-button"]').first().click();
      cy.get('[data-testid="reaction-count"]').should('contain', '1');
    });

    it('should remove reaction from message', () => {
      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="reaction-button"]').first().click();
      cy.get('[data-testid="reaction-button"]').first().click();
      cy.get('[data-testid="reaction-count"]').should('contain', '0');
    });
  });

  describe('Message Search', () => {
    it('should search messages', () => {
      cy.get('[data-testid="search-input"]').type('test');
      cy.get('[data-testid="search-results"]').should('be.visible');
    });

    it('should highlight search results', () => {
      cy.get('[data-testid="search-input"]').type('test');
      cy.get('[data-testid="highlighted-text"]').should('be.visible');
    });

    it('should clear search', () => {
      cy.get('[data-testid="search-input"]').type('test');
      cy.get('[data-testid="clear-search-button"]').click();
      cy.get('[data-testid="search-results"]').should('not.be.visible');
    });
  });

  describe('Message Export', () => {
    it('should export chat history', () => {
      cy.get('[data-testid="export-button"]').click();
      cy.get('[data-testid="export-modal"]').should('be.visible');
    });

    it('should export as JSON', () => {
      cy.get('[data-testid="export-button"]').click();
      cy.get('[data-testid="export-json-button"]').click();
      
      // Check if download is triggered
      cy.readFile('cypress/downloads/chat-history.json').should('exist');
    });

    it('should export as CSV', () => {
      cy.get('[data-testid="export-button"]').click();
      cy.get('[data-testid="export-csv-button"]').click();
      
      cy.readFile('cypress/downloads/chat-history.csv').should('exist');
    });
  });

  describe('Conversation Management', () => {
    it('should create new conversation', () => {
      cy.get('[data-testid="new-conversation-button"]').click();
      cy.get('[data-testid="conversation-title-input"]').type('New Chat');
      cy.get('[data-testid="create-conversation-button"]').click();

      cy.get('[data-testid="conversation-list"]').should('contain', 'New Chat');
    });

    it('should switch between conversations', () => {
      cy.get('[data-testid="conversation-item"]').first().click();
      cy.get('[data-testid="conversation-title"]').should('contain', 'Conversation 1');
    });

    it('should delete conversation', () => {
      cy.get('[data-testid="conversation-item"]').first().find('[data-testid="delete-button"]').click();
      cy.get('[data-testid="confirm-delete-button"]').click();

      cy.get('[data-testid="conversation-list"]').should('not.contain', 'Conversation 1');
    });
  });

  describe('Chat Settings', () => {
    it('should open chat settings', () => {
      cy.get('[data-testid="settings-button"]').click();
      cy.get('[data-testid="chat-settings-modal"]').should('be.visible');
    });

    it('should change chat theme', () => {
      cy.get('[data-testid="settings-button"]').click();
      cy.get('[data-testid="theme-selector"]').select('dark');
      cy.get('[data-testid="save-settings-button"]').click();

      cy.get('[data-testid="chat-container"]').should('have.class', 'dark-theme');
    });

    it('should change message font size', () => {
      cy.get('[data-testid="settings-button"]').click();
      cy.get('[data-testid="font-size-slider"]').invoke('val', 16).trigger('change');
      cy.get('[data-testid="save-settings-button"]').click();

      cy.get('[data-testid="chat-messages"]').should('have.css', 'font-size', '16px');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      cy.get('[data-testid="message-input"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="send-button"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="file-input"]').should('have.attr', 'aria-label');
    });

    it('should support keyboard navigation', () => {
      cy.get('body').tab();
      cy.focus('[data-testid="message-input"]');
      cy.get('[data-testid="message-input"]').should('be.focused');
    });

    it('should announce new messages to screen readers', () => {
      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="screen-reader-announcement"]').should('contain', 'New message received');
    });
  });

  describe('Performance', () => {
    it('should load chat interface quickly', () => {
      cy.visit('/chat');
      cy.get('[data-testid="chat-container"]').should('be.visible');
      
      // Check that page loads within 3 seconds
      cy.get('[data-testid="chat-container"]', { timeout: 3000 }).should('be.visible');
    });

    it('should handle large message history', () => {
      // Generate many messages
      for (let i = 0; i < 100; i++) {
        cy.get('[data-testid="message-input"]').type(`Message ${i}`);
        cy.get('[data-testid="send-button"]').click();
      }

      // Should still be responsive
      cy.get('[data-testid="message-input"]').should('be.visible');
    });

    it('should scroll to bottom on new message', () => {
      cy.get('[data-testid="message-input"]').type('Test message');
      cy.get('[data-testid="send-button"]').click();

      cy.get('[data-testid="chat-messages"]').should('have.prop', 'scrollTop', 0);
    });
  });
});