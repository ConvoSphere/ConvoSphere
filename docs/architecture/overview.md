# Architecture Overview

The AI Chat Application is built with a modern, scalable architecture that separates concerns and provides excellent performance, security, and maintainability.

## 🏗️ System Architecture

The application follows a **microservices-inspired** architecture with clear separation between frontend, backend, and external services.

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Browser]
        Mobile[Mobile App]
        API_Client[API Client]
    end
    
    subgraph "Frontend (React)"
        UI[React UI Components]
        State[Zustand State Management]
        Router[React Router]
        WS_Client[WebSocket Client]
    end
    
    subgraph "Backend (FastAPI)"
        API[REST API Gateway]
        WS_Server[WebSocket Server]
        Auth[Authentication Service]
        Chat[Chat Service]
        AI[AI Integration Service]
        Search[Search Service]
        File[File Processing Service]
        User[User Management Service]
    end
    
    subgraph "External Services"
        AI_Providers[AI Providers<br/>OpenAI, Anthropic, etc.]
        Storage[File Storage<br/>Local/S3/Cloud]
        VectorDB[Vector Database<br/>Weaviate]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Primary Database)]
        Redis[(Redis<br/>Cache & Sessions)]
        Weaviate[(Weaviate<br/>Vector Database)]
    end
    
    Web --> UI
    Mobile --> API_Client
    API_Client --> API
    
    UI --> State
    UI --> Router
    UI --> WS_Client
    
    WS_Client --> WS_Server
    API --> Auth
    API --> Chat
    API --> AI
    API --> Search
    API --> File
    API --> User
    
    Chat --> WS_Server
    AI --> AI_Providers
    Search --> VectorDB
    File --> Storage
    
    Auth --> PG
    Chat --> PG
    User --> PG
    File --> PG
    
    Auth --> Redis
    Chat --> Redis
    Search --> Weaviate
```

## 🔄 Data Flow

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant R as Redis
    
    U->>F: Enter credentials
    F->>B: POST /auth/login
    B->>DB: Verify user credentials
    B->>R: Store session data
    B->>F: Return JWT tokens
    F->>F: Store tokens in state
    F->>U: Redirect to chat
```

### Chat Message Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant WS as WebSocket
    participant B as Backend
    participant AI as AI Service
    participant DB as Database
    
    U->>F: Send message
    F->>WS: Send message via WebSocket
    WS->>B: Process message
    B->>DB: Store message
    B->>AI: Generate response
    AI->>B: Return AI response
    B->>DB: Store AI response
    B->>WS: Send response
    WS->>F: Update UI in real-time
    F->>U: Display response
```

### File Upload Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant P as File Processor
    participant V as Vector DB
    participant S as Storage
    
    U->>F: Upload file
    F->>B: POST /files/upload
    B->>S: Store file
    B->>P: Process file content
    P->>P: Extract text & chunk
    P->>V: Create embeddings
    P->>V: Store vectors
    B->>F: Return file info
    F->>U: Show upload success
```

## 🏛️ Component Architecture

### Backend Components

```mermaid
graph LR
    subgraph "API Layer"
        Router[FastAPI Router]
        Middleware[Middleware Stack]
    end
    
    subgraph "Service Layer"
        Auth_Service[Auth Service]
        Chat_Service[Chat Service]
        AI_Service[AI Service]
        Search_Service[Search Service]
        File_Service[File Service]
        User_Service[User Service]
    end
    
    subgraph "Data Layer"
        Models[SQLAlchemy Models]
        Repos[Repository Pattern]
        Migrations[Alembic Migrations]
    end
    
    subgraph "External Integrations"
        LiteLLM[LiteLLM Client]
        Weaviate_Client[Weaviate Client]
        Redis_Client[Redis Client]
    end
    
    Router --> Middleware
    Middleware --> Auth_Service
    Middleware --> Chat_Service
    Middleware --> AI_Service
    Middleware --> Search_Service
    Middleware --> File_Service
    Middleware --> User_Service
    
    Auth_Service --> Models
    Chat_Service --> Models
    AI_Service --> LiteLLM
    Search_Service --> Weaviate_Client
    File_Service --> Models
    User_Service --> Models
    
    Models --> Repos
    Repos --> Migrations
```

### Frontend Components

```mermaid
graph LR
    subgraph "UI Layer"
        Pages[Page Components]
        Components[Reusable Components]
        Layout[Layout Components]
    end
    
    subgraph "State Management"
        Store[Zustand Store]
        Actions[Store Actions]
        Selectors[Store Selectors]
    end
    
    subgraph "Service Layer"
        API_Service[API Service]
        WS_Service[WebSocket Service]
        Auth_Service[Auth Service]
        File_Service[File Service]
    end
    
    subgraph "Utilities"
        Utils[Utility Functions]
        Hooks[Custom Hooks]
        Types[TypeScript Types]
    end
    
    Pages --> Components
    Components --> Layout
    
    Pages --> Store
    Components --> Store
    
    Store --> Actions
    Store --> Selectors
    
    Actions --> API_Service
    Actions --> WS_Service
    Actions --> Auth_Service
    Actions --> File_Service
    
    API_Service --> Utils
    WS_Service --> Utils
    Auth_Service --> Utils
    File_Service --> Utils
    
    Utils --> Hooks
    Utils --> Types
```

## 🗄️ Database Design

### Entity Relationship Diagram

```mermaid
erDiagram
    users {
        uuid id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        string avatar_url
        boolean is_active
        string role
        timestamp created_at
        timestamp updated_at
    }
    
    conversations {
        uuid id PK
        uuid user_id FK
        string title
        string description
        json metadata
        timestamp created_at
        timestamp updated_at
    }
    
    messages {
        uuid id PK
        uuid conversation_id FK
        uuid user_id FK
        string content
        string message_type
        json metadata
        timestamp created_at
        timestamp updated_at
    }
    
    files {
        uuid id PK
        uuid user_id FK
        string filename
        string file_path
        string file_type
        integer file_size
        json metadata
        timestamp created_at
        timestamp updated_at
    }
    
    knowledge_chunks {
        uuid id PK
        uuid file_id FK
        string content
        vector embedding
        json metadata
        timestamp created_at
    }
    
    users ||--o{ conversations : "has"
    users ||--o{ messages : "sends"
    users ||--o{ files : "uploads"
    conversations ||--o{ messages : "contains"
    files ||--o{ knowledge_chunks : "generates"
```

## 🔒 Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph "Client Security"
        HTTPS[HTTPS/TLS]
        CSP[Content Security Policy]
        CORS[CORS Headers]
    end
    
    subgraph "Authentication"
        JWT[JWT Tokens]
        Refresh[Refresh Tokens]
        Rate_Limit[Rate Limiting]
    end
    
    subgraph "Authorization"
        RBAC[Role-Based Access Control]
        Permissions[Permission Checks]
        Audit[Audit Logging]
    end
    
    subgraph "Data Security"
        Encryption[Data Encryption]
        Validation[Input Validation]
        Sanitization[Output Sanitization]
    end
    
    HTTPS --> JWT
    JWT --> RBAC
    RBAC --> Encryption
    
    CSP --> Validation
    CORS --> Sanitization
    Rate_Limit --> Audit
```

## 📊 Performance Architecture

### Caching Strategy

```mermaid
graph LR
    subgraph "Client Cache"
        Browser[Browser Cache]
        Local[Local Storage]
        Session[Session Storage]
    end
    
    subgraph "Application Cache"
        Redis[Redis Cache]
        Memory[In-Memory Cache]
    end
    
    subgraph "Database Cache"
        Query[Query Cache]
        Connection[Connection Pool]
    end
    
    Browser --> Redis
    Local --> Memory
    Session --> Redis
    Redis --> Query
    Memory --> Connection
```

### Load Balancing

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX/HAProxy]
    end
    
    subgraph "Application Instances"
        App1[App Instance 1]
        App2[App Instance 2]
        App3[App Instance 3]
    end
    
    subgraph "Database Cluster"
        Master[(Master DB)]
        Slave1[(Slave DB 1)]
        Slave2[(Slave DB 2)]
    end
    
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> Master
    App2 --> Master
    App3 --> Master
    
    Master --> Slave1
    Master --> Slave2
```

## 🔧 Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.104+ | Modern Python web framework |
| **Database** | PostgreSQL | 13+ | Primary relational database |
| **Cache** | Redis | 6+ | Session storage and caching |
| **Vector DB** | Weaviate | 1.22+ | Vector database for embeddings |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM and migrations |
| **AI Integration** | LiteLLM | 1.10+ | AI provider abstraction |
| **Authentication** | JWT | - | Token-based authentication |
| **Testing** | Pytest | 7.4+ | Testing framework |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18+ | UI framework |
| **Language** | TypeScript | 5.0+ | Type-safe JavaScript |
| **State Management** | Zustand | 4.4+ | Lightweight state management |
| **UI Library** | Ant Design | 5.0+ | Component library |
| **Routing** | React Router | 6.8+ | Client-side routing |
| **HTTP Client** | Axios | 1.6+ | API communication |
| **WebSocket** | Socket.io | 4.7+ | Real-time communication |
| **Testing** | Jest + RTL | - | Testing framework |

### DevOps & Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Docker Compose | Local development |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Monitoring** | Prometheus + Grafana | System monitoring |
| **Logging** | Structured logging | Application logs |
| **Security** | Security headers, CORS | Application security |

## 🚀 Scalability Considerations

### Horizontal Scaling

The architecture supports horizontal scaling through:

- **Stateless API design** - No server-side session storage
- **Database connection pooling** - Efficient database connections
- **Redis for session storage** - Shared session data across instances
- **Load balancer ready** - Multiple application instances
- **Microservices ready** - Service separation for independent scaling

### Performance Optimization

- **Caching strategy** - Multiple layers of caching
- **Database indexing** - Optimized query performance
- **Connection pooling** - Efficient resource usage
- **Async processing** - Non-blocking operations
- **CDN ready** - Static asset delivery optimization

## 🔄 Deployment Architecture

### Development Environment

```mermaid
graph LR
    subgraph "Development"
        Dev_App[Development App]
        Dev_DB[(Dev Database)]
        Dev_Redis[(Dev Redis)]
        Dev_Weaviate[(Dev Weaviate)]
    end
    
    Dev_App --> Dev_DB
    Dev_App --> Dev_Redis
    Dev_App --> Dev_Weaviate
```

### Production Environment

```mermaid
graph TB
    subgraph "Production"
        LB[Load Balancer]
        App1[App Instance 1]
        App2[App Instance 2]
        App3[App Instance 3]
        Master[(Master DB)]
        Slave1[(Slave DB 1)]
        Slave2[(Slave DB 2)]
        Redis_Cluster[(Redis Cluster)]
        Weaviate_Cluster[(Weaviate Cluster)]
    end
    
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> Master
    App2 --> Master
    App3 --> Master
    
    Master --> Slave1
    Master --> Slave2
    
    App1 --> Redis_Cluster
    App2 --> Redis_Cluster
    App3 --> Redis_Cluster
    
    App1 --> Weaviate_Cluster
    App2 --> Weaviate_Cluster
    App3 --> Weaviate_Cluster
```

## 📚 Next Steps

- **[Backend Architecture](backend.md)** - Detailed backend design
- **[Frontend Architecture](frontend.md)** - Frontend component design
- **[Database Design](database.md)** - Database schema and relationships
- **[Security Architecture](security.md)** - Security implementation details
- **[API Reference](../api/overview.md)** - Complete API documentation 