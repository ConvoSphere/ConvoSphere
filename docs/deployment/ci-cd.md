# CI/CD Pipeline Guide

This guide covers the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the AI Chat Application. It includes automated testing, building, and deployment processes.

## CI/CD Overview

### Pipeline Architecture

The CI/CD pipeline follows a modern GitOps approach with automated testing, building, and deployment:

```
┌─────────────────────────────────────────────────────────┐
│ CI/CD Pipeline Architecture                             │
├─────────────────────────────────────────────────────────┤
│ Development Workflow                                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Code        │ │ Pull        │ │ Feature     │        │
│ │ Changes     │ │ Request     │ │ Branch      │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ CI Pipeline (GitHub Actions)                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Lint &      │ │ Unit &      │ │ Integration │        │
│ │ Format      │ │ Integration │ │ Tests       │        │
│ │ Code        │ │ Tests       │ │             │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ Build & Package                                         │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Build       │ │ Docker      │ │ Push to     │        │
│ │ Application │ │ Images      │ │ Registry    │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ CD Pipeline (ArgoCD)                                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Deploy to   │ │ Deploy to   │ │ Deploy to   │        │
│ │ Development │ │ Staging     │ │ Production  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### Pipeline Stages

1. **Code Quality**: Linting, formatting, security scanning
2. **Testing**: Unit tests, integration tests, E2E tests
3. **Building**: Compile and package applications
4. **Security**: Vulnerability scanning, dependency checks
5. **Deployment**: Automated deployment to environments
6. **Monitoring**: Post-deployment verification

## GitHub Actions Configuration

### Main CI Workflow

#### `.github/workflows/ci.yml`
```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Code Quality Checks
  code-quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm ci

      - name: Run linting
        run: |
          # Python linting
          flake8 backend/
          black --check backend/
          isort --check-only backend/
          
          # JavaScript linting
          npm run lint
          npm run type-check

      - name: Security scanning
        run: |
          # Python security
          bandit -r backend/
          safety check
          
          # JavaScript security
          npm audit --audit-level moderate

  # Backend Tests
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
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest backend/tests/unit/ -v --cov=backend --cov-report=xml

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest backend/tests/integration/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend
          name: backend-coverage

  # Frontend Tests
  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend-react/coverage/lcov.info
          flags: frontend
          name: frontend-coverage

  # Build and Package
  build:
    name: Build and Package
    runs-on: ubuntu-latest
    needs: [code-quality, backend-tests, frontend-tests]
    if: github.event_name == 'push'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push Frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend-react
          file: ./frontend-react/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate deployment manifests
        run: |
          # Generate Kubernetes manifests
          helm template ./helm/aichat \
            --set image.tag=${{ github.sha }} \
            --set environment=production \
            --output-dir ./manifests

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: deployment-manifests
          path: ./manifests/
```

### Security Workflow

#### `.github/workflows/security.yml`
```yaml
name: Security Scanning

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run OWASP ZAP scan
        uses: zaproxy/action-full-scan@v0.8.0
        with:
          target: 'https://staging.aichatapp.com'

      - name: Run dependency scanning
        run: |
          # Python dependencies
          pip install safety
          safety check --json --output safety-report.json
          
          # Node.js dependencies
          npm audit --audit-level moderate --json > npm-audit.json

      - name: Upload security reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            safety-report.json
            npm-audit.json
```

## ArgoCD Configuration

### Application Definition

#### `argocd/apps/aichat-production.yaml`
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: aichat-production
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/ai-chat-app
    targetRevision: main
    path: helm/aichat
    helm:
      values: |
        environment: production
        replicaCount:
          backend: 3
          frontend: 2
        resources:
          backend:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          frontend:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
        ingress:
          enabled: true
          host: aichatapp.com
          tls:
            enabled: true
            secretName: aichat-tls
        monitoring:
          enabled: true
          prometheus:
            enabled: true
          grafana:
            enabled: true
  destination:
    server: https://kubernetes.default.svc
    namespace: aichat-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

#### `argocd/apps/aichat-staging.yaml`
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: aichat-staging
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/ai-chat-app
    targetRevision: develop
    path: helm/aichat
    helm:
      values: |
        environment: staging
        replicaCount:
          backend: 2
          frontend: 1
        resources:
          backend:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "250m"
          frontend:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "128Mi"
              cpu: "100m"
        ingress:
          enabled: true
          host: staging.aichatapp.com
        monitoring:
          enabled: true
  destination:
    server: https://kubernetes.default.svc
    namespace: aichat-staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Helm Charts

### Main Chart Structure

#### `helm/aichat/Chart.yaml`
```yaml
apiVersion: v2
name: aichat
description: AI Chat Application Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - ai
  - chat
  - fastapi
  - react
maintainers:
  - name: AI Chat Team
    email: team@aichatapp.com
```

#### `helm/aichat/values.yaml`
```yaml
# Global configuration
global:
  environment: production
  imageRegistry: ghcr.io
  imagePullSecrets: []

# Backend configuration
backend:
  enabled: true
  replicaCount: 3
  image:
    repository: your-org/ai-chat-app/backend
    tag: latest
    pullPolicy: IfNotPresent
  
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "250m"
  
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: aichat-secrets
          key: database-url
    - name: REDIS_URL
      valueFrom:
        secretKeyRef:
          name: aichat-secrets
          key: redis-url
    - name: OPENAI_API_KEY
      valueFrom:
        secretKeyRef:
          name: aichat-secrets
          key: openai-api-key
  
  service:
    type: ClusterIP
    port: 8000
  
  ingress:
    enabled: true
    className: nginx
    annotations:
      nginx.ingress.kubernetes.io/rewrite-target: /
    hosts:
      - host: aichatapp.com
        paths:
          - path: /api
            pathType: Prefix

# Frontend configuration
frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: your-org/ai-chat-app/frontend
    tag: latest
    pullPolicy: IfNotPresent
  
  resources:
    requests:
      memory: "64Mi"
      cpu: "50m"
    limits:
      memory: "128Mi"
      cpu: "100m"
  
  env:
    - name: REACT_APP_API_URL
      value: "https://aichatapp.com/api"
    - name: REACT_APP_WS_URL
      value: "wss://aichatapp.com/ws"
  
  service:
    type: ClusterIP
    port: 80
  
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: aichatapp.com
        paths:
          - path: /
            pathType: Prefix

# Database configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: "postgres"
    database: "aichat"
  
  primary:
    persistence:
      enabled: true
      size: 10Gi
  
  metrics:
    enabled: true

# Redis configuration
redis:
  enabled: true
  auth:
    enabled: true
    password: "redis"
  
  master:
    persistence:
      enabled: true
      size: 5Gi
  
  metrics:
    enabled: true

# Monitoring configuration
monitoring:
  enabled: true
  
  prometheus:
    enabled: true
    retention: 15d
  
  grafana:
    enabled: true
    adminPassword: "admin"
    persistence:
      enabled: true
      size: 5Gi

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  
  tls:
    enabled: true
    secretName: aichat-tls
  
  hosts:
    - host: aichatapp.com
      paths:
        - path: /
          pathType: Prefix
```

## Deployment Strategies

### Blue-Green Deployment

#### Blue-Green Configuration
```yaml
# Blue-Green deployment configuration
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: aichat-backend
spec:
  replicas: 3
  strategy:
    blueGreen:
      activeService: aichat-backend-active
      previewService: aichat-backend-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: aichat-backend-preview
      postPromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: aichat-backend-active
  selector:
    matchLabels:
      app: aichat-backend
  template:
    metadata:
      labels:
        app: aichat-backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/your-org/ai-chat-app/backend:latest
        ports:
        - containerPort: 8000
```

### Canary Deployment

#### Canary Configuration
```yaml
# Canary deployment configuration
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: aichat-backend-canary
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 1m}
      - setWeight: 20
      - pause: {duration: 1m}
      - setWeight: 50
      - pause: {duration: 2m}
      - setWeight: 100
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: aichat-backend
  selector:
    matchLabels:
      app: aichat-backend
  template:
    metadata:
      labels:
        app: aichat-backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/your-org/ai-chat-app/backend:latest
```

## Environment Management

### Environment-Specific Configurations

#### Development Environment
```yaml
# values-dev.yaml
environment: development
replicaCount:
  backend: 1
  frontend: 1

resources:
  backend:
    requests:
      memory: "128Mi"
      cpu: "50m"
    limits:
      memory: "256Mi"
      cpu: "100m"

ingress:
  enabled: false

monitoring:
  enabled: false
```

#### Staging Environment
```yaml
# values-staging.yaml
environment: staging
replicaCount:
  backend: 2
  frontend: 1

resources:
  backend:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "250m"

ingress:
  enabled: true
  host: staging.aichatapp.com

monitoring:
  enabled: true
  prometheus:
    retention: 7d
```

#### Production Environment
```yaml
# values-production.yaml
environment: production
replicaCount:
  backend: 5
  frontend: 3

resources:
  backend:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"

ingress:
  enabled: true
  host: aichatapp.com
  tls:
    enabled: true

monitoring:
  enabled: true
  prometheus:
    retention: 30d
```

## Automated Testing

### E2E Testing Pipeline

#### `.github/workflows/e2e-tests.yml`
```yaml
name: E2E Tests

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Start test environment
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30

      - name: Run E2E tests
        run: |
          npm run test:e2e:ci
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

      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose.test.yml down
```

### Performance Testing

#### `.github/workflows/performance-tests.yml`
```yaml
name: Performance Tests

on:
  pull_request:
    branches: [ main ]

jobs:
  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install locust
          pip install -r requirements.txt

      - name: Start application
        run: |
          docker-compose up -d
          sleep 60

      - name: Run performance tests
        run: |
          locust -f tests/performance/locustfile.py \
            --host=http://localhost:8000 \
            --users=100 \
            --spawn-rate=10 \
            --run-time=5m \
            --headless \
            --html=performance-report.html

      - name: Upload performance report
        uses: actions/upload-artifact@v4
        with:
          name: performance-report
          path: performance-report.html
```

## Monitoring and Alerting

### Deployment Monitoring

#### Deployment Health Checks
```yaml
# Deployment health check configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: health-check-config
data:
  health-check.sh: |
    #!/bin/bash
    set -e
    
    # Check application health
    curl -f http://localhost:8000/health || exit 1
    
    # Check database connectivity
    python -c "
    import psycopg2
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    " || exit 1
    
    # Check Redis connectivity
    python -c "
    import redis
    r = redis.from_url('$REDIS_URL')
    r.ping()
    " || exit 1
    
    echo "Health check passed"
```

### Rollback Procedures

#### Automated Rollback
```yaml
# Automated rollback configuration
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: aichat-backend
spec:
  strategy:
    blueGreen:
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: aichat-backend-preview
        - name: failure-threshold
          value: "0.8"
        - name: minimum-success-rate
          value: "0.9"
      rollbackWindow:
        revisionHistoryLimit: 5
```

## Security and Compliance

### Security Scanning

#### Container Security
```yaml
# Container security scanning
- name: Container Security Scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/your-org/ai-chat-app/backend:latest'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

#### Dependency Scanning
```yaml
# Dependency vulnerability scanning
- name: Dependency Scan
  run: |
    # Python dependencies
    pip install safety
    safety check --json --output safety-report.json
    
    # Node.js dependencies
    npm audit --audit-level moderate --json > npm-audit.json
    
    # Check for critical vulnerabilities
    if jq -e '.vulnerabilities[] | select(.severity == "CRITICAL")' safety-report.json; then
      echo "Critical vulnerabilities found in Python dependencies"
      exit 1
    fi
    
    if jq -e '.vulnerabilities[] | select(.severity == "CRITICAL")' npm-audit.json; then
      echo "Critical vulnerabilities found in Node.js dependencies"
      exit 1
    fi
```

### Compliance Checks

#### Policy Enforcement
```yaml
# OPA (Open Policy Agent) policies
apiVersion: config.kubernetes.io/v1
kind: ConfigMap
metadata:
  name: aichat-policies
data:
  security-policy.rego: |
    package kubernetes.admission
    
    deny[msg] {
      input.request.kind.kind == "Pod"
      not input.request.object.spec.securityContext.runAsNonRoot
      msg := "Pods must not run as root"
    }
    
    deny[msg] {
      input.request.kind.kind == "Pod"
      not input.request.object.spec.securityContext.readOnlyRootFilesystem
      msg := "Pods must have read-only root filesystem"
    }
```

## Troubleshooting

### Common CI/CD Issues

#### Build Failures
```bash
# Debug build issues
docker build --progress=plain --no-cache -t debug-image .

# Check build context
docker build --target debug -t debug-image .

# Analyze image layers
docker history debug-image
```

#### Deployment Failures
```bash
# Check ArgoCD application status
argocd app get aichat-production

# Check Kubernetes resources
kubectl get pods -n aichat-production
kubectl describe pod <pod-name> -n aichat-production

# Check logs
kubectl logs <pod-name> -n aichat-production
kubectl logs <pod-name> -n aichat-production --previous
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -n aichat-production
kubectl describe hpa -n aichat-production

# Check metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods | jq

# Check network policies
kubectl get networkpolicies -n aichat-production
```

---

**Next Steps**: Learn about [Production Deployment](production.md) for complete production setup, or explore [Monitoring](monitoring.md) for comprehensive observability.