# Production Deployment

This guide covers deploying the AI Chat Application to production environments with high availability, security, and performance.

## Overview

Production deployment includes:

- **Infrastructure Setup**: Cloud infrastructure configuration
- **Container Orchestration**: Kubernetes or Docker Swarm deployment
- **Load Balancing**: High availability and traffic distribution
- **Monitoring & Logging**: Production monitoring and alerting
- **Security**: SSL/TLS, firewalls, and security best practices
- **Backup & Recovery**: Data backup and disaster recovery
- **CI/CD Pipeline**: Automated deployment pipeline

## Architecture

### Production Infrastructure

```mermaid
graph TD
    A[Load Balancer] --> B[Web Server 1]
    A --> C[Web Server 2]
    A --> D[Web Server N]
    B --> E[Application Server 1]
    C --> F[Application Server 2]
    D --> G[Application Server N]
    E --> H[Database Cluster]
    F --> H
    G --> H
    E --> I[Redis Cluster]
    F --> I
    G --> I
    E --> J[Object Storage]
    F --> J
    G --> J
    K[Monitoring] --> L[Logs & Metrics]
    L --> M[Alerting]
```

### Deployment Flow

```mermaid
graph LR
    A[Code Push] --> B[CI Pipeline]
    B --> C[Build Image]
    C --> D[Security Scan]
    D --> E[Push to Registry]
    E --> F[Deploy to Staging]
    F --> G[Tests]
    G --> H[Deploy to Production]
    H --> I[Health Checks]
    I --> J[Traffic Switch]
```

## Infrastructure Setup

### Cloud Provider Configuration

#### AWS Setup

```yaml
# infrastructure/aws/main.tf
provider "aws" {
  region = "us-west-2"
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "ai-chat-app-vpc"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "public-subnet-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "private-subnet-${count.index + 1}"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "ai-chat-app-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.27"
  
  vpc_config {
    subnet_ids              = aws_subnet.private[*].id
    endpoint_private_access = true
    endpoint_public_access  = true
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier           = "ai-chat-app-db"
  engine               = "postgres"
  engine_version       = "14.7"
  instance_class       = "db.r6g.large"
  allocated_storage    = 100
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = "ai_chat_app"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection = true
  
  tags = {
    Name = "ai-chat-app-database"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "ai-chat-app-redis"
  engine               = "redis"
  node_type            = "cache.r6g.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  
  security_group_ids = [aws_security_group.redis.id]
  subnet_group_name  = aws_elasticache_subnet_group.main.name
}

# S3 Bucket for File Storage
resource "aws_s3_bucket" "main" {
  bucket = "ai-chat-app-files-${random_string.bucket_suffix.result}"
  
  tags = {
    Name = "ai-chat-app-file-storage"
  }
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

#### Google Cloud Platform Setup

```yaml
# infrastructure/gcp/main.tf
provider "google" {
  project = var.project_id
  region  = "us-central1"
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "ai-chat-app-vpc"
  auto_create_subnetworks = false
}

# Subnets
resource "google_compute_subnetwork" "private" {
  name          = "private-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.main.id
  region        = "us-central1"
  
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "public" {
  name          = "public-subnet"
  ip_cidr_range = "10.0.1.0/24"
  network       = google_compute_network.main.id
  region        = "us-central1"
}

# GKE Cluster
resource "google_container_cluster" "main" {
  name     = "ai-chat-app-cluster"
  location = "us-central1"
  
  remove_default_node_pool = true
  initial_node_count       = 1
  
  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.private.name
  
  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/16"
    services_ipv4_cidr_block = "/22"
  }
  
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
}

# Cloud SQL Database
resource "google_sql_database_instance" "main" {
  name             = "ai-chat-app-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"
  
  settings {
    tier = "db-custom-2-4096"
    
    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }
  }
  
  deletion_protection = true
}

resource "google_sql_database" "main" {
  name     = "ai_chat_app"
  instance = google_sql_database_instance.main.name
}

# Cloud Storage Bucket
resource "google_storage_bucket" "main" {
  name          = "ai-chat-app-files-${random_string.bucket_suffix.result}"
  location      = "US"
  force_destroy = false
  
  versioning {
    enabled = true
  }
  
  uniform_bucket_level_access = true
}
```

### Kubernetes Configuration

#### Namespace Setup

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-chat-app
  labels:
    name: ai-chat-app
```

#### ConfigMap and Secrets

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-chat-app-config
  namespace: ai-chat-app
data:
  DATABASE_URL: "postgresql://user:password@ai-chat-app-db:5432/ai_chat_app"
  REDIS_URL: "redis://ai-chat-app-redis:6379"
  S3_BUCKET: "ai-chat-app-files"
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
---
apiVersion: v1
kind: Secret
metadata:
  name: ai-chat-app-secrets
  namespace: ai-chat-app
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret-key>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
  OPENAI_API_KEY: <base64-encoded-openai-key>
  ANTHROPIC_API_KEY: <base64-encoded-anthropic-key>
```

#### Deployment Configuration

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-chat-app-backend
  namespace: ai-chat-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-chat-app-backend
  template:
    metadata:
      labels:
        app: ai-chat-app-backend
    spec:
      containers:
      - name: backend
        image: ai-chat-app/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: ai-chat-app-config
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: ai-chat-app-config
              key: REDIS_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ai-chat-app-secrets
              key: SECRET_KEY
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ai-chat-app-secrets
              key: JWT_SECRET_KEY
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-chat-app-secrets
              key: OPENAI_API_KEY
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
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
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-chat-app-frontend
  namespace: ai-chat-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-chat-app-frontend
  template:
    metadata:
      labels:
        app: ai-chat-app-frontend
    spec:
      containers:
      - name: frontend
        image: ai-chat-app/frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "https://api.aichatapp.com"
        - name: REACT_APP_WS_URL
          value: "wss://api.aichatapp.com/ws"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
```

#### Service Configuration

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-chat-app-backend-service
  namespace: ai-chat-app
spec:
  selector:
    app: ai-chat-app-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: ai-chat-app-frontend-service
  namespace: ai-chat-app
spec:
  selector:
    app: ai-chat-app-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
```

#### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-chat-app-ingress
  namespace: ai-chat-app
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.aichatapp.com
    - app.aichatapp.com
    secretName: ai-chat-app-tls
  rules:
  - host: api.aichatapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-chat-app-backend-service
            port:
              number: 80
  - host: app.aichatapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-chat-app-frontend-service
            port:
              number: 80
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Backend
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile.backend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push Frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --name ai-chat-app-cluster --region us-west-2
    
    - name: Deploy to Kubernetes
      run: |
        # Update image tags
        sed -i "s|IMAGE_TAG|${{ github.sha }}|g" k8s/deployment.yaml
        
        # Apply configurations
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/deployment.yaml
        kubectl apply -f k8s/services.yaml
        kubectl apply -f k8s/ingress.yaml
        
        # Wait for deployment
        kubectl rollout status deployment/ai-chat-app-backend -n ai-chat-app
        kubectl rollout status deployment/ai-chat-app-frontend -n ai-chat-app
    
    - name: Run smoke tests
      run: |
        # Wait for services to be ready
        sleep 30
        
        # Test API health
        curl -f https://api.aichatapp.com/health
        
        # Test frontend
        curl -f https://app.aichatapp.com
```

### Docker Configuration

#### Backend Dockerfile

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

## Security Configuration

### SSL/TLS Setup

```yaml
# k8s/certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: ai-chat-app-cert
  namespace: ai-chat-app
spec:
  secretName: ai-chat-app-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - api.aichatapp.com
  - app.aichatapp.com
```

### Network Policies

```yaml
# k8s/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: ai-chat-app
spec:
  podSelector:
    matchLabels:
      app: ai-chat-app-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ai-chat-app
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: ai-chat-app
    ports:
    - protocol: TCP
      port: 5432  # Database
    - protocol: TCP
      port: 6379  # Redis
  - to: []
    ports:
    - protocol: TCP
      port: 443   # External HTTPS
```

### Security Context

```yaml
# Add to deployment.yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: backend
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
    - job_name: 'ai-chat-app-backend'
      static_configs:
      - targets: ['ai-chat-app-backend-service:8000']
      metrics_path: /metrics
      scrape_interval: 10s
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
```

### Grafana Dashboard

```yaml
# k8s/grafana.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secrets
              key: admin-password
        volumeMounts:
        - name: dashboards
          mountPath: /var/lib/grafana/dashboards
      volumes:
      - name: dashboards
        configMap:
          name: grafana-dashboards
```

### Logging Configuration

```yaml
# k8s/logging.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch-master"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

## Backup and Recovery

### Database Backup

```yaml
# k8s/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: ai-chat-app
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:14
            command:
            - /bin/bash
            - -c
            - |
              pg_dump $DATABASE_URL | gzip > /backup/backup-$(date +%Y%m%d-%H%M%S).sql.gz
              aws s3 cp /backup/backup-*.sql.gz s3://ai-chat-app-backups/
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: ai-chat-app-secrets
                  key: database-url
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: backup-secrets
                  key: aws-access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: backup-secrets
                  key: aws-secret-access-key
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            emptyDir: {}
          restartPolicy: OnFailure
```

### Disaster Recovery

```bash
#!/bin/bash
# scripts/disaster-recovery.sh

# Restore database from backup
restore_database() {
    local backup_file=$1
    
    echo "Restoring database from $backup_file..."
    
    # Download backup from S3
    aws s3 cp s3://ai-chat-app-backups/$backup_file /tmp/
    
    # Restore database
    gunzip -c /tmp/$backup_file | psql $DATABASE_URL
    
    echo "Database restore completed"
}

# Scale down applications
scale_down() {
    echo "Scaling down applications..."
    kubectl scale deployment ai-chat-app-backend --replicas=0 -n ai-chat-app
    kubectl scale deployment ai-chat-app-frontend --replicas=0 -n ai-chat-app
}

# Scale up applications
scale_up() {
    echo "Scaling up applications..."
    kubectl scale deployment ai-chat-app-backend --replicas=3 -n ai-chat-app
    kubectl scale deployment ai-chat-app-frontend --replicas=3 -n ai-chat-app
}

# Main recovery process
main() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo "Usage: $0 <backup-file>"
        exit 1
    fi
    
    echo "Starting disaster recovery process..."
    
    # Scale down
    scale_down
    
    # Restore database
    restore_database $backup_file
    
    # Scale up
    scale_up
    
    echo "Disaster recovery completed"
}

main "$@"
```

## Performance Optimization

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-chat-app-backend-hpa
  namespace: ai-chat-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-chat-app-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Resource Quotas

```yaml
# k8s/resource-quotas.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ai-chat-app-quota
  namespace: ai-chat-app
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "10"
```

## Best Practices

1. **Infrastructure as Code**: Use Terraform or CloudFormation for infrastructure
2. **Container Security**: Scan images for vulnerabilities
3. **Secrets Management**: Use Kubernetes secrets or external secret managers
4. **Monitoring**: Implement comprehensive monitoring and alerting
5. **Backup Strategy**: Regular automated backups with testing
6. **Load Testing**: Test application performance under load
7. **Security Scanning**: Regular security audits and penetration testing
8. **Documentation**: Maintain up-to-date deployment documentation
9. **Rollback Strategy**: Plan for quick rollbacks in case of issues
10. **Compliance**: Ensure compliance with relevant regulations (GDPR, SOC2, etc.)