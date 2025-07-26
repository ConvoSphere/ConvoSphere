#!/bin/bash

# ConvoSphere Security Scanner
# Führt umfassende Security-Checks durch

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="security_scan_$(date +%Y%m%d_%H%M%S).log"
SCAN_RESULTS="security_results_$(date +%Y%m%d_%H%M%S).json"

echo -e "${BLUE}🔒 ConvoSphere Security Scanner${NC}"
echo "=================================="
echo "Scan started: $(date)"
echo "Log file: $LOG_FILE"
echo "Results file: $SCAN_RESULTS"
echo ""

# Funktionen
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_secret_exposure() {
    log "🔍 Checking for secret exposure..."
    
    # Suche nach hardcodierten Secrets
    SECRETS_FOUND=0
    
    # API Keys
    if grep -r "sk-[a-zA-Z0-9]" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ 2>/dev/null; then
        log "${RED}❌ Found hardcoded API keys${NC}"
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    fi
    
    # Default secrets
    if grep -r "dev-secret-key-for-development-only-change-in-production" . --exclude-dir=.git 2>/dev/null; then
        log "${RED}❌ Found default development secrets${NC}"
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    fi
    
    # Passwords in code
    if grep -r "password.*=" . --exclude-dir=.git --exclude-dir=node_modules 2>/dev/null; then
        log "${YELLOW}⚠️  Found potential password assignments${NC}"
    fi
    
    if [ $SECRETS_FOUND -eq 0 ]; then
        log "${GREEN}✅ No hardcoded secrets found${NC}"
    fi
    
    return $SECRETS_FOUND
}

check_docker_security() {
    log "🐳 Checking Docker security..."
    
    # Prüfe Docker-Compose auf exponierte Ports
    EXPOSED_PORTS=0
    
    if grep -q "5432:5432" docker-compose.yml; then
        log "${RED}❌ PostgreSQL port exposed${NC}"
        EXPOSED_PORTS=$((EXPOSED_PORTS + 1))
    fi
    
    if grep -q "6379:6379" docker-compose.yml; then
        log "${RED}❌ Redis port exposed${NC}"
        EXPOSED_PORTS=$((EXPOSED_PORTS + 1))
    fi
    
    if grep -q "8080:8080" docker-compose.yml; then
        log "${RED}❌ Weaviate port exposed${NC}"
        EXPOSED_PORTS=$((EXPOSED_PORTS + 1))
    fi
    
    if [ $EXPOSED_PORTS -eq 0 ]; then
        log "${GREEN}✅ No database ports exposed${NC}"
    fi
    
    return $EXPOSED_PORTS
}

check_dependencies() {
    log "📦 Checking dependencies for vulnerabilities..."
    
    # Python dependencies
    if command -v safety &> /dev/null; then
        log "Running safety check..."
        safety check -r requirements.txt --json --output safety_report.json 2>/dev/null || true
        if [ -f safety_report.json ]; then
            VULNERABILITIES=$(jq length safety_report.json 2>/dev/null || echo "0")
            log "Found $VULNERABILITIES vulnerabilities in Python dependencies"
        fi
    else
        log "${YELLOW}⚠️  Safety not installed - skipping dependency check${NC}"
    fi
    
    # Node.js dependencies (if applicable)
    if [ -f package.json ]; then
        if command -v npm &> /dev/null; then
            log "Running npm audit..."
            npm audit --audit-level=moderate 2>/dev/null || true
        fi
    fi
}

check_code_quality() {
    log "🔍 Checking code quality and security..."
    
    # Python code analysis
    if command -v bandit &> /dev/null; then
        log "Running bandit security analysis..."
        bandit -r backend/ -f json -o bandit_report.json 2>/dev/null || true
        if [ -f bandit_report.json ]; then
            ISSUES=$(jq '.results | length' bandit_report.json 2>/dev/null || echo "0")
            log "Found $ISSUES security issues in Python code"
        fi
    else
        log "${YELLOW}⚠️  Bandit not installed - skipping code analysis${NC}"
    fi
    
    # Check for common security anti-patterns
    log "Checking for security anti-patterns..."
    
    # SQL Injection patterns
    SQL_INJECTION_COUNT=$(grep -r "execute.*%" backend/ --include="*.py" 2>/dev/null | wc -l)
    if [ $SQL_INJECTION_COUNT -gt 0 ]; then
        log "${YELLOW}⚠️  Found $SQL_INJECTION_COUNT potential SQL injection patterns${NC}"
    fi
    
    # XSS patterns
    XSS_COUNT=$(grep -r "innerHTML\|outerHTML\|document\.write" frontend-react/ --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l)
    if [ $XSS_COUNT -gt 0 ]; then
        log "${YELLOW}⚠️  Found $XSS_COUNT potential XSS patterns${NC}"
    fi
}

check_configuration() {
    log "⚙️  Checking configuration security..."
    
    # Environment files
    if [ -f .env.production ]; then
        log "${GREEN}✅ Production environment file exists${NC}"
    else
        log "${YELLOW}⚠️  Production environment file missing${NC}"
    fi
    
    # Git ignore
    if grep -q ".env.production" .gitignore; then
        log "${GREEN}✅ Production env file in .gitignore${NC}"
    else
        log "${RED}❌ Production env file not in .gitignore${NC}"
    fi
    
    # Secrets directory
    if [ -d secrets ]; then
        log "${GREEN}✅ Secrets directory exists${NC}"
        if [ -f secrets/README.md ]; then
            log "${GREEN}✅ Secrets documentation exists${NC}"
        fi
    else
        log "${YELLOW}⚠️  Secrets directory missing${NC}"
    fi
}

check_network_security() {
    log "🌐 Checking network security..."
    
    # CORS configuration
    if grep -q "allow_origins.*\[\"\\*\"\]" backend/main.py; then
        log "${RED}❌ CORS allows all origins${NC}"
    else
        log "${GREEN}✅ CORS properly configured${NC}"
    fi
    
    # Security headers
    if grep -q "SecurityHeadersMiddleware" backend/main.py; then
        log "${GREEN}✅ Security headers middleware configured${NC}"
    else
        log "${YELLOW}⚠️  Security headers middleware not found${NC}"
    fi
}

generate_report() {
    log "📊 Generating security report..."
    
    cat > "$SCAN_RESULTS" << EOF
{
    "scan_date": "$(date -Iseconds)",
    "scan_duration": "$SECONDS seconds",
    "summary": {
        "total_issues": 0,
        "critical_issues": 0,
        "high_issues": 0,
        "medium_issues": 0,
        "low_issues": 0
    },
    "findings": []
}
EOF
    
    log "Security report generated: $SCAN_RESULTS"
}

# Hauptausführung
main() {
    SECONDS=0
    
    log "Starting comprehensive security scan..."
    
    # Führe alle Checks durch
    check_secret_exposure
    SECRET_ISSUES=$?
    
    check_docker_security
    DOCKER_ISSUES=$?
    
    check_dependencies
    check_code_quality
    check_configuration
    check_network_security
    
    # Generiere Report
    generate_report
    
    # Zusammenfassung
    TOTAL_ISSUES=$((SECRET_ISSUES + DOCKER_ISSUES))
    
    echo ""
    echo "=================================="
    echo -e "${BLUE}🔒 Security Scan Complete${NC}"
    echo "=================================="
    echo "Duration: $SECONDS seconds"
    echo "Total issues found: $TOTAL_ISSUES"
    echo "Log file: $LOG_FILE"
    echo "Results file: $SCAN_RESULTS"
    
    if [ $TOTAL_ISSUES -eq 0 ]; then
        echo -e "${GREEN}✅ No critical security issues found${NC}"
        exit 0
    else
        echo -e "${RED}❌ Critical security issues found - review required${NC}"
        exit 1
    fi
}

# Script ausführen
main "$@"