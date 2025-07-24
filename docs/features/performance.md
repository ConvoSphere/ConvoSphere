# Performance

The Performance feature focuses on optimizing the AI Chat Application for speed, scalability, and efficient resource utilization.

## Overview

The Performance system includes:

- **Caching Strategies**: Multi-layer caching for improved response times
- **Database Optimization**: Query optimization and indexing strategies
- **Load Balancing**: Distribution of traffic across multiple servers
- **CDN Integration**: Content delivery network for static assets
- **Monitoring & Metrics**: Real-time performance monitoring
- **Resource Management**: Efficient memory and CPU utilization

## Architecture

### Performance Optimization Layers

```mermaid
graph TD
    A[User Request] --> B[Load Balancer]
    B --> C[CDN Cache]
    C --> D[Application Cache]
    D --> E[Database Cache]
    E --> F[Database]
    G[Monitoring] --> H[Performance Metrics]
    H --> I[Alerting]
```

### Caching Strategy

```mermaid
graph LR
    A[Browser Cache] --> B[CDN Cache]
    B --> C[Application Cache]
    C --> D[Database Cache]
    D --> E[Database]
    F[Cache Invalidation] --> G[Cache Updates]
```

## Features

### Multi-Layer Caching

Comprehensive caching strategy across all layers:

```python
class CacheManager:
    def __init__(self, redis_client, memory_cache):
        self.redis = redis_client
        self.memory = memory_cache
        self.cache_config = {
            'user_profile': {'ttl': 3600, 'layer': 'redis'},
            'conversation': {'ttl': 1800, 'layer': 'redis'},
            'ai_response': {'ttl': 300, 'layer': 'memory'},
            'search_results': {'ttl': 600, 'layer': 'redis'},
            'file_metadata': {'ttl': 7200, 'layer': 'redis'}
        }
    
    async def get(self, key: str, cache_type: str = 'redis') -> Optional[Any]:
        """Get value from cache"""
        if cache_type == 'redis':
            return await self.redis.get(key)
        elif cache_type == 'memory':
            return self.memory.get(key)
        return None
    
    async def set(self, key: str, value: Any, cache_type: str = 'redis', ttl: int = None):
        """Set value in cache"""
        config = self.cache_config.get(key.split(':')[0], {})
        ttl = ttl or config.get('ttl', 3600)
        layer = config.get('layer', 'redis')
        
        if layer == 'redis':
            await self.redis.setex(key, ttl, json.dumps(value))
        elif layer == 'memory':
            self.memory.set(key, value, ttl)
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache by pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
    
    async def warm_cache(self, cache_type: str):
        """Warm up cache with frequently accessed data"""
        if cache_type == 'user_profiles':
            # Pre-load active user profiles
            active_users = await self.get_active_users()
            for user in active_users:
                await self.set(f"user_profile:{user.id}", user.to_dict())
        
        elif cache_type == 'conversations':
            # Pre-load recent conversations
            recent_conversations = await self.get_recent_conversations()
            for conv in recent_conversations:
                await self.set(f"conversation:{conv.id}", conv.to_dict())
```

### Database Optimization

Query optimization and indexing strategies:

```python
class DatabaseOptimizer:
    def __init__(self, db: Session):
        self.db = db
    
    def optimize_queries(self):
        """Apply query optimizations"""
        # Enable query result caching
        self.db.execute("SET enable_seqscan = off")
        self.db.execute("SET random_page_cost = 1.1")
        self.db.execute("SET effective_cache_size = '4GB'")
    
    def create_indexes(self):
        """Create performance indexes"""
        indexes = [
            # Users table
            "CREATE INDEX CONCURRENTLY idx_users_email ON users(email)",
            "CREATE INDEX CONCURRENTLY idx_users_created_at ON users(created_at)",
            "CREATE INDEX CONCURRENTLY idx_users_last_login ON users(last_login_at)",
            
            # Messages table
            "CREATE INDEX CONCURRENTLY idx_messages_conversation_id ON messages(conversation_id)",
            "CREATE INDEX CONCURRENTLY idx_messages_created_at ON messages(created_at)",
            "CREATE INDEX CONCURRENTLY idx_messages_user_id ON messages(user_id)",
            
            # Conversations table
            "CREATE INDEX CONCURRENTLY idx_conversations_user_id ON conversations(user_id)",
            "CREATE INDEX CONCURRENTLY idx_conversations_updated_at ON conversations(updated_at)",
            
            # Composite indexes
            "CREATE INDEX CONCURRENTLY idx_messages_conv_created ON messages(conversation_id, created_at)",
            "CREATE INDEX CONCURRENTLY idx_conversations_user_updated ON conversations(user_id, updated_at)"
        ]
        
        for index_sql in indexes:
            try:
                self.db.execute(index_sql)
            except Exception as e:
                print(f"Index creation failed: {e}")
    
    def analyze_tables(self):
        """Update table statistics"""
        tables = ['users', 'messages', 'conversations', 'files', 'documents']
        for table in tables:
            self.db.execute(f"ANALYZE {table}")
    
    def optimize_vacuum(self):
        """Optimize database with VACUUM"""
        self.db.execute("VACUUM ANALYZE")
```

### Query Optimization

```python
class QueryOptimizer:
    def __init__(self, db: Session):
        self.db = db
    
    def optimize_conversation_query(self, user_id: int, limit: int = 50) -> List[Conversation]:
        """Optimized conversation query with eager loading"""
        return self.db.query(Conversation).options(
            joinedload(Conversation.messages).joinedload(Message.user),
            joinedload(Conversation.user)
        ).filter(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).limit(limit).all()
    
    def optimize_message_query(self, conversation_id: int, page: int = 1, size: int = 20) -> List[Message]:
        """Optimized message query with pagination"""
        offset = (page - 1) * size
        
        return self.db.query(Message).options(
            joinedload(Message.user),
            joinedload(Message.attachments)
        ).filter(
            Message.conversation_id == conversation_id
        ).order_by(
            Message.created_at.desc()
        ).offset(offset).limit(size).all()
    
    def optimize_search_query(self, query: str, user_id: int) -> List[SearchResult]:
        """Optimized search query with full-text search"""
        return self.db.query(Message).filter(
            and_(
                Message.user_id == user_id,
                Message.content.ilike(f"%{query}%")
            )
        ).options(
            joinedload(Message.conversation)
        ).order_by(
            Message.created_at.desc()
        ).limit(20).all()
```

### Load Balancing

```python
class LoadBalancer:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.current_index = 0
        self.health_checker = HealthChecker()
    
    def get_next_server(self) -> str:
        """Get next available server using round-robin"""
        healthy_servers = [s for s in self.servers if self.health_checker.is_healthy(s)]
        
        if not healthy_servers:
            raise NoHealthyServersError("No healthy servers available")
        
        server = healthy_servers[self.current_index % len(healthy_servers)]
        self.current_index += 1
        
        return server
    
    def get_server_by_load(self) -> str:
        """Get server with lowest load"""
        server_loads = []
        
        for server in self.servers:
            if self.health_checker.is_healthy(server):
                load = self.health_checker.get_server_load(server)
                server_loads.append((server, load))
        
        if not server_loads:
            raise NoHealthyServersError("No healthy servers available")
        
        # Return server with lowest load
        return min(server_loads, key=lambda x: x[1])[0]

class HealthChecker:
    def __init__(self):
        self.health_cache = {}
        self.cache_ttl = 30  # 30 seconds
    
    def is_healthy(self, server: str) -> bool:
        """Check if server is healthy"""
        cache_key = f"health:{server}"
        cached = self.health_cache.get(cache_key)
        
        if cached and time.time() - cached['timestamp'] < self.cache_ttl:
            return cached['healthy']
        
        # Perform health check
        try:
            response = requests.get(f"{server}/health", timeout=5)
            healthy = response.status_code == 200
        except:
            healthy = False
        
        self.health_cache[cache_key] = {
            'healthy': healthy,
            'timestamp': time.time()
        }
        
        return healthy
    
    def get_server_load(self, server: str) -> float:
        """Get server load percentage"""
        try:
            response = requests.get(f"{server}/metrics", timeout=5)
            metrics = response.json()
            return metrics.get('cpu_usage', 0.0)
        except:
            return 100.0  # Assume high load if can't reach server
```

### CDN Integration

```python
class CDNService:
    def __init__(self, cdn_url: str, api_key: str):
        self.cdn_url = cdn_url
        self.api_key = api_key
        self.client = self._create_client()
    
    def get_cdn_url(self, file_path: str) -> str:
        """Get CDN URL for file"""
        return f"{self.cdn_url}/{file_path}"
    
    def upload_to_cdn(self, file_path: str, file_content: bytes) -> str:
        """Upload file to CDN"""
        cdn_path = f"uploads/{file_path}"
        
        # Upload to CDN
        self.client.upload_fileobj(
            io.BytesIO(file_content),
            'cdn-bucket',
            cdn_path,
            ExtraArgs={
                'CacheControl': 'max-age=31536000',  # 1 year
                'ContentType': self._get_content_type(file_path)
            }
        )
        
        return self.get_cdn_url(cdn_path)
    
    def invalidate_cache(self, file_paths: List[str]):
        """Invalidate CDN cache for files"""
        for path in file_paths:
            self.client.create_invalidation(
                DistributionId='CDN_DISTRIBUTION_ID',
                InvalidationBatch={
                    'Paths': {
                        'Quantity': 1,
                        'Items': [f'/{path}']
                    },
                    'CallerReference': str(uuid.uuid4())
                }
            )
    
    def _get_content_type(self, file_path: str) -> str:
        """Get content type for file"""
        ext = Path(file_path).suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.js': 'application/javascript',
            '.css': 'text/css'
        }
        return content_types.get(ext, 'application/octet-stream')
```

### Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self, prometheus_client):
        self.prometheus = prometheus_client
        
        # Define metrics
        self.request_duration = prometheus_client.Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_count = prometheus_client.Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.active_connections = prometheus_client.Gauge(
            'websocket_active_connections',
            'Number of active WebSocket connections'
        )
        
        self.database_query_duration = prometheus_client.Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['query_type', 'table']
        )
        
        self.cache_hit_ratio = prometheus_client.Gauge(
            'cache_hit_ratio',
            'Cache hit ratio percentage',
            ['cache_type']
        )
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.request_duration.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).observe(duration)
        
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
    
    def record_database_query(self, query_type: str, table: str, duration: float):
        """Record database query metrics"""
        self.database_query_duration.labels(
            query_type=query_type,
            table=table
        ).observe(duration)
    
    def update_cache_metrics(self, cache_type: str, hits: int, misses: int):
        """Update cache hit ratio metrics"""
        total = hits + misses
        if total > 0:
            hit_ratio = (hits / total) * 100
            self.cache_hit_ratio.labels(cache_type=cache_type).set(hit_ratio)
    
    def update_websocket_connections(self, count: int):
        """Update WebSocket connection count"""
        self.active_connections.set(count)
```

### Resource Management

```python
class ResourceManager:
    def __init__(self):
        self.memory_threshold = 0.8  # 80% memory usage threshold
        self.cpu_threshold = 0.7     # 70% CPU usage threshold
    
    def check_system_resources(self) -> Dict[str, float]:
        """Check system resource usage"""
        import psutil
        
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        return {
            'memory_usage': memory.percent / 100,
            'cpu_usage': cpu / 100,
            'disk_usage': disk.percent / 100,
            'memory_available': memory.available / (1024**3),  # GB
            'disk_available': disk.free / (1024**3)  # GB
        }
    
    def is_system_overloaded(self) -> bool:
        """Check if system is overloaded"""
        resources = self.check_system_resources()
        
        return (resources['memory_usage'] > self.memory_threshold or
                resources['cpu_usage'] > self.cpu_threshold)
    
    def optimize_memory_usage(self):
        """Optimize memory usage"""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Clear application caches if memory usage is high
        if self.check_system_resources()['memory_usage'] > 0.9:
            cache_manager.clear_least_used()
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        resources = self.check_system_resources()
        
        if resources['memory_usage'] > 0.8:
            recommendations.append("High memory usage detected. Consider increasing memory or optimizing cache usage.")
        
        if resources['cpu_usage'] > 0.7:
            recommendations.append("High CPU usage detected. Consider load balancing or optimizing queries.")
        
        if resources['disk_usage'] > 0.9:
            recommendations.append("High disk usage detected. Consider cleanup or increasing storage.")
        
        return recommendations
```

## API Endpoints

### Performance Metrics

**GET** `/api/v1/performance/metrics`

Get current performance metrics.

```python
@router.get("/performance/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_admin_user)
):
    """Get performance metrics (admin only)"""
    
    monitor = PerformanceMonitor(prometheus_client)
    resource_manager = ResourceManager()
    
    metrics = {
        'system_resources': resource_manager.check_system_resources(),
        'cache_stats': await cache_manager.get_stats(),
        'database_stats': await database_optimizer.get_stats(),
        'recommendations': resource_manager.get_performance_recommendations()
    }
    
    return metrics
```

### Cache Management

**POST** `/api/v1/performance/cache/clear`

Clear application cache.

```python
@router.post("/performance/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user)
):
    """Clear application cache (admin only)"""
    
    if cache_type:
        await cache_manager.clear_cache(cache_type)
    else:
        await cache_manager.clear_all_caches()
    
    return {"message": "Cache cleared successfully"}
```

### Database Optimization

**POST** `/api/v1/performance/database/optimize`

Run database optimization.

```python
@router.post("/performance/database/optimize")
async def optimize_database(
    current_user: User = Depends(get_current_admin_user)
):
    """Run database optimization (admin only)"""
    
    optimizer = DatabaseOptimizer(db)
    
    # Run optimizations
    optimizer.optimize_queries()
    optimizer.analyze_tables()
    optimizer.optimize_vacuum()
    
    return {"message": "Database optimization completed"}
```

## Configuration

### Performance Settings

```python
# config/performance.py
class PerformanceConfig:
    # Caching
    REDIS_URL = "redis://localhost:6379"
    CACHE_TTL = 3600  # 1 hour
    MEMORY_CACHE_SIZE = 1000
    
    # Database
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 30
    DB_POOL_TIMEOUT = 30
    
    # CDN
    CDN_URL = "https://cdn.example.com"
    CDN_CACHE_TTL = 31536000  # 1 year
    
    # Load Balancing
    LOAD_BALANCER_ALGORITHM = "round_robin"  # or "least_connections"
    HEALTH_CHECK_INTERVAL = 30
    
    # Monitoring
    METRICS_ENABLED = True
    METRICS_PORT = 9090
    
    # Resource Management
    MEMORY_THRESHOLD = 0.8
    CPU_THRESHOLD = 0.7
    AUTO_OPTIMIZATION = True
```

### Database Configuration

```python
# config/database.py
DATABASE_CONFIG = {
    'url': 'postgresql://user:password@localhost:5432/ai_chat_app',
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'echo': False,
    'echo_pool': False,
    'pool_pre_ping': True,
    'connect_args': {
        'connect_timeout': 10,
        'application_name': 'ai_chat_app'
    }
}
```

## Monitoring Dashboard

### Key Metrics

1. **Response Time**: Average API response times
2. **Throughput**: Requests per second
3. **Error Rate**: Percentage of failed requests
4. **Cache Hit Ratio**: Cache effectiveness
5. **Database Performance**: Query execution times
6. **Resource Usage**: CPU, memory, disk usage
7. **Active Connections**: WebSocket connections
8. **Queue Length**: Request queue length

### Alerting

```python
class PerformanceAlerting:
    def __init__(self, alert_service: AlertService):
        self.alert_service = alert_service
        self.thresholds = {
            'response_time': 2.0,  # seconds
            'error_rate': 0.05,    # 5%
            'memory_usage': 0.9,   # 90%
            'cpu_usage': 0.8,      # 80%
            'cache_hit_ratio': 0.7  # 70%
        }
    
    async def check_alerts(self, metrics: Dict):
        """Check for performance alerts"""
        alerts = []
        
        # Response time alert
        if metrics.get('avg_response_time', 0) > self.thresholds['response_time']:
            alerts.append({
                'type': 'high_response_time',
                'message': f"High response time: {metrics['avg_response_time']:.2f}s",
                'severity': 'warning'
            })
        
        # Error rate alert
        if metrics.get('error_rate', 0) > self.thresholds['error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'message': f"High error rate: {metrics['error_rate']:.2%}",
                'severity': 'critical'
            })
        
        # Resource usage alerts
        if metrics.get('memory_usage', 0) > self.thresholds['memory_usage']:
            alerts.append({
                'type': 'high_memory_usage',
                'message': f"High memory usage: {metrics['memory_usage']:.1%}",
                'severity': 'warning'
            })
        
        # Send alerts
        for alert in alerts:
            await self.alert_service.send_alert(alert)
```

## Best Practices

1. **Caching Strategy**: Implement multi-layer caching
2. **Database Optimization**: Use proper indexes and query optimization
3. **Load Balancing**: Distribute traffic across multiple servers
4. **CDN Usage**: Use CDN for static assets
5. **Monitoring**: Implement comprehensive performance monitoring
6. **Resource Management**: Monitor and optimize resource usage
7. **Connection Pooling**: Use connection pooling for database connections
8. **Async Operations**: Use async/await for I/O operations
9. **Compression**: Enable gzip compression for responses
10. **Regular Optimization**: Schedule regular performance optimization tasks