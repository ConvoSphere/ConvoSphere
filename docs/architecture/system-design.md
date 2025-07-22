# System Design

This document provides a comprehensive overview of the AI Chat Application's system design, including architecture patterns, data flow, scalability considerations, and design decisions.

## System Overview

The AI Chat Application is designed as a modern, scalable, full-stack application that provides real-time AI-powered chat capabilities with support for file processing, knowledge base management, and multi-provider AI integration.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Browser]
        Mobile[Mobile App]
        API_Client[API Client]
    end
    
    subgraph "Frontend Layer"
        React[React Frontend]
        WebSocket[WebSocket Client]
    end
    
    subgraph "API Gateway"
        Nginx[Nginx Load Balancer]
        Rate_Limit[Rate Limiting]
        Auth[Authentication]
    end
    
    subgraph "Backend Services"
        API[FastAPI Backend]
        WebSocket_Server[WebSocket Server]
        File_Processor[File Processor]
        AI_Orchestrator[AI Orchestrator]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
        Vector_DB[(Vector Database)]
        File_Storage[File Storage]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
        Anthropic[Anthropic API]
        Email[Email Service]
        Monitoring[Monitoring]
    end
    
    Web --> Nginx
    Mobile --> Nginx
    API_Client --> Nginx
    Nginx --> Rate_Limit
    Rate_Limit --> Auth
    Auth --> API
    Auth --> WebSocket_Server
    
    API --> PostgreSQL
    API --> Redis
    API --> Vector_DB
    API --> File_Processor
    File_Processor --> File_Storage
    API --> AI_Orchestrator
    AI_Orchestrator --> OpenAI
    AI_Orchestrator --> Anthropic
    
    WebSocket_Server --> Redis
    WebSocket_Server --> PostgreSQL
    
    API --> Email
    API --> Monitoring
```

## Core Design Principles

### 1. Microservices Architecture

The system is designed using a microservices approach with clear separation of concerns:

- **API Gateway**: Handles routing, authentication, and rate limiting
- **User Service**: Manages user accounts and authentication
- **Chat Service**: Handles conversation and message management
- **File Service**: Processes and stores uploaded files
- **AI Service**: Orchestrates AI provider interactions
- **Knowledge Service**: Manages knowledge base and vector search

### 2. Event-Driven Architecture

The system uses events for loose coupling between services:

```mermaid
sequenceDiagram
    participant User
    participant API
    participant ChatService
    participant AIService
    participant EventBus
    
    User->>API: Send Message
    API->>ChatService: Store Message
    ChatService->>EventBus: MessageCreated Event
    EventBus->>AIService: Process Message
    AIService->>API: AI Response
    API->>User: Return Response
```

### 3. CQRS Pattern

Command Query Responsibility Segregation is implemented for better performance:

- **Commands**: Write operations (create, update, delete)
- **Queries**: Read operations with optimized data access
- **Event Sourcing**: For audit trails and state reconstruction

## Data Architecture

### Database Design

#### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) DEFAULT 'general',
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Files table
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    is_processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base documents
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    file_id UUID REFERENCES files(id) ON DELETE SET NULL,
    vector_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Redis Data Structures

```python
# Session storage
sessions = {
    "session:user_id": {
        "user_id": "uuid",
        "expires_at": "timestamp",
        "last_activity": "timestamp"
    }
}

# Rate limiting
rate_limits = {
    "rate_limit:user_id": {
        "requests": "count",
        "window_start": "timestamp"
    }
}

# Real-time chat
chat_rooms = {
    "chat:conversation_id": {
        "participants": ["user_id1", "user_id2"],
        "last_message": "timestamp"
    }
}

# Cache
cache = {
    "user:user_id": "user_data",
    "conversation:conversation_id": "conversation_data",
    "file:file_id": "file_metadata"
}
```

### Vector Database Design

```python
# Weaviate schema for knowledge base
class KnowledgeDocument:
    properties = {
        "title": "string",
        "content": "text",
        "user_id": "uuid",
        "file_id": "uuid",
        "created_at": "date",
        "tags": "string[]",
        "category": "string"
    }
    vectorizer = "text2vec-openai"
    module_config = {
        "text2vec-openai": {
            "model": "ada",
            "modelVersion": "002",
            "type": "text"
        }
    }
```

## Service Architecture

### API Service

```python
# FastAPI application structure
app/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── dependencies.py        # Dependency injection
├── middleware/            # Custom middleware
│   ├── auth.py           # Authentication middleware
│   ├── rate_limit.py     # Rate limiting
│   └── cors.py           # CORS handling
├── api/                   # API routes
│   ├── v1/
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── users.py      # User management
│   │   ├── conversations.py # Chat endpoints
│   │   ├── files.py      # File upload/management
│   │   └── knowledge.py  # Knowledge base
│   └── websocket.py      # WebSocket endpoints
├── services/              # Business logic
│   ├── auth_service.py   # Authentication logic
│   ├── chat_service.py   # Chat management
│   ├── file_service.py   # File processing
│   ├── ai_service.py     # AI provider integration
│   └── knowledge_service.py # Knowledge base
├── models/                # Data models
│   ├── user.py           # User models
│   ├── conversation.py   # Chat models
│   └── file.py           # File models
└── utils/                 # Utilities
    ├── security.py       # Security utilities
    ├── validators.py     # Data validation
    └── helpers.py        # Helper functions
```

### AI Orchestration Service

```python
class AIOrchestrator:
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'google': GoogleAIProvider()
        }
        self.model_selector = ModelSelector()
        self.fallback_chain = FallbackChain()
    
    async def generate_response(self, message, context, user_preferences):
        # Select best model based on user preferences and cost
        model = self.model_selector.select_model(user_preferences)
        
        # Try primary model
        try:
            response = await self.providers[model.provider].generate(
                message, context, model.config
            )
            return response
        except Exception as e:
            # Fallback to alternative models
            return await self.fallback_chain.execute(message, context, e)
```

## Scalability Design

### Horizontal Scaling

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Load Balancer]
    end
    
    subgraph "API Instances"
        API1[API Instance 1]
        API2[API Instance 2]
        API3[API Instance 3]
    end
    
    subgraph "Database Cluster"
        DB1[(Primary DB)]
        DB2[(Replica 1)]
        DB3[(Replica 2)]
    end
    
    subgraph "Cache Cluster"
        Redis1[(Redis 1)]
        Redis2[(Redis 2)]
        Redis3[(Redis 3)]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> DB1
    API2 --> DB1
    API3 --> DB1
    
    DB1 --> DB2
    DB1 --> DB3
    
    API1 --> Redis1
    API2 --> Redis2
    API3 --> Redis3
```

### Database Scaling

#### Read Replicas

```sql
-- Primary database for writes
-- Replica databases for reads
-- Connection pooling for efficient resource usage

-- Example connection string with read replicas
DATABASE_URL=postgresql://user:pass@primary:5432/db
DATABASE_READ_REPLICAS=[
    "postgresql://user:pass@replica1:5432/db",
    "postgresql://user:pass@replica2:5432/db"
]
```

#### Sharding Strategy

```python
# User-based sharding
def get_shard_key(user_id: str) -> str:
    return f"shard_{hash(user_id) % SHARD_COUNT}"

# Conversation-based sharding
def get_conversation_shard(conversation_id: str) -> str:
    return f"shard_{hash(conversation_id) % SHARD_COUNT}"
```

### Caching Strategy

```python
# Multi-level caching
class CacheManager:
    def __init__(self):
        self.l1_cache = {}  # In-memory cache
        self.l2_cache = Redis()  # Distributed cache
        self.l3_cache = Database()  # Persistent storage
    
    async def get(self, key: str):
        # Try L1 cache first
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # Try L2 cache
        value = await self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value
            return value
        
        # Get from L3 cache
        value = await self.l3_cache.get(key)
        if value:
            await self.l2_cache.set(key, value, ttl=3600)
            self.l1_cache[key] = value
            return value
        
        return None
```

## Security Design

### Authentication & Authorization

```python
# JWT-based authentication
class JWTAuth:
    def create_token(self, user_id: str, permissions: List[str]) -> str:
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    def verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Role-based access control
class RBAC:
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        user_roles = self.get_user_roles(user_id)
        required_permissions = self.get_required_permissions(resource, action)
        return any(role in user_roles for role in required_permissions)
```

### Data Protection

```python
# Data encryption
class DataEncryption:
    def encrypt_sensitive_data(self, data: str) -> str:
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        data = base64.b64decode(encrypted_data)
        nonce = data[:12]
        tag = data[12:28]
        ciphertext = data[28:]
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()

# Input validation and sanitization
class InputValidator:
    def validate_message(self, content: str) -> str:
        # Remove potentially dangerous content
        sanitized = bleach.clean(content, tags=ALLOWED_TAGS, strip=True)
        if len(sanitized) > MAX_MESSAGE_LENGTH:
            raise ValueError("Message too long")
        return sanitized
```

## Performance Design

### Response Time Optimization

```python
# Async processing for non-blocking operations
class AsyncProcessor:
    async def process_message(self, message: str) -> str:
        # Process message asynchronously
        tasks = [
            self.validate_message(message),
            self.enrich_context(message),
            self.prepare_ai_request(message)
        ]
        results = await asyncio.gather(*tasks)
        return self.combine_results(results)

# Connection pooling
class DatabasePool:
    def __init__(self):
        self.pool = asyncpg.create_pool(
            DATABASE_URL,
            min_size=10,
            max_size=50,
            command_timeout=60
        )
    
    async def get_connection(self):
        return await self.pool.acquire()
```

### Throughput Optimization

```python
# Batch processing
class BatchProcessor:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.queue = asyncio.Queue()
    
    async def process_batch(self):
        batch = []
        while len(batch) < self.batch_size:
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                batch.append(item)
            except asyncio.TimeoutError:
                break
        
        if batch:
            await self.process_items(batch)

# Background task processing
class BackgroundTasks:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.workers = []
    
    async def start_workers(self, num_workers: int = 5):
        for _ in range(num_workers):
            worker = asyncio.create_task(self.worker())
            self.workers.append(worker)
    
    async def worker(self):
        while True:
            task = await self.task_queue.get()
            try:
                await self.process_task(task)
            except Exception as e:
                logger.error(f"Task processing error: {e}")
            finally:
                self.task_queue.task_done()
```

## Monitoring & Observability

### Metrics Collection

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Business metrics
MESSAGE_COUNT = Counter('messages_total', 'Total messages sent')
AI_RESPONSE_TIME = Histogram('ai_response_time_seconds', 'AI response time')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')

# System metrics
DATABASE_CONNECTIONS = Gauge('database_connections', 'Active database connections')
REDIS_MEMORY_USAGE = Gauge('redis_memory_bytes', 'Redis memory usage')
```

### Logging Strategy

```python
# Structured logging
import structlog

logger = structlog.get_logger()

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        "http_request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        user_id=request.state.user_id if hasattr(request.state, 'user_id') else None
    )
    
    return response
```

### Health Checks

```python
# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "ai_providers": await check_ai_providers(),
        "file_storage": await check_file_storage()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Deployment Architecture

### Container Orchestration

```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-chat-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-chat-api
  template:
    metadata:
      labels:
        app: ai-chat-api
    spec:
      containers:
      - name: api
        image: ai-chat-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ai-chat-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### CI/CD Pipeline

```yaml
# GitHub Actions workflow
name: Deploy AI Chat Application

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run tests
      run: |
        pip install -r requirements.txt
        pytest tests/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker image
      run: |
        docker build -t ai-chat-api:${{ github.sha }} .
        docker push ai-chat-api:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        kubectl set image deployment/ai-chat-api api=ai-chat-api:${{ github.sha }}
```

## Future Considerations

### Scalability Improvements

1. **Microservices Migration**: Break down monolithic API into smaller services
2. **Event Sourcing**: Implement event sourcing for better audit trails
3. **CQRS**: Separate read and write models for better performance
4. **GraphQL**: Add GraphQL API for flexible data querying

### Technology Upgrades

1. **Database**: Consider migrating to distributed databases like CockroachDB
2. **Cache**: Implement multi-region Redis clusters
3. **Search**: Add Elasticsearch for advanced search capabilities
4. **AI**: Integrate more AI providers and models

### Performance Optimizations

1. **CDN**: Implement content delivery network for static assets
2. **Edge Computing**: Deploy edge functions for low-latency responses
3. **Streaming**: Implement streaming responses for real-time AI interactions
4. **Compression**: Add response compression for better bandwidth usage

## Conclusion

The AI Chat Application is designed with scalability, security, and performance in mind. The architecture supports horizontal scaling, implements robust security measures, and provides comprehensive monitoring capabilities. The system can handle high loads while maintaining low latency and high availability.

For implementation details, see the [Backend Architecture](backend.md) and [Frontend Architecture](frontend.md) documents.