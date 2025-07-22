# Database Architecture

This document describes the database architecture and design for the AI Chat Application.

## Overview

The AI Chat Application uses a multi-database architecture to support different types of data and use cases:

- **PostgreSQL**: Primary relational database for user data, chat history, and application state
- **Redis**: Caching and session management
- **Weaviate**: Vector database for semantic search and knowledge base

## Database Schema

### PostgreSQL Schema

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Chats Table
```sql
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Files Table
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Redis Schema

#### Session Storage
```
session:{session_id} -> {
    "user_id": "uuid",
    "expires_at": "timestamp",
    "data": "json"
}
```

#### Cache Storage
```
cache:{key} -> {
    "value": "data",
    "expires_at": "timestamp"
}
```

#### Rate Limiting
```
rate_limit:{user_id}:{endpoint} -> {
    "count": "integer",
    "window_start": "timestamp"
}
```

### Weaviate Schema

#### Document Collection
```json
{
    "class": "Document",
    "properties": [
        {
            "name": "content",
            "dataType": ["text"]
        },
        {
            "name": "metadata",
            "dataType": ["text"]
        },
        {
            "name": "user_id",
            "dataType": ["text"]
        },
        {
            "name": "created_at",
            "dataType": ["date"]
        }
    ]
}
```

## Data Flow

### Authentication Flow
1. User login request
2. Validate credentials against PostgreSQL
3. Create session in Redis
4. Return JWT token

### Chat Flow
1. User sends message
2. Store message in PostgreSQL
3. Process with AI provider
4. Store AI response in PostgreSQL
5. Update chat metadata

### File Upload Flow
1. User uploads file
2. Store file metadata in PostgreSQL
3. Process file content
4. Index content in Weaviate for search

## Performance Considerations

### Indexing
- Create indexes on frequently queried columns
- Use composite indexes for complex queries
- Monitor query performance regularly

### Caching Strategy
- Cache frequently accessed data in Redis
- Use cache invalidation strategies
- Implement cache warming for critical data

### Connection Pooling
- Configure appropriate connection pool sizes
- Monitor connection usage
- Implement connection health checks

## Backup and Recovery

### PostgreSQL Backup
- Daily full backups
- Hourly incremental backups
- Point-in-time recovery capability

### Redis Backup
- Periodic RDB snapshots
- AOF persistence for durability
- Replication for high availability

### Weaviate Backup
- Regular collection exports
- Configuration backups
- Disaster recovery procedures

## Security

### Data Encryption
- Encrypt data at rest
- Use TLS for data in transit
- Implement field-level encryption for sensitive data

### Access Control
- Role-based access control
- Database user permissions
- Network-level security

### Audit Logging
- Log all database operations
- Monitor for suspicious activity
- Regular security audits

## Monitoring

### Metrics to Track
- Query performance
- Connection pool usage
- Cache hit rates
- Storage usage

### Alerts
- High query latency
- Connection pool exhaustion
- Storage space warnings
- Failed backup alerts

## Migration Strategy

### Schema Changes
- Use migration scripts
- Test migrations in staging
- Plan rollback procedures
- Coordinate with application deployments

### Data Migration
- Plan for large data migrations
- Use incremental migration strategies
- Validate data integrity
- Monitor migration performance