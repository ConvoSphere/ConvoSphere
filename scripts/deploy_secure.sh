#!/bin/bash

# ConvoSphere Secure Deployment Script
# Führt sichere Deployment-Schritte durch

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${BLUE}🚀 ConvoSphere Secure Deployment${NC}"
echo "=================================="
echo "Environment: $ENVIRONMENT"
echo "Compose file: $COMPOSE_FILE"
echo ""

# Funktionen
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Docker prüfen
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not installed${NC}"
        exit 1
    fi
    
    # Docker Compose prüfen
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose not installed${NC}"
        exit 1
    fi
    
    # Environment file prüfen
    if [ ! -f .env.production ]; then
        echo -e "${RED}❌ Production environment file missing${NC}"
        echo "Please create .env.production with proper configuration"
        exit 1
    fi
    
    # Secrets prüfen
    if [ ! -d secrets ]; then
        echo -e "${RED}❌ Secrets directory missing${NC}"
        echo "Please create secrets directory and add required secrets"
        exit 1
    fi
    
    # Required secret files
    REQUIRED_SECRETS=("openai_api_key" "secret_key" "database_url" "database_password")
    for secret in "${REQUIRED_SECRETS[@]}"; do
        if [ ! -f "secrets/$secret" ]; then
            echo -e "${RED}❌ Missing secret file: secrets/$secret${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

setup_secrets() {
    log "🔐 Setting up Docker secrets..."
    
    # Docker secrets erstellen
    docker secret create openai_api_key secrets/openai_api_key 2>/dev/null || log "Secret already exists"
    docker secret create secret_key secrets/secret_key 2>/dev/null || log "Secret already exists"
    docker secret create database_url secrets/database_url 2>/dev/null || log "Secret already exists"
    docker secret create database_password secrets/database_password 2>/dev/null || log "Secret already exists"
    
    echo -e "${GREEN}✅ Docker secrets configured${NC}"
}

security_scan() {
    log "🔒 Running security scan..."
    
    if [ -f scripts/security_scan.sh ]; then
        ./scripts/security_scan.sh
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}⚠️  Security issues found - review before continuing${NC}"
            read -p "Continue with deployment? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Deployment cancelled"
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Security scan script not found${NC}"
    fi
}

backup_existing() {
    log "💾 Creating backup of existing deployment..."
    
    if docker ps --format "table {{.Names}}" | grep -q convosphere; then
        BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Docker volumes backup
        docker run --rm -v convosphere_postgres_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
        docker run --rm -v convosphere_redis_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
        docker run --rm -v convosphere_weaviate_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/weaviate_backup.tar.gz -C /data .
        
        echo -e "${GREEN}✅ Backup created in $BACKUP_DIR${NC}"
    else
        echo -e "${YELLOW}⚠️  No existing deployment found - skipping backup${NC}"
    fi
}

stop_existing() {
    log "🛑 Stopping existing deployment..."
    
    if [ -f docker-compose.yml ]; then
        docker-compose down --remove-orphans || true
    fi
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true
    fi
    
    echo -e "${GREEN}✅ Existing deployment stopped${NC}"
}

build_images() {
    log "🔨 Building secure Docker images..."
    
    # Build with production requirements
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    echo -e "${GREEN}✅ Images built successfully${NC}"
}

deploy_services() {
    log "🚀 Deploying services..."
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be healthy
    log "⏳ Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    HEALTHY_SERVICES=0
    TOTAL_SERVICES=5  # backend, frontend, postgres, redis, weaviate
    
    for service in backend frontend postgres redis weaviate; do
        if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy"; then
            HEALTHY_SERVICES=$((HEALTHY_SERVICES + 1))
            echo -e "${GREEN}✅ $service is healthy${NC}"
        else
            echo -e "${RED}❌ $service is not healthy${NC}"
        fi
    done
    
    if [ $HEALTHY_SERVICES -eq $TOTAL_SERVICES ]; then
        echo -e "${GREEN}✅ All services are healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Some services are not healthy - check logs${NC}"
        docker-compose -f "$COMPOSE_FILE" logs --tail=50
    fi
}

run_tests() {
    log "🧪 Running security tests..."
    
    # Health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
        return 1
    fi
    
    # Security headers check
    SECURITY_HEADERS=$(curl -I http://localhost:8000/health 2>/dev/null | grep -E "(X-Content-Type-Options|X-Frame-Options|Strict-Transport-Security)" | wc -l)
    if [ $SECURITY_HEADERS -ge 3 ]; then
        echo -e "${GREEN}✅ Security headers present${NC}"
    else
        echo -e "${YELLOW}⚠️  Some security headers missing${NC}"
    fi
    
    # SSL check (if using HTTPS)
    if [ "$ENVIRONMENT" = "production" ]; then
        if curl -f https://localhost/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ HTTPS working${NC}"
        else
            echo -e "${YELLOW}⚠️  HTTPS not configured${NC}"
        fi
    fi
}

show_status() {
    log "📊 Deployment status:"
    
    echo ""
    echo "Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    echo "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    echo ""
    echo "Access URLs:"
    echo "Frontend: http://localhost:8081"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
}

cleanup() {
    log "🧹 Cleaning up..."
    
    # Remove old images
    docker image prune -f
    
    # Remove old containers
    docker container prune -f
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Hauptausführung
main() {
    echo -e "${BLUE}Starting secure deployment process...${NC}"
    
    check_prerequisites
    setup_secrets
    security_scan
    backup_existing
    stop_existing
    build_images
    deploy_services
    run_tests
    show_status
    cleanup
    
    echo ""
    echo "=================================="
    echo -e "${GREEN}🎉 Secure deployment completed successfully!${NC}"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo "1. Update DNS to point to your server"
    echo "2. Configure SSL certificates"
    echo "3. Set up monitoring and alerting"
    echo "4. Run regular security scans"
    echo ""
    echo "Documentation:"
    echo "- Security guide: SECURITY_ANALYSIS.md"
    echo "- Action plan: SECURITY_ACTION_PLAN.md"
    echo "- Monitoring: Check logs with 'docker-compose -f $COMPOSE_FILE logs'"
}

# Error handling
trap 'echo -e "${RED}❌ Deployment failed${NC}"; exit 1' ERR

# Script ausführen
main "$@"