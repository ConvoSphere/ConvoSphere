# API Documentation

## Overview

The AI Assistant Platform provides a comprehensive REST API for managing assistants, conversations, tools, and users.

## Base URL

- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

## API Endpoints Overview

The API is organized into the following main categories:

- **Authentication** (`/auth`) - User authentication and SSO
- **User Management** (`/users`) - User profiles and administration
- **Assistant Management** (`/assistants`) - AI assistant configuration
- **Agent Management** (`/agents`) - Agent operations
- **Conversations** (`/conversations`) - Conversation management
- **Chat** (`/chat`) - Real-time messaging
- **WebSocket** (`/ws`) - Real-time communication
- **Knowledge Base** (`/knowledge`) - Document management
- **Tools** (`/tools`) - Tool management
- **MCP Tools** (`/mcp`) - Model Context Protocol tools
- **AI** (`/ai`) - AI service operations
- **RAG** (`/rag`) - Retrieval-Augmented Generation
- **Search** (`/search`) - Search functionality
- **Conversation Intelligence** (`/intelligence`) - Analytics and insights
- **Domain Groups** (`/domain-groups`) - Enterprise user management
- **Audit** (`/audit`) - Audit logging
- **Health** (`/health`) - System health monitoring
- **Hybrid Mode** (`/hybrid-mode`) - Hybrid AI operations
- **Monitoring** (`/monitoring`) - System monitoring
- **Logs** (`/logs`) - Log management
- **Statistics** (`/statistics`) - Dashboard statistics
- **Storage** (`/storage`) - File storage operations

## Authentication

All API endpoints require authentication using JWT tokens.

### Login

```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### Using Tokens

Include the token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/login
Authenticate user and get access token.

#### POST /auth/refresh
Refresh access token using refresh token.

#### POST /auth/logout
Logout user and invalidate tokens.

#### POST /auth/register
Register new user account.

#### GET /auth/me
Get current user information.

#### GET /auth/sso/providers
Get available SSO providers.

#### GET /auth/sso/login/{provider}
Initiate SSO login with specific provider.

#### GET /auth/sso/callback/{provider}
Handle SSO callback from provider.

#### POST /auth/sso/link/{provider}
Link SSO account to existing user.

#### GET /auth/sso/metadata
Get SAML metadata for SSO configuration.

### Users

#### GET /users/me
Get current user profile.

#### PUT /users/me
Update current user profile.

#### GET /users
List all users (admin only).

#### GET /users/{user_id}
Get specific user details.

#### PUT /users/{user_id}
Update user (admin only).

#### DELETE /users/{user_id}
Delete user (admin only).

### Assistants

#### GET /assistants
List all assistants.

Query parameters:
- `page`: Page number (default: 1)
- `size`: Page size (default: 20)
- `status`: Filter by status (active, inactive, draft)
- `category`: Filter by category

Response:
```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Assistant Name",
            "description": "Assistant description",
            "personality": "Friendly and helpful",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
}
```

#### POST /assistants
Create new assistant.

Request:
```json
{
    "name": "My Assistant",
    "description": "A helpful AI assistant",
    "personality": "Friendly and professional",
    "system_prompt": "You are a helpful assistant...",
    "tools": ["web_search", "file_upload"],
    "model": "gpt-4",
    "temperature": 0.7
}
```

#### GET /assistants/{assistant_id}
Get specific assistant details.

#### PUT /assistants/{assistant_id}
Update assistant.

#### DELETE /assistants/{assistant_id}
Delete assistant.

### Conversations

#### GET /conversations
List user conversations.

Query parameters:
- `page`: Page number (default: 1)
- `size`: Page size (default: 20)
- `assistant_id`: Filter by assistant

#### POST /conversations
Start new conversation.

Request:
```json
{
    "assistant_id": "uuid",
    "title": "Conversation Title",
    "initial_message": "Hello, how can you help me?"
}
```

#### GET /conversations/{conversation_id}
Get conversation details and messages.

#### POST /conversations/{conversation_id}/messages
Send message to conversation.

Request:
```json
{
    "content": "User message",
    "attachments": [
        {
            "type": "file",
            "url": "https://example.com/file.pdf"
        }
    ]
}
```

#### DELETE /conversations/{conversation_id}
Delete conversation.

### Chat

#### POST /chat/conversations
Create new conversation.

#### GET /chat/conversations
List user conversations.

#### POST /chat/conversations/{conversation_id}/messages
Send message to conversation.

#### GET /chat/conversations/{conversation_id}/messages
Get conversation messages.

#### GET /chat/conversations/{conversation_id}/mode/status
Get conversation mode status.

### Tools

#### GET /tools
List available tools.

#### POST /tools/{tool_id}/execute
Execute a specific tool.

### MCP Tools

#### GET /mcp/tools
List available MCP tools.

#### POST /mcp/tools/{tool_id}/execute
Execute MCP tool.

#### GET /mcp/providers
List MCP providers.

### Knowledge Base

#### GET /knowledge/documents
List knowledge base documents with advanced filtering and pagination.

**Query Parameters:**
- `skip` (int): Number of documents to skip (default: 0)
- `limit` (int): Number of documents to return (default: 100, max: 1000)
- `status` (string): Filter by document status (uploaded, processing, processed, error, reprocessing)
- `document_type` (string): Filter by document type (pdf, document, text, spreadsheet, presentation, image, audio, video, code, other)
- `author` (string): Filter by author
- `year` (int): Filter by year
- `language` (string): Filter by language (ISO code)
- `tag_names` (string): Comma-separated list of tag names
- `search_type` (string): Search type for filtering (hybrid, semantic, keyword)
- `sort_by` (string): Sort field (created_at, updated_at, title, file_size)
- `sort_order` (string): Sort order (asc, desc)

#### POST /knowledge/documents
Upload new document with metadata.

**Form Data:**
- `file` (file): Document file to upload
- `title` (string): Document title
- `description` (string, optional): Document description
- `tags` (string, optional): JSON array of tags
- `processing_options` (string, optional): JSON object with processing options

#### POST /knowledge/documents/upload-advanced
Upload document with advanced processing options.

**Form Data:**
- `file` (file): Document file to upload
- `title` (string): Document title
- `description` (string, optional): Document description
- `tags` (string, optional): JSON array of tags
- `engine` (string): Processing engine (auto, traditional, docling)
- `processing_options` (string, optional): JSON object with processing options

#### GET /knowledge/documents/{document_id}
Get document details by ID.

#### PUT /knowledge/documents/{document_id}
Update document metadata.

**Request Body:**
```json
{
    "title": "Updated Title",
    "description": "Updated description",
    "author": "Author Name",
    "source": "Source URL",
    "year": 2024,
    "language": "en",
    "keywords": ["keyword1", "keyword2"],
    "tags": ["tag1", "tag2"]
}
```

#### DELETE /knowledge/documents/{document_id}
Delete document and all associated chunks.

#### POST /knowledge/documents/{document_id}/process
Process document (extract text, create chunks, generate embeddings).

#### POST /knowledge/documents/{document_id}/reprocess
Reprocess document with new options.

**Request Body:**
```json
{
    "chunk_size": 500,
    "chunk_overlap": 50,
    "embedding_model": "text-embedding-ada-002",
    "processing_engine": "traditional"
}
```

#### GET /knowledge/documents/{document_id}/download
Download original document file.

### Document Processing

#### GET /knowledge/processing/jobs
Get processing jobs for current user.

**Query Parameters:**
- `status` (string): Filter by job status (pending, running, completed, failed)
- `limit` (int): Number of jobs to return (default: 50)

#### POST /knowledge/processing/jobs
Create new processing job.

**Request Body:**
```json
{
    "document_id": "uuid",
    "job_type": "process",
    "priority": 0,
    "processing_options": {
        "chunk_size": 500,
        "embedding_model": "text-embedding-ada-002"
    }
}
```

### Tags

#### GET /knowledge/tags
Get all tags for current user's documents.

#### GET /knowledge/tags/search
Search tags by name.

**Query Parameters:**
- `q` (string): Search query
- `limit` (int): Number of results (default: 20)

#### POST /knowledge/tags
Create new tag.

**Request Body:**
```json
{
    "name": "Tag Name",
    "description": "Tag description",
    "color": "#FF5733"
}
```

#### DELETE /knowledge/tags/{tag_id}
Delete tag (if not used by any documents).

### Statistics

#### GET /knowledge/stats
Get knowledge base statistics.

**Response:**
```json
{
    "total_documents": 150,
    "total_chunks": 2500,
    "total_tokens": 125000,
    "documents_by_status": {
        "processed": 120,
        "processing": 5,
        "error": 3
    },
    "documents_by_type": {
        "pdf": 80,
        "document": 40,
        "text": 30
    },
    "storage_used": 104857600,
    "last_processed": "2024-01-15T10:30:00Z"
}
```

### AI Service

#### POST /ai/chat/completion
Generate chat completion using the modular AI service.

**Request Body:**
```json
{
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ],
    "user_id": "user123",
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "use_knowledge_base": true,
    "use_tools": true,
    "max_context_chunks": 5
}
```

**Response:**
```json
{
    "content": "Hello! I'm doing well, thank you for asking. How can I help you today?",
    "model": "gpt-4",
    "usage": {
        "input_tokens": 10,
        "output_tokens": 15
    },
    "finish_reason": "stop",
    "request_id": "req-123456"
}
```

#### POST /ai/chat/completion/stream
Generate streaming chat completion.

**Request Body:** Same as `/ai/chat/completion`

**Response:** Server-Sent Events stream with chunks:
```
data: {"content": "Hello", "model": "gpt-4", "finish_reason": null, "request_id": "req-123456"}

data: {"content": " world", "model": "gpt-4", "finish_reason": null, "request_id": "req-123456"}

data: {"content": "!", "model": "gpt-4", "finish_reason": "stop", "request_id": "req-123456"}
```

#### POST /ai/embeddings
Generate embeddings for text.

**Request Body:**
```json
{
    "texts": ["Hello world", "Test embedding"],
    "provider": "openai",
    "model": "text-embedding-ada-002"
}
```

**Response:**
```json
{
    "embeddings": [
        [0.1, 0.2, 0.3, ...],
        [0.4, 0.5, 0.6, ...]
    ],
    "model": "text-embedding-ada-002",
    "usage": {
        "input_tokens": 10
    },
    "request_id": "req-123456"
}
```

#### POST /ai/tools/execute
Execute tools based on AI response.

**Request Body:**
```json
{
    "ai_response": "I'll help you calculate that. <tool_call><tool_name>calculator</tool_name><parameters>{\"expression\": \"2 + 2\"}</parameters></tool_call>",
    "user_id": "user123"
}
```

**Response:**
```json
[
    {
        "tool": "calculator",
        "result": "4",
        "execution_time": 0.05
    }
]
```

#### GET /ai/providers
Get available AI providers.

**Response:**
```json
{
    "providers": ["openai", "anthropic", "google", "azure"]
}
```

#### GET /ai/models/{provider}
Get available models for a provider.

**Response:**
```json
{
    "models": [
        {
            "name": "gpt-4",
            "type": "chat",
            "max_tokens": 8192,
            "cost_per_1k_input": 0.03,
            "cost_per_1k_output": 0.06
        },
        {
            "name": "gpt-3.5-turbo",
            "type": "chat",
            "max_tokens": 4096,
            "cost_per_1k_input": 0.0015,
            "cost_per_1k_output": 0.002
        }
    ]
}
```

#### GET /ai/costs/summary/{user_id}
Get cost summary for a user.

**Query Parameters:**
- `days` (int): Number of days to include (default: 30)

**Response:**
```json
{
    "total_cost": 0.15,
    "total_tokens": 500,
    "daily_cost": 0.05,
    "monthly_cost": 0.15,
    "cost_by_model": {
        "gpt-4": 0.10,
        "gpt-3.5-turbo": 0.05
    }
}
```

#### GET /ai/costs/daily/{user_id}
Get daily cost breakdown.

**Query Parameters:**
- `days` (int): Number of days to include (default: 7)

**Response:**
```json
[
    {
        "date": "2024-01-01",
        "cost": 0.02,
        "tokens": 100,
        "requests": 5
    },
    {
        "date": "2024-01-02",
        "cost": 0.03,
        "tokens": 150,
        "requests": 8
    }
]
```

#### GET /ai/usage/stats/{user_id}
Get model usage statistics.

**Query Parameters:**
- `days` (int): Number of days to include (default: 30)

**Response:**
```json
{
    "gpt-4": {
        "total_requests": 50,
        "total_tokens": 2500,
        "total_cost": 0.075,
        "avg_tokens_per_request": 50
    },
    "gpt-3.5-turbo": {
        "total_requests": 100,
        "total_tokens": 3000,
        "total_cost": 0.045,
        "avg_tokens_per_request": 30
    }
}
```

### RAG (Retrieval-Augmented Generation)

#### POST /rag/query
Query knowledge base with RAG using configurable strategies.

**Request Body:**
```json
{
    "query": "What is machine learning?",
    "conversation_id": "uuid",
    "config_id": "default",
    "max_results": 5,
    "similarity_threshold": 0.7,
    "include_sources": true,
    "include_metadata": true
}
```

#### GET /rag/context/{conversation_id}
Get RAG context for conversation.

**Query Parameters:**
- `limit` (int): Number of context items (default: 10)
- `include_metadata` (boolean): Include document metadata (default: true)

#### POST /rag/configs
Create new RAG configuration.

**Request Body:**
```json
{
    "name": "Custom RAG Config",
    "description": "Configuration for technical documents",
    "strategy": "hybrid",
    "max_context_length": 4000,
    "max_results": 5,
    "similarity_threshold": 0.7,
    "embedding_model": "text-embedding-3-small",
    "ranking_method": "relevance",
    "cache_results": true
}
```

#### GET /rag/configs
List available RAG configurations.

#### PUT /rag/configs/{config_id}
Update RAG configuration.

#### DELETE /rag/configs/{config_id}
Delete RAG configuration.

#### GET /rag/metrics
Get RAG performance metrics.

**Response:**
```json
{
    "total_requests": 1250,
    "successful_requests": 1200,
    "failed_requests": 50,
    "avg_retrieval_time": 0.85,
    "avg_processing_time": 1.2,
    "avg_total_time": 2.05,
    "avg_similarity_score": 0.78,
    "avg_relevance_score": 0.82,
    "cache_hit_rate": 0.65,
    "source_usage": {
        "knowledge_base": 80,
        "conversations": 20
    },
    "strategy_usage": {
        "semantic": 40,
        "hybrid": 35,
        "keyword": 15,
        "contextual": 10
    }
}
```

### Search

#### POST /search
Perform advanced search with multiple search types and filtering.

**Request Body:**
```json
{
    "query": "search query",
    "search_type": "hybrid",
    "filters": [
        {
            "field": "document_type",
            "operator": "equals",
            "value": "pdf",
            "boost": 1.0
        }
    ],
    "facets": [
        {
            "field": "author",
            "size": 10,
            "min_count": 1
        }
    ],
    "sort_by": "relevance",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20,
    "include_highlights": true,
    "include_facets": true
}
```

#### POST /search/semantic
Perform semantic search using embeddings.

**Request Body:**
```json
{
    "query": "search query",
    "filters": [],
    "sort_by": "relevance",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20
}
```

#### POST /search/hybrid
Perform hybrid search combining semantic and keyword search.

**Request Body:**
```json
{
    "query": "search query",
    "filters": [],
    "sort_by": "relevance",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20
}
```

#### POST /search/full-text
Perform full-text search with exact phrase matching.

**Request Body:**
```json
{
    "query": "exact phrase to search",
    "filters": [],
    "sort_by": "relevance",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20
}
```

#### POST /search/faceted
Perform faceted search with aggregation.

**Request Body:**
```json
{
    "query": "search query",
    "facets": [
        {
            "field": "document_type",
            "size": 10,
            "min_count": 1
        },
        {
            "field": "author",
            "size": 5,
            "min_count": 2
        }
    ],
    "filters": [],
    "sort_by": "relevance",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20
}
```

#### POST /search/fuzzy
Perform fuzzy search with typo tolerance.

**Request Body:**
```json
{
    "query": "search query with possible typos",
    "filters": [],
    "sort_by": "relevance",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20
}
```

#### GET /search/suggestions
Get search suggestions and autocomplete.

**Query Parameters:**
- `query` (string): Partial search query
- `limit` (int): Number of suggestions (default: 10, max: 50)

#### GET /search/autocomplete
Get autocomplete suggestions.

**Query Parameters:**
- `query` (string): Partial search query
- `limit` (int): Number of suggestions (default: 5, max: 20)

#### GET /search/trending
Get trending search queries.

**Query Parameters:**
- `days` (int): Number of days to analyze (default: 7, max: 30)
- `limit` (int): Number of trending queries (default: 10, max: 50)

#### GET /search/analytics
Get search analytics and statistics.

**Query Parameters:**
- `days` (int): Number of days to analyze (default: 30, max: 365)

**Response:**
```json
{
    "total_searches": 1250,
    "unique_users": 45,
    "avg_results_per_search": 8.5,
    "popular_queries": [
        {"query": "AI", "count": 45},
        {"query": "machine learning", "count": 32}
    ],
    "search_types": {
        "semantic": 60,
        "hybrid": 30,
        "keyword": 10
    },
    "avg_search_time": 0.85
}
```

### Domain Groups

#### GET /domain-groups
List domain groups.

#### POST /domain-groups
Create domain group.

#### GET /domain-groups/{group_id}
Get domain group details.

### Conversation Intelligence

#### GET /intelligence/analytics/{conversation_id}
Get conversation analytics.

#### POST /intelligence/summarize
Summarize conversation.

### Hybrid Mode

#### POST /hybrid-mode/switch
Switch conversation mode.

#### GET /hybrid-mode/status/{conversation_id}
Get hybrid mode status.

### Audit

#### GET /audit/logs
Get audit logs.

#### GET /audit/logs/{user_id}
Get user-specific audit logs.

### Health

#### GET /health
System health check.

#### GET /health/detailed
Detailed system health information.

### WebSocket

#### WebSocket /ws/
General WebSocket endpoint.

#### WebSocket /ws/{conversation_id}
Conversation-specific WebSocket endpoint.

### Tools (Detailed)

#### GET /tools
List available tools.

Response:
```json
{
    "items": [
        {
            "id": "web_search",
            "name": "Web Search",
            "description": "Search the web for information",
            "category": "search",
            "parameters": {
                "query": {
                    "type": "string",
                    "required": true,
                    "description": "Search query"
                }
            }
        }
    ]
}
```

#### GET /tools/{tool_id}
Get specific tool details.

#### POST /tools
Create custom tool (admin only).

### Health

#### GET /health
Basic health check.

#### GET /health/detailed
Detailed health check with component status.

## Error Handling

### Error Response Format

```json
{
    "detail": "Error message",
    "status_code": 400,
    "error_code": "VALIDATION_ERROR"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `422`: Validation Error - Invalid data format
- `500`: Internal Server Error - Server error

### Rate Limiting

- API endpoints: 100 requests per minute
- Authentication endpoints: 10 requests per minute

## WebSocket Support

### Real-time Updates

Connect to WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Message Types

- `conversation_update`: New message in conversation
- `assistant_status`: Assistant status change
- `system_notification`: System notifications

## SDK Examples

### Python SDK

```python
from ai_assistant_sdk import AIAssistantClient

client = AIAssistantClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your-api-key"
)

# List assistants
assistants = client.assistants.list()

# Start conversation
conversation = client.conversations.create(
    assistant_id="uuid",
    message="Hello!"
)
```

### JavaScript SDK

```javascript
import { AIAssistantClient } from '@ai-assistant/sdk';

const client = new AIAssistantClient({
    baseUrl: 'http://localhost:8000/api/v1',
    apiKey: 'your-api-key'
});

// List assistants
const assistants = await client.assistants.list();

// Start conversation
const conversation = await client.conversations.create({
    assistantId: 'uuid',
    message: 'Hello!'
});
```

## Pagination

All list endpoints support pagination:

```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5,
    "has_next": true,
    "has_prev": false
}
```

## Filtering and Sorting

### Filtering

Use query parameters for filtering:

```
GET /assistants?status=active&category=general
```

### Sorting

Use `sort` parameter:

```
GET /assistants?sort=name:asc
GET /assistants?sort=created_at:desc
```

## File Upload

### Upload File

```http
POST /files/upload
Content-Type: multipart/form-data

file: <file_data>
```

### File Types Supported

- Images: PNG, JPG, GIF, WebP
- Documents: PDF, DOC, DOCX, TXT
- Data: CSV, JSON, XML
- Archives: ZIP, RAR

### File Size Limits

- Images: 10MB
- Documents: 50MB
- Data files: 100MB

## Webhooks

### Configure Webhook

```http
POST /webhooks
{
    "url": "https://your-domain.com/webhook",
    "events": ["conversation.created", "message.received"],
    "secret": "webhook-secret"
}
```

### Webhook Events

- `conversation.created`: New conversation started
- `conversation.updated`: Conversation updated
- `message.received`: New message received
- `assistant.status_changed`: Assistant status changed
- `user.created`: New user registered
- `user.updated`: User profile updated

### Webhook Payload

```json
{
    "event": "conversation.created",
    "timestamp": "2024-01-01T00:00:00Z",
    "data": {
        "conversation_id": "uuid",
        "assistant_id": "uuid",
        "user_id": "uuid"
    }
}
``` 