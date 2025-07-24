# Monitoring Guide

This guide covers monitoring and observability for the AI Chat Application in production environments. It includes system monitoring, application metrics, logging, alerting, and troubleshooting.

## Monitoring Overview

### Monitoring Stack

The AI Chat Application uses a comprehensive monitoring stack:

```
┌─────────────────────────────────────────────────────────┐
│ Monitoring Architecture                                 │
├─────────────────────────────────────────────────────────┤
│ Application Layer                                       │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Frontend    │ │ Backend API │ │ AI Services │        │
│ │ Monitoring  │ │ Monitoring  │ │ Monitoring  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ Infrastructure Layer                                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ System      │ │ Database    │ │ Network     │        │
│ │ Metrics     │ │ Monitoring  │ │ Monitoring  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ Observability Layer                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Prometheus  │ │ Grafana     │ │ AlertManager│        │
│ │ (Metrics)   │ │ (Dashboards)│ │ (Alerting)  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ Logging Layer                                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Fluentd     │ │ Elasticsearch│ │ Kibana      │        │
│ │ (Log Agg)   │ │ (Log Store) │ │ (Log Viz)   │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### Key Monitoring Components

- **Prometheus**: Time-series metrics collection
- **Grafana**: Metrics visualization and dashboards
- **AlertManager**: Alert routing and notification
- **Fluentd**: Log aggregation and forwarding
- **Elasticsearch**: Log storage and indexing
- **Kibana**: Log visualization and analysis

## Application Metrics

### Backend API Metrics

#### HTTP Metrics
```yaml
# Request metrics
http_requests_total{method="POST", endpoint="/api/chat", status="200"}
http_request_duration_seconds{method="POST", endpoint="/api/chat", quantile="0.95"}
http_request_size_bytes{method="POST", endpoint="/api/chat"}
http_response_size_bytes{method="POST", endpoint="/api/chat"}

# Error metrics
http_errors_total{method="POST", endpoint="/api/chat", error_type="validation"}
http_4xx_errors_total{method="POST", endpoint="/api/chat"}
http_5xx_errors_total{method="POST", endpoint="/api/chat"}
```

#### Business Metrics
```yaml
# Chat metrics
chat_messages_total{conversation_id="123", user_id="456"}
chat_conversations_created_total{user_id="456"}
chat_files_uploaded_total{file_type="pdf", user_id="456"}

# AI metrics
ai_requests_total{model="gpt-4", user_id="456"}
ai_response_time_seconds{model="gpt-4", quantile="0.95"}
ai_tokens_used_total{model="gpt-4", user_id="456"}
ai_errors_total{model="gpt-4", error_type="rate_limit"}
```

#### Database Metrics
```yaml
# Connection metrics
db_connections_active{database="postgres"}
db_connections_idle{database="postgres"}
db_connections_max{database="postgres"}

# Query metrics
db_query_duration_seconds{query_type="select", table="messages"}
db_queries_total{query_type="insert", table="messages"}
db_slow_queries_total{threshold="1s", table="messages"}
```

### Frontend Metrics

#### Performance Metrics
```yaml
# Page load metrics
page_load_time_seconds{page="/chat", quantile="0.95"}
page_load_time_seconds{page="/login", quantile="0.95"}

# User interaction metrics
user_interaction_duration_seconds{action="message_send"}
user_interaction_duration_seconds{action="file_upload"}

# Error metrics
js_errors_total{error_type="network", page="/chat"}
js_errors_total{error_type="runtime", page="/chat"}
```

#### User Experience Metrics
```yaml
# Engagement metrics
user_session_duration_seconds{user_id="456"}
user_messages_per_session{user_id="456"}
user_conversations_per_session{user_id="456"}

# Feature usage metrics
feature_usage_total{feature="file_upload", user_id="456"}
feature_usage_total{feature="ai_tools", user_id="456"}
```

## System Metrics

### Infrastructure Metrics

#### CPU and Memory
```yaml
# CPU metrics
cpu_usage_percent{instance="backend-1", core="0"}
cpu_usage_percent{instance="backend-1", core="1"}
cpu_load_average{instance="backend-1", period="1m"}
cpu_load_average{instance="backend-1", period="5m"}

# Memory metrics
memory_usage_bytes{instance="backend-1"}
memory_available_bytes{instance="backend-1"}
memory_swap_usage_bytes{instance="backend-1"}
```

#### Disk and Network
```yaml
# Disk metrics
disk_usage_percent{instance="backend-1", mount="/"}
disk_io_read_bytes{instance="backend-1", device="sda"}
disk_io_write_bytes{instance="backend-1", device="sda"}

# Network metrics
network_bytes_received{instance="backend-1", interface="eth0"}
network_bytes_transmitted{instance="backend-1", interface="eth0"}
network_packets_dropped{instance="backend-1", interface="eth0"}
```

#### Container Metrics
```yaml
# Docker metrics
container_cpu_usage_seconds{container="backend-api"}
container_memory_usage_bytes{container="backend-api"}
container_network_receive_bytes{container="backend-api"}
container_network_transmit_bytes{container="backend-api"}
```

### Database Metrics

#### PostgreSQL Metrics
```yaml
# Connection metrics
pg_stat_database_numbackends{database="aichat"}
pg_stat_database_xact_commit{database="aichat"}
pg_stat_database_xact_rollback{database="aichat"}

# Performance metrics
pg_stat_database_blk_read_time{database="aichat"}
pg_stat_database_blk_write_time{database="aichat"}
pg_stat_database_tup_fetched{database="aichat"}
pg_stat_database_tup_inserted{database="aichat"}
```

#### Redis Metrics
```yaml
# Memory metrics
redis_memory_used_bytes{instance="redis-1"}
redis_memory_max_bytes{instance="redis-1"}
redis_memory_fragmentation_ratio{instance="redis-1"}

# Performance metrics
redis_commands_processed_total{instance="redis-1"}
redis_keyspace_hits_total{instance="redis-1"}
redis_keyspace_misses_total{instance="redis-1"}
```

## Logging Configuration

### Log Levels and Format

#### Log Levels
```python
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": "%(lineno)d"}',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/aichat/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
            'level': 'INFO'
        }
    },
    'loggers': {
        'aichat': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

#### Structured Logging
```python
# Example structured log messages
import logging
import json

logger = logging.getLogger('aichat')

# User action log
logger.info('User action', extra={
    'user_id': user.id,
    'action': 'send_message',
    'conversation_id': conversation.id,
    'message_length': len(message),
    'timestamp': datetime.utcnow().isoformat()
})

# Error log
logger.error('Database connection failed', extra={
    'error_type': 'database_connection',
    'database': 'postgres',
    'retry_count': 3,
    'duration_seconds': 5.2
})
```

### Log Aggregation

#### Fluentd Configuration
```ruby
# Fluentd configuration for log aggregation
<source>
  @type tail
  path /var/log/aichat/*.log
  pos_file /var/log/fluentd/aichat.log.pos
  tag aichat.app
  format json
  time_key timestamp
  time_format %Y-%m-%d %H:%M:%S
</source>

<filter aichat.app>
  @type record_transformer
  <record>
    hostname "#{Socket.gethostname}"
    environment "#{ENV['ENVIRONMENT']}"
    service "aichat-backend"
  </record>
</filter>

<match aichat.app>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name aichat-logs
  type_name fluentd
  logstash_format true
  logstash_prefix aichat
  time_key timestamp
  time_precision 3
</match>
```

## Dashboards and Visualization

### Grafana Dashboards

#### Application Overview Dashboard
```json
{
  "dashboard": {
    "title": "AI Chat Application Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_5xx_errors_total[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

#### System Resources Dashboard
```json
{
  "dashboard": {
    "title": "System Resources",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Disk Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "node_filesystem_avail_bytes / node_filesystem_size_bytes * 100",
            "legendFormat": "{{instance}} {{mountpoint}}"
          }
        ]
      }
    ]
  }
}
```

### Custom Dashboards

#### AI Service Dashboard
```json
{
  "dashboard": {
    "title": "AI Services Monitoring",
    "panels": [
      {
        "title": "AI Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_requests_total[5m])",
            "legendFormat": "{{model}}"
          }
        ]
      },
      {
        "title": "AI Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(ai_response_time_seconds_bucket[5m]))",
            "legendFormat": "{{model}} 95th percentile"
          }
        ]
      },
      {
        "title": "AI Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_errors_total[5m])",
            "legendFormat": "{{model}} {{error_type}}"
          }
        ]
      }
    ]
  }
}
```

## Alerting Configuration

### Alert Rules

#### Critical Alerts
```yaml
# Critical system alerts
groups:
  - name: critical_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 90% for 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 90% for 5 minutes"

      - alert: DiskSpaceCritical
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Critical disk space on {{ $labels.instance }}"
          description: "Disk space is below 10%"
```

#### Application Alerts
```yaml
# Application-specific alerts
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_5xx_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "5xx error rate is above 10% for 2 minutes"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times detected"
          description: "95th percentile response time is above 2 seconds"

      - alert: AIServiceDown
        expr: up{job="ai-service"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AI service is down"
          description: "AI service has been down for more than 1 minute"
```

### Alert Routing

#### AlertManager Configuration
```yaml
# AlertManager configuration
global:
  smtp_smarthost: 'smtp.company.com:587'
  smtp_from: 'alerts@aichatapp.com'
  smtp_auth_username: 'alerts'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'team-ai-chat'
  routes:
    - match:
        severity: critical
      receiver: 'team-ai-chat-urgent'
      continue: true
    - match:
        alertname: HighCPUUsage
      receiver: 'team-infrastructure'

receivers:
  - name: 'team-ai-chat'
    email_configs:
      - to: 'ai-chat-team@company.com'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#ai-chat-alerts'
        title: '{{ template "slack.title" . }}'
        text: '{{ template "slack.text" . }}'

  - name: 'team-ai-chat-urgent'
    email_configs:
      - to: 'ai-chat-urgent@company.com'
    pagerduty_configs:
      - service_key: 'pagerduty-service-key'
```

## Performance Monitoring

### APM (Application Performance Monitoring)

#### Distributed Tracing
```python
# OpenTelemetry configuration for distributed tracing
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Example trace
@tracer.start_as_current_span("process_message")
def process_message(message):
    with tracer.start_as_current_span("validate_message"):
        validate_message(message)
    
    with tracer.start_as_current_span("save_to_database"):
        save_message_to_db(message)
    
    with tracer.start_as_current_span("send_to_ai"):
        ai_response = send_to_ai_service(message)
    
    return ai_response
```

#### Performance Metrics
```python
# Custom performance metrics
from prometheus_client import Histogram, Counter, Gauge

# Request duration histogram
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status']
)

# Active connections gauge
active_connections = Gauge(
    'websocket_active_connections',
    'Number of active WebSocket connections'
)

# Message processing counter
messages_processed = Counter(
    'messages_processed_total',
    'Total number of messages processed',
    ['status', 'type']
)

# Example usage
@request_duration.time()
def handle_chat_message(message):
    try:
        result = process_message(message)
        messages_processed.labels(status='success', type='chat').inc()
        return result
    except Exception as e:
        messages_processed.labels(status='error', type='chat').inc()
        raise
```

## Health Checks

### Application Health Checks

#### Health Check Endpoints
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
        "database": check_database_connection(),
        "redis": check_redis_connection(),
        "ai_service": check_ai_service_health(),
        "file_storage": check_file_storage_health()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }

def check_database_connection():
    try:
        db.execute("SELECT 1")
        return True
    except Exception:
        return False
```

#### Kubernetes Health Checks
```yaml
# Kubernetes health check configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aichat-backend
spec:
  template:
    spec:
      containers:
      - name: backend
        image: aichat/backend:latest
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/detailed
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

## Troubleshooting

### Common Monitoring Issues

#### Metrics Not Appearing
```bash
# Check Prometheus targets
curl -s http://prometheus:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health, lastError: .lastError}'

# Check metric endpoints
curl -s http://backend:8000/metrics | grep -E "(http_requests_total|ai_requests_total)"

# Check Prometheus configuration
docker exec prometheus cat /etc/prometheus/prometheus.yml
```

#### Logs Not Appearing
```bash
# Check Fluentd status
docker exec fluentd fluentd --dry-run -c /fluentd/etc/fluent.conf

# Check Elasticsearch indices
curl -s http://elasticsearch:9200/_cat/indices | grep aichat

# Check log files
docker exec backend tail -f /var/log/aichat/app.log
```

#### Alerts Not Firing
```bash
# Check AlertManager status
curl -s http://alertmanager:9093/api/v1/status

# Check alert rules
curl -s http://prometheus:9090/api/v1/rules | jq '.data.groups[].rules[].name'

# Test alert rule
curl -s "http://prometheus:9090/api/v1/query?query=up" | jq
```

### Performance Optimization

#### Prometheus Optimization
```yaml
# Prometheus configuration optimization
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aichat-backend'
    scrape_interval: 10s
    metrics_path: /metrics
    static_configs:
      - targets: ['backend:8000']
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'http_requests_total'
        action: keep
```

#### Grafana Optimization
```ini
# Grafana configuration optimization
[server]
http_port = 3000
max_concurrent_sharing_request = 10

[database]
max_open_conn = 100
max_idle_conn = 100
conn_max_lifetime = 14400

[security]
allow_embedding = true
cookie_secure = true
```

---

**Next Steps**: Learn about [Production Deployment](production.md) for complete deployment setup, or explore [CI/CD Pipeline](ci-cd.md) for automated deployment workflows.