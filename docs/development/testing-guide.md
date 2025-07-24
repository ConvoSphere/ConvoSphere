# Testing Guide

This guide provides comprehensive information about testing strategies, methodologies, and best practices for the AI Chat Application. It covers unit testing, integration testing, end-to-end testing, and performance testing.

## Testing Strategy Overview

### Testing Pyramid

The AI Chat Application follows the testing pyramid approach:

```
┌─────────────────────────────────────────────────────────┐
│                    E2E Tests                            │
│                    (Few, Slow)                          │
├─────────────────────────────────────────────────────────┤
│                Integration Tests                        │
│                (Some, Medium)                           │
├─────────────────────────────────────────────────────────┤
│                   Unit Tests                            │
│                  (Many, Fast)                           │
└─────────────────────────────────────────────────────────┘
```

### Testing Principles

- **Fast Feedback**: Unit tests should run quickly
- **Reliable**: Tests should be deterministic and not flaky
- **Maintainable**: Tests should be easy to understand and modify
- **Comprehensive**: Cover critical paths and edge cases
- **Automated**: All tests should run automatically in CI/CD

## Unit Testing

### Backend Unit Testing

#### Test Structure
```
backend/
├── tests/
│   ├── unit/
│   │   ├── test_api/
│   │   │   ├── test_auth.py
│   │   │   ├── test_chat.py
│   │   │   └── test_users.py
│   │   ├── test_services/
│   │   │   ├── test_ai_service.py
│   │   │   ├── test_file_service.py
│   │   │   └── test_user_service.py
│   │   ├── test_models/
│   │   │   ├── test_user.py
│   │   │   ├── test_message.py
│   │   │   └── test_conversation.py
│   │   └── test_utils/
│   │       ├── test_validation.py
│   │       └── test_helpers.py
│   ├── conftest.py
│   └── fixtures/
│       ├── users.py
│       ├── conversations.py
│       └── messages.py
```

#### Example Unit Test
```python
# backend/tests/unit/test_services/test_ai_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.ai_service import AIService
from backend.models.message import Message
from backend.exceptions import AIServiceError

class TestAIService:
    @pytest.fixture
    def ai_service(self):
        return AIService()
    
    @pytest.fixture
    def mock_openai_client(self):
        with patch('backend.services.ai_service.OpenAIClient') as mock:
            yield mock
    
    def test_generate_response_success(self, ai_service, mock_openai_client):
        # Arrange
        message = Message(content="Hello, how are you?")
        expected_response = "I'm doing well, thank you!"
        
        mock_openai_client.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=expected_response))]
        )
        
        # Act
        result = ai_service.generate_response(message)
        
        # Assert
        assert result.content == expected_response
        mock_openai_client.return_value.chat.completions.create.assert_called_once()
    
    def test_generate_response_api_error(self, ai_service, mock_openai_client):
        # Arrange
        message = Message(content="Hello")
        mock_openai_client.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        # Act & Assert
        with pytest.raises(AIServiceError):
            ai_service.generate_response(message)
    
    def test_generate_response_empty_content(self, ai_service):
        # Arrange
        message = Message(content="")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            ai_service.generate_response(message)
    
    @pytest.mark.parametrize("content,expected_tokens", [
        ("Hello", 1),
        ("This is a longer message", 5),
        ("", 0),
    ])
    def test_count_tokens(self, ai_service, content, expected_tokens):
        # Act
        result = ai_service.count_tokens(content)
        
        # Assert
        assert result == expected_tokens
```

#### Test Configuration
```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import get_db, Base
from backend.main import app

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Frontend Unit Testing

#### Test Structure
```
frontend-react/
├── src/
│   ├── __tests__/
│   │   ├── components/
│   │   │   ├── ChatMessage.test.tsx
│   │   │   ├── MessageInput.test.tsx
│   │   │   └── FileUpload.test.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.test.ts
│   │   │   ├── useAuth.test.ts
│   │   │   └── useWebSocket.test.ts
│   │   ├── services/
│   │   │   ├── api.test.ts
│   │   │   ├── websocket.test.ts
│   │   │   └── storage.test.ts
│   │   └── utils/
│   │       ├── validation.test.ts
│   │       └── helpers.test.ts
│   ├── setupTests.ts
│   └── mocks/
│       ├── api.ts
│       ├── websocket.ts
│       └── storage.ts
```

#### Example Unit Test
```typescript
// frontend-react/src/__tests__/components/ChatMessage.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatMessage } from '../../components/ChatMessage';
import { Message } from '../../types/message';

const mockMessage: Message = {
  id: '1',
  content: 'Hello, world!',
  role: 'user',
  timestamp: new Date('2023-01-01T00:00:00Z'),
  conversationId: 'conv-1'
};

const mockOnEdit = jest.fn();
const mockOnDelete = jest.fn();

describe('ChatMessage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders message content correctly', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        isOwnMessage={true}
      />
    );

    expect(screen.getByText('Hello, world!')).toBeInTheDocument();
  });

  it('shows edit and delete buttons for own messages', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        isOwnMessage={true}
      />
    );

    expect(screen.getByLabelText('Edit message')).toBeInTheDocument();
    expect(screen.getByLabelText('Delete message')).toBeInTheDocument();
  });

  it('does not show edit and delete buttons for other messages', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        isOwnMessage={false}
      />
    );

    expect(screen.queryByLabelText('Edit message')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Delete message')).not.toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        isOwnMessage={true}
      />
    );

    fireEvent.click(screen.getByLabelText('Edit message'));
    expect(mockOnEdit).toHaveBeenCalledWith(mockMessage);
  });

  it('calls onDelete when delete button is clicked', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        isOwnMessage={true}
      />
    );

    fireEvent.click(screen.getByLabelText('Delete message'));
    expect(mockOnDelete).toHaveBeenCalledWith(mockMessage.id);
  });

  it('displays timestamp in correct format', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        isOwnMessage={true}
      />
    );

    expect(screen.getByText(/Jan 1, 2023/)).toBeInTheDocument();
  });
});
```

#### Test Configuration
```typescript
// frontend-react/src/setupTests.ts
import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};
```

## Integration Testing

### Backend Integration Tests

#### API Integration Tests
```python
# backend/tests/integration/test_api/test_chat_api.py
import pytest
from fastapi.testclient import TestClient
from backend.models.user import User
from backend.models.conversation import Conversation

class TestChatAPI:
    def test_create_message_success(self, client, auth_headers, test_user, test_conversation):
        # Arrange
        message_data = {
            "content": "Hello, AI!",
            "conversation_id": str(test_conversation.id)
        }
        
        # Act
        response = client.post(
            "/api/chat/messages",
            json=message_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello, AI!"
        assert data["user_id"] == str(test_user.id)
        assert data["conversation_id"] == str(test_conversation.id)
    
    def test_create_message_unauthorized(self, client, test_conversation):
        # Arrange
        message_data = {
            "content": "Hello, AI!",
            "conversation_id": str(test_conversation.id)
        }
        
        # Act
        response = client.post("/api/chat/messages", json=message_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_create_message_invalid_conversation(self, client, auth_headers):
        # Arrange
        message_data = {
            "content": "Hello, AI!",
            "conversation_id": "invalid-uuid"
        }
        
        # Act
        response = client.post(
            "/api/chat/messages",
            json=message_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_get_conversation_messages(self, client, auth_headers, test_conversation, test_messages):
        # Act
        response = client.get(
            f"/api/chat/conversations/{test_conversation.id}/messages",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == len(test_messages)
        assert data["total"] == len(test_messages)
    
    def test_stream_ai_response(self, client, auth_headers, test_conversation):
        # Arrange
        message_data = {
            "content": "What is the weather like?",
            "conversation_id": str(test_conversation.id)
        }
        
        # Act
        with client.stream(
            "POST",
            "/api/chat/stream",
            json=message_data,
            headers=auth_headers
        ) as response:
            # Assert
            assert response.status_code == 200
            chunks = []
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    chunks.append(chunk.decode())
            
            # Verify streaming response
            assert len(chunks) > 0
            assert any("data:" in chunk for chunk in chunks)
```

#### Database Integration Tests
```python
# backend/tests/integration/test_database/test_user_repository.py
import pytest
from backend.repositories.user_repository import UserRepository
from backend.models.user import User
from backend.schemas.user import UserCreate

class TestUserRepository:
    def test_create_user(self, db_session):
        # Arrange
        repo = UserRepository(db_session)
        user_data = UserCreate(
            email="test@example.com",
            password="testpassword",
            full_name="Test User"
        )
        
        # Act
        user = repo.create(user_data)
        
        # Assert
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
    
    def test_get_user_by_email(self, db_session, test_user):
        # Arrange
        repo = UserRepository(db_session)
        
        # Act
        user = repo.get_by_email(test_user.email)
        
        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_email_not_found(self, db_session):
        # Arrange
        repo = UserRepository(db_session)
        
        # Act
        user = repo.get_by_email("nonexistent@example.com")
        
        # Assert
        assert user is None
    
    def test_update_user(self, db_session, test_user):
        # Arrange
        repo = UserRepository(db_session)
        new_name = "Updated Name"
        
        # Act
        updated_user = repo.update(test_user.id, {"full_name": new_name})
        
        # Assert
        assert updated_user.full_name == new_name
        assert updated_user.id == test_user.id
    
    def test_delete_user(self, db_session, test_user):
        # Arrange
        repo = UserRepository(db_session)
        
        # Act
        repo.delete(test_user.id)
        
        # Assert
        deleted_user = repo.get_by_id(test_user.id)
        assert deleted_user is None
```

### Frontend Integration Tests

#### Component Integration Tests
```typescript
// frontend-react/src/__tests__/integration/ChatInterface.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatInterface } from '../../components/ChatInterface';
import { ChatProvider } from '../../contexts/ChatContext';
import { AuthProvider } from '../../contexts/AuthContext';
import { rest } from 'msw';
import { server } from '../../mocks/server';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      <ChatProvider>
        {component}
      </ChatProvider>
    </AuthProvider>
  );
};

describe('ChatInterface Integration', () => {
  beforeEach(() => {
    server.use(
      rest.get('/api/conversations', (req, res, ctx) => {
        return res(
          ctx.json({
            conversations: [
              { id: '1', title: 'Test Conversation', updatedAt: '2023-01-01T00:00:00Z' }
            ]
          })
        );
      })
    );
  });

  it('loads conversations and displays them', async () => {
    renderWithProviders(<ChatInterface />);

    await waitFor(() => {
      expect(screen.getByText('Test Conversation')).toBeInTheDocument();
    });
  });

  it('sends message and receives AI response', async () => {
    server.use(
      rest.post('/api/chat/messages', (req, res, ctx) => {
        return res(
          ctx.json({
            id: 'msg-1',
            content: 'Hello! How can I help you?',
            role: 'assistant',
            timestamp: '2023-01-01T00:00:00Z'
          })
        );
      })
    );

    renderWithProviders(<ChatInterface />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Hello, AI!' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Hello, AI!')).toBeInTheDocument();
      expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();
    });
  });

  it('handles file upload and displays file in chat', async () => {
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });

    server.use(
      rest.post('/api/files/upload', (req, res, ctx) => {
        return res(
          ctx.json({
            id: 'file-1',
            filename: 'test.txt',
            size: 12,
            url: '/files/test.txt'
          })
        );
      })
    );

    renderWithProviders(<ChatInterface />);

    const fileInput = screen.getByLabelText('Upload file');
    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument();
    });
  });
});
```

## End-to-End Testing

### E2E Test Structure
```
tests/
├── e2e/
│   ├── specs/
│   │   ├── auth.spec.ts
│   │   ├── chat.spec.ts
│   │   ├── file-upload.spec.ts
│   │   └── user-management.spec.ts
│   ├── fixtures/
│   │   ├── users.json
│   │   └── conversations.json
│   ├── pages/
│   │   ├── LoginPage.ts
│   │   ├── ChatPage.ts
│   │   └── SettingsPage.ts
│   └── utils/
│       ├── test-helpers.ts
│       └── api-helpers.ts
```

### Example E2E Test
```typescript
// tests/e2e/specs/chat.spec.ts
import { test, expect } from '@playwright/test';
import { ChatPage } from '../pages/ChatPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Chat Functionality', () => {
  let chatPage: ChatPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    chatPage = new ChatPage(page);
    loginPage = new LoginPage(page);
    
    // Login before each test
    await loginPage.goto();
    await loginPage.login('test@example.com', 'password');
    await chatPage.goto();
  });

  test('should send message and receive AI response', async () => {
    // Arrange
    const message = 'Hello, AI! How are you?';
    
    // Act
    await chatPage.sendMessage(message);
    
    // Assert
    await expect(chatPage.getMessageByContent(message)).toBeVisible();
    await expect(chatPage.getAIResponse()).toBeVisible();
  });

  test('should create new conversation', async () => {
    // Act
    await chatPage.createNewConversation();
    
    // Assert
    await expect(chatPage.getNewConversationTitle()).toBeVisible();
    await expect(chatPage.getEmptyChatState()).toBeVisible();
  });

  test('should upload file and display in chat', async () => {
    // Arrange
    const filePath = 'tests/e2e/fixtures/test-file.txt';
    
    // Act
    await chatPage.uploadFile(filePath);
    
    // Assert
    await expect(chatPage.getFileByName('test-file.txt')).toBeVisible();
  });

  test('should handle long messages', async () => {
    // Arrange
    const longMessage = 'A'.repeat(1000);
    
    // Act
    await chatPage.sendMessage(longMessage);
    
    // Assert
    await expect(chatPage.getMessageByContent(longMessage)).toBeVisible();
  });

  test('should handle network errors gracefully', async () => {
    // Arrange
    await chatPage.simulateNetworkError();
    
    // Act
    await chatPage.sendMessage('Test message');
    
    // Assert
    await expect(chatPage.getErrorMessage()).toBeVisible();
    await expect(chatPage.getRetryButton()).toBeVisible();
  });
});
```

### Page Object Model
```typescript
// tests/e2e/pages/ChatPage.ts
import { Page, Locator, expect } from '@playwright/test';

export class ChatPage {
  readonly page: Page;
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  readonly messageList: Locator;
  readonly newChatButton: Locator;
  readonly fileUploadInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.messageInput = page.getByPlaceholder('Type your message...');
    this.sendButton = page.getByLabelText('Send message');
    this.messageList = page.locator('[data-testid="message-list"]');
    this.newChatButton = page.getByLabelText('New chat');
    this.fileUploadInput = page.locator('input[type="file"]');
  }

  async goto() {
    await this.page.goto('/chat');
  }

  async sendMessage(content: string) {
    await this.messageInput.fill(content);
    await this.sendButton.click();
  }

  async createNewConversation() {
    await this.newChatButton.click();
  }

  async uploadFile(filePath: string) {
    await this.fileUploadInput.setInputFiles(filePath);
  }

  getMessageByContent(content: string) {
    return this.page.getByText(content);
  }

  getAIResponse() {
    return this.page.locator('[data-testid="ai-message"]').first();
  }

  getNewConversationTitle() {
    return this.page.getByText('New Conversation');
  }

  getEmptyChatState() {
    return this.page.getByText('Start a new conversation');
  }

  getFileByName(filename: string) {
    return this.page.getByText(filename);
  }

  getErrorMessage() {
    return this.page.getByText('Failed to send message');
  }

  getRetryButton() {
    return this.page.getByRole('button', { name: 'Retry' });
  }

  async simulateNetworkError() {
    await this.page.route('**/api/chat/messages', route => {
      route.abort('failed');
    });
  }
}
```

## Performance Testing

### Load Testing with Locust

#### Locust Test File
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import json
import random

class ChatUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def send_message(self):
        """Send a chat message"""
        message_data = {
            "content": f"Test message {random.randint(1, 1000)}",
            "conversation_id": "test-conversation-id"
        }
        
        with self.client.post(
            "/api/chat/messages",
            json=message_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed to send message: {response.status_code}")
    
    @task(1)
    def get_conversations(self):
        """Get user conversations"""
        with self.client.get(
            "/api/chat/conversations",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get conversations: {response.status_code}")
    
    @task(1)
    def upload_file(self):
        """Upload a file"""
        files = {"file": ("test.txt", "Test file content", "text/plain")}
        
        with self.client.post(
            "/api/files/upload",
            files=files,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed to upload file: {response.status_code}")
```

### Performance Test Configuration
```yaml
# tests/performance/locust.conf
locustfile = tests/performance/locustfile.py
host = http://localhost:8000
users = 100
spawn-rate = 10
run-time = 5m
headless = true
html = performance-report.html
csv = performance-results
```

## Test Data Management

### Test Fixtures

#### Backend Fixtures
```python
# backend/tests/fixtures/users.py
import pytest
from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.services.user_service import UserService

@pytest.fixture
def test_user(db_session):
    user_service = UserService(db_session)
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword",
        full_name="Test User"
    )
    return user_service.create_user(user_data)

@pytest.fixture
def test_users(db_session):
    user_service = UserService(db_session)
    users = []
    
    for i in range(5):
        user_data = UserCreate(
            email=f"user{i}@example.com",
            password="password",
            full_name=f"User {i}"
        )
        users.append(user_service.create_user(user_data))
    
    return users

@pytest.fixture
def admin_user(db_session):
    user_service = UserService(db_session)
    user_data = UserCreate(
        email="admin@example.com",
        password="adminpassword",
        full_name="Admin User",
        is_admin=True
    )
    return user_service.create_user(user_data)
```

#### Frontend Fixtures
```typescript
// frontend-react/src/__tests__/fixtures/users.ts
export const mockUsers = [
  {
    id: '1',
    email: 'test@example.com',
    fullName: 'Test User',
    isActive: true,
    createdAt: '2023-01-01T00:00:00Z'
  },
  {
    id: '2',
    email: 'admin@example.com',
    fullName: 'Admin User',
    isActive: true,
    isAdmin: true,
    createdAt: '2023-01-01T00:00:00Z'
  }
];

export const mockUser = mockUsers[0];

// frontend-react/src/__tests__/fixtures/messages.ts
export const mockMessages = [
  {
    id: '1',
    content: 'Hello, AI!',
    role: 'user',
    timestamp: '2023-01-01T00:00:00Z',
    conversationId: 'conv-1'
  },
  {
    id: '2',
    content: 'Hello! How can I help you?',
    role: 'assistant',
    timestamp: '2023-01-01T00:00:01Z',
    conversationId: 'conv-1'
  }
];
```

## Test Coverage

### Coverage Configuration

#### Backend Coverage
```ini
# backend/.coveragerc
[run]
source = backend
omit = 
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*
    */env/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

#### Frontend Coverage
```json
// frontend-react/package.json
{
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{js,jsx,ts,tsx}",
      "!src/**/*.d.ts",
      "!src/index.tsx",
      "!src/serviceWorker.ts",
      "!src/setupTests.ts"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

## Continuous Integration

### GitHub Actions Test Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    name: Backend Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest --cov=backend --cov-report=xml --cov-report=html
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend
          name: backend-coverage

  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test -- --coverage --watchAll=false
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend-react/coverage/lcov.info
          flags: frontend
          name: frontend-coverage

  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Start application
        run: |
          docker-compose up -d
          sleep 60
      
      - name: Run E2E tests
        run: npm run test:e2e:ci
        env:
          TEST_URL: http://localhost:3000
          API_URL: http://localhost:8000
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: e2e-test-results
          path: |
            test-results/
            playwright-report/
```

## Best Practices

### Testing Best Practices

1. **Test Naming**: Use descriptive test names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear sections
3. **Test Isolation**: Each test should be independent and not rely on other tests
4. **Mock External Dependencies**: Mock external services and APIs
5. **Use Test Data Builders**: Create helper functions for generating test data
6. **Test Edge Cases**: Include tests for error conditions and edge cases
7. **Keep Tests Fast**: Optimize tests to run quickly
8. **Maintain Test Data**: Keep test data up to date with schema changes

### Common Anti-patterns

1. **Testing Implementation Details**: Focus on behavior, not implementation
2. **Over-mocking**: Only mock what's necessary
3. **Flaky Tests**: Ensure tests are deterministic
4. **Slow Tests**: Optimize test performance
5. **Test Duplication**: Reuse test utilities and fixtures
6. **Testing Framework Code**: Don't test the testing framework itself

---

**Next Steps**: Learn about [API Development](api-development.md) for building new features, or explore [Code Style](code-style.md) for maintaining code quality.