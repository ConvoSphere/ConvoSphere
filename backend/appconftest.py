"""
Test configuration and fixtures for the AI Assistant Platform.

This module provides test data and configuration for all test modules.
"""

import uuid
from datetime import datetime, timedelta
from datetime import UTC

# Test User Credentials
TEST_USER_CREDENTIALS = {
    "admin": {
        "email": "admin@test.com",
        "username": "admin",
        "password": "TestPassword123!",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_active": True,
    },
    "user": {
        "email": "user@test.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "is_active": True,
    },
    "manager": {
        "email": "manager@test.com",
        "username": "manager",
        "password": "TestPassword123!",
        "first_name": "Manager",
        "last_name": "User",
        "role": "manager",
        "is_active": True,
    },
    "guest": {
        "email": "guest@test.com",
        "username": "guest",
        "password": "TestPassword123!",
        "first_name": "Guest",
        "last_name": "User",
        "role": "guest",
        "is_active": True,
    },
}

# Test Assistant Data
TEST_ASSISTANT_DATA = {
    "basic": {
        "name": "Test Assistant",
        "description": "A test assistant for testing purposes",
        "instructions": "You are a helpful test assistant.",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "is_active": True,
        "is_public": False,
    },
    "public": {
        "name": "Public Test Assistant",
        "description": "A public test assistant",
        "instructions": "You are a public test assistant.",
        "model": "gpt-4",
        "temperature": 0.5,
        "max_tokens": 2000,
        "is_active": True,
        "is_public": True,
    },
    "specialized": {
        "name": "Specialized Assistant",
        "description": "A specialized assistant for specific tasks",
        "instructions": "You are specialized in technical documentation.",
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 1500,
        "is_active": True,
        "is_public": False,
    },
}

# Test Conversation Data
TEST_CONVERSATION_DATA = {
    "basic": {
        "title": "Test Conversation",
        "description": "A test conversation",
        "is_public": False,
        "tags": ["test", "conversation"],
    },
    "public": {
        "title": "Public Test Conversation",
        "description": "A public test conversation",
        "is_public": True,
        "tags": ["public", "test"],
    },
    "technical": {
        "title": "Technical Discussion",
        "description": "A technical conversation about programming",
        "is_public": False,
        "tags": ["technical", "programming"],
    },
}

# Test Message Data
TEST_MESSAGE_DATA = {
    "user_message": {
        "content": "Hello, how are you?",
        "role": "user",
        "message_type": "text",
    },
    "assistant_message": {
        "content": "I'm doing well, thank you for asking! How can I help you today?",
        "role": "assistant",
        "message_type": "text",
    },
    "system_message": {
        "content": "This is a system message for testing purposes.",
        "role": "system",
        "message_type": "text",
    },
    "tool_message": {
        "content": "Tool execution result",
        "role": "tool",
        "message_type": "tool",
        "tool_name": "test_tool",
        "tool_data": {"result": "success"},
    },
}

# Test Document Data
TEST_DOCUMENT_DATA = {
    "pdf": {
        "title": "Test PDF Document",
        "description": "A test PDF document for testing purposes",
        "file_name": "test_document.pdf",
        "file_type": "application/pdf",
        "file_size": 1024,
        "content": "This is test content for a PDF document.",
        "tags": ["test", "pdf", "document"],
        "status": "processed",
    },
    "text": {
        "title": "Test Text Document",
        "description": "A test text document",
        "file_name": "test_document.txt",
        "file_type": "text/plain",
        "file_size": 512,
        "content": "This is test content for a text document.",
        "tags": ["test", "text", "document"],
        "status": "processed",
    },
    "markdown": {
        "title": "Test Markdown Document",
        "description": "A test markdown document",
        "file_name": "test_document.md",
        "file_type": "text/markdown",
        "file_size": 768,
        "content": "# Test Document\n\nThis is a test markdown document.",
        "tags": ["test", "markdown", "document"],
        "status": "processed",
    },
}

# Test Tool Data
TEST_TOOL_DATA = {
    "basic": {
        "name": "test_tool",
        "description": "A test tool for testing purposes",
        "category": "utility",
        "is_active": True,
        "parameters": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input parameter"}
            },
            "required": ["input"],
        },
    },
    "calculator": {
        "name": "calculator",
        "description": "A simple calculator tool",
        "category": "math",
        "is_active": True,
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["operation", "a", "b"],
        },
    },
}

# Test Knowledge Base Data
TEST_KNOWLEDGE_DATA = {
    "basic": {
        "name": "Test Knowledge Base",
        "description": "A test knowledge base for testing purposes",
        "is_public": False,
        "tags": ["test", "knowledge"],
    },
    "public": {
        "name": "Public Knowledge Base",
        "description": "A public knowledge base",
        "is_public": True,
        "tags": ["public", "knowledge"],
    },
}

# Test Domain Group Data
TEST_DOMAIN_GROUP_DATA = {
    "basic": {
        "name": "Test Domain Group",
        "description": "A test domain group for testing purposes",
        "is_active": True,
        "tags": ["test", "domain"],
    },
    "technical": {
        "name": "Technical Domain Group",
        "description": "A technical domain group",
        "is_active": True,
        "tags": ["technical", "domain"],
    },
}

# Test API Endpoints
TEST_API_ENDPOINTS = {
    "auth": {
        "register": "/api/v1/auth/register",
        "login": "/api/v1/auth/login",
        "logout": "/api/v1/auth/logout",
        "refresh": "/api/v1/auth/refresh",
        "profile": "/api/v1/auth/profile",
    },
    "users": {
        "list": "/api/v1/users/",
        "create": "/api/v1/users/",
        "get": "/api/v1/users/{user_id}",
        "update": "/api/v1/users/{user_id}",
        "delete": "/api/v1/users/{user_id}",
    },
    "assistants": {
        "list": "/api/v1/assistants/",
        "create": "/api/v1/assistants/",
        "get": "/api/v1/assistants/{assistant_id}",
        "update": "/api/v1/assistants/{assistant_id}",
        "delete": "/api/v1/assistants/{assistant_id}",
    },
    "conversations": {
        "list": "/api/v1/conversations/",
        "create": "/api/v1/conversations/",
        "get": "/api/v1/conversations/{conversation_id}",
        "update": "/api/v1/conversations/{conversation_id}",
        "delete": "/api/v1/conversations/{conversation_id}",
    },
    "chat": {
        "send_message": "/api/v1/chat/send",
        "stream": "/api/v1/chat/stream",
        "history": "/api/v1/chat/history",
    },
    "tools": {
        "list": "/api/v1/tools/",
        "create": "/api/v1/tools/",
        "get": "/api/v1/tools/{tool_id}",
        "update": "/api/v1/tools/{tool_id}",
        "delete": "/api/v1/tools/{tool_id}",
        "execute": "/api/v1/tools/{tool_id}/execute",
    },
    "knowledge": {
        "list": "/api/v1/knowledge/",
        "create": "/api/v1/knowledge/",
        "get": "/api/v1/knowledge/{knowledge_id}",
        "update": "/api/v1/knowledge/{knowledge_id}",
        "delete": "/api/v1/knowledge/{knowledge_id}",
        "search": "/api/v1/knowledge/search",
    },
}

# Test Headers
TEST_HEADERS = {
    "json": {"Content-Type": "application/json"},
    "multipart": {"Content-Type": "multipart/form-data"},
    "auth": {"Authorization": "Bearer test_token"},
    "admin_auth": {"Authorization": "Bearer admin_test_token"},
}

# Test Error Messages
TEST_ERROR_MESSAGES = {
    "unauthorized": "Not authorized to access this resource",
    "not_found": "Resource not found",
    "validation_error": "Validation error",
    "server_error": "Internal server error",
    "rate_limit": "Rate limit exceeded",
    "invalid_token": "Invalid or expired token",
    "permission_denied": "Permission denied",
}

# Test UUIDs
TEST_UUIDS = {
    "user_1": str(uuid.uuid4()),
    "user_2": str(uuid.uuid4()),
    "assistant_1": str(uuid.uuid4()),
    "assistant_2": str(uuid.uuid4()),
    "conversation_1": str(uuid.uuid4()),
    "conversation_2": str(uuid.uuid4()),
    "tool_1": str(uuid.uuid4()),
    "tool_2": str(uuid.uuid4()),
    "document_1": str(uuid.uuid4()),
    "document_2": str(uuid.uuid4()),
    "knowledge_1": str(uuid.uuid4()),
    "knowledge_2": str(uuid.uuid4()),
}

# Test Timestamps
TEST_TIMESTAMPS = {
    "past_1_hour": datetime.now(UTC) - timedelta(hours=1),
    "past_1_day": datetime.now(UTC) - timedelta(days=1),
    "past_1_week": datetime.now(UTC) - timedelta(weeks=1),
    "past_1_month": datetime.now(UTC) - timedelta(days=30),
    "future_1_hour": datetime.now(UTC) + timedelta(hours=1),
    "future_1_day": datetime.now(UTC) + timedelta(days=1),
}

# Test Configuration
TEST_CONFIG = {
    "database_url": "sqlite:///./test.db",
    "redis_url": "redis://localhost:6379",
    "weaviate_url": "http://localhost:8080",
    "secret_key": "test-secret-key-for-testing-purposes-only-32-chars",
    "debug": True,
    "environment": "test",
}

# Test File Paths
TEST_FILE_PATHS = {
    "pdf": "tests/fixtures/test_document.pdf",
    "text": "tests/fixtures/test_document.txt",
    "markdown": "tests/fixtures/test_document.md",
    "image": "tests/fixtures/test_image.jpg",
    "excel": "tests/fixtures/test_document.xlsx",
    "word": "tests/fixtures/test_document.docx",
}

# Test Search Queries
TEST_SEARCH_QUERIES = {
    "simple": "test query",
    "complex": "complex search query with multiple terms",
    "technical": "Python programming language tutorial",
    "business": "business strategy and planning",
    "empty": "",
    "whitespace": "   ",
    "special_chars": "test@#$%^&*()_+",
    "unicode": "test query with unicode: äöüß",
}

# Test Pagination
TEST_PAGINATION = {
    "page_1": {"page": 1, "size": 10},
    "page_2": {"page": 2, "size": 10},
    "large_page": {"page": 1, "size": 100},
    "small_page": {"page": 1, "size": 5},
    "invalid_page": {"page": 0, "size": 10},
    "invalid_size": {"page": 1, "size": 0},
}

# Test Filters
TEST_FILTERS = {
    "active_only": {"is_active": True},
    "public_only": {"is_public": True},
    "by_role": {"role": "user"},
    "by_status": {"status": "active"},
    "by_category": {"category": "utility"},
    "date_range": {
        "created_after": TEST_TIMESTAMPS["past_1_week"],
        "created_before": datetime.now(UTC),
    },
    "search": {"search": "test"},
    "tags": {"tags": ["test", "document"]},
}

# Test Sort Options
TEST_SORT_OPTIONS = {
    "name_asc": {"sort_by": "name", "sort_order": "asc"},
    "name_desc": {"sort_by": "name", "sort_order": "desc"},
    "created_asc": {"sort_by": "created_at", "sort_order": "asc"},
    "created_desc": {"sort_by": "created_at", "sort_order": "desc"},
    "updated_asc": {"sort_by": "updated_at", "sort_order": "asc"},
    "updated_desc": {"sort_by": "updated_at", "sort_order": "desc"},
}

# Test WebSocket Messages
TEST_WEBSOCKET_MESSAGES = {
    "ping": {"type": "ping", "data": {}},
    "pong": {"type": "pong", "data": {}},
    "chat_message": {
        "type": "chat_message",
        "data": {
            "content": "Hello from WebSocket",
            "role": "user",
            "conversation_id": TEST_UUIDS["conversation_1"],
        },
    },
    "assistant_response": {
        "type": "assistant_response",
        "data": {
            "content": "Hello! I'm here to help.",
            "role": "assistant",
            "conversation_id": TEST_UUIDS["conversation_1"],
        },
    },
    "error": {
        "type": "error",
        "data": {"message": "Test error message", "code": "TEST_ERROR"},
    },
}

# Test Performance Data
TEST_PERFORMANCE_DATA = {
    "api_request": {
        "endpoint": "/api/v1/users/",
        "method": "GET",
        "response_time": 0.15,
        "status_code": 200,
        "user_id": TEST_UUIDS["user_1"],
    },
    "database_query": {
        "query": "SELECT * FROM users WHERE id = :id",
        "execution_time": 0.05,
        "rows_returned": 1,
        "user_id": TEST_UUIDS["user_1"],
    },
    "cache_operation": {
        "operation": "get",
        "key": "user:profile:123",
        "execution_time": 0.001,
        "hit": True,
    },
}

# Test Security Data
TEST_SECURITY_DATA = {
    "weak_password": "password",
    "strong_password": "StrongPassword123!",
    "invalid_email": "invalid-email",
    "valid_email": "test@example.com",
    "sql_injection": "'; DROP TABLE users; --",
    "xss_payload": "<script>alert('XSS')</script>",
    "path_traversal": "../../../etc/passwd",
    "command_injection": "; rm -rf /",
}

# Test Rate Limiting
TEST_RATE_LIMITING = {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "burst_limit": 10,
    "window_size": 60,  # seconds
}

# Test CORS
TEST_CORS = {
    "allowed_origins": [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://test.example.com",
    ],
    "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allowed_headers": ["Content-Type", "Authorization"],
    "expose_headers": ["X-Total-Count"],
    "allow_credentials": True,
    "max_age": 3600,
}
