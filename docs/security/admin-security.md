# Security Configuration for Administrators

This guide provides comprehensive security configuration and management for ConvoSphere administrators.

## 🔧 Security Setup

### Initial Security Configuration

#### 1. Environment Setup
```bash
# Create production environment file
cp .env.production .env.production.backup

# Generate secure secrets
openssl rand -hex 32 > secrets/secret_key
openssl rand -base64 32 > secrets/database_password
echo "sk-your-actual-openai-key" > secrets/openai_api_key
echo "postgresql://convosphere:$(cat secrets/database_password)@postgres:5432/convosphere" > secrets/database_url

# Set proper permissions
chmod 600 secrets/*
chown root:root secrets/*
```

#### 2. Docker Secrets Configuration
```bash
# Create Docker secrets
docker secret create openai_api_key secrets/openai_api_key
docker secret create secret_key secrets/secret_key
docker secret create database_url secrets/database_url
docker secret create database_password secrets/database_password

# Verify secrets
docker secret ls
```

#### 3. Network Security
```bash
# Configure firewall rules
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 22/tcp   # SSH (restrict to specific IPs)
ufw deny 5432/tcp  # PostgreSQL
ufw deny 6379/tcp  # Redis
ufw deny 8080/tcp  # Weaviate

# Enable firewall
ufw enable
ufw status
```

## 🛡️ Security Monitoring

### Security Dashboard Setup

#### 1. Monitoring Configuration
```yaml
# docker-compose.prod.yml additions
services:
  security-monitor:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure-password
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - internal-network
```

#### 2. Log Aggregation
```bash
# Configure log forwarding
docker-compose -f docker-compose.prod.yml logs -f | \
  grep -E "(ERROR|WARN|SECURITY)" | \
  tee -a /var/log/convosphere/security.log
```

#### 3. Alert Configuration
```python
# backend/app/core/security_alerts.py
ALERT_THRESHOLDS = {
    "failed_logins": 5,      # Alert after 5 failed logins
    "rate_limit_exceeded": 10, # Alert after 10 rate limit violations
    "suspicious_activity": 3,  # Alert after 3 suspicious events
    "api_errors": 20,         # Alert after 20 API errors
}
```

### Security Metrics

#### Key Performance Indicators (KPIs)
- **Mean Time to Detection (MTTD)**: < 1 hour
- **Mean Time to Response (MTTR)**: < 4 hours
- **Security Incident Rate**: 0 per month
- **Failed Authentication Attempts**: < 100 per day
- **Rate Limit Violations**: < 50 per day

#### Monitoring Dashboard
```bash
# Access security dashboard
curl -u admin:secure-password http://localhost:3000/api/dashboards/db/security

# Security metrics endpoint
curl http://localhost:8000/api/v1/admin/security/metrics
```

## 🔐 Access Control

### User Management

#### 1. Role-Based Access Control (RBAC)
```python
# User roles and permissions
ROLES = {
    "user": ["read:own", "write:own", "delete:own"],
    "premium": ["read:own", "write:own", "delete:own", "export:own"],
    "moderator": ["read:all", "write:own", "delete:reported", "moderate:content"],
    "admin": ["read:all", "write:all", "delete:all", "manage:users", "manage:system"]
}
```

#### 2. Session Management
```python
# Session configuration
SESSION_CONFIG = {
    "timeout": 3600,           # 1 hour
    "max_sessions": 5,         # Max concurrent sessions
    "inactivity_timeout": 1800, # 30 minutes
    "secure_cookies": True,
    "http_only": True,
    "same_site": "strict"
}
```

#### 3. IP Whitelisting
```bash
# Configure IP whitelist for admin access
ALLOWED_ADMIN_IPS=(
    "192.168.1.100"
    "10.0.0.50"
    "203.0.113.25"
)

# Update nginx configuration
echo "allow ${ALLOWED_ADMIN_IPS[@]};" >> /etc/nginx/conf.d/admin.conf
echo "deny all;" >> /etc/nginx/conf.d/admin.conf
```

## 🚨 Incident Response

### Security Incident Procedures

#### 1. Incident Classification
```python
INCIDENT_LEVELS = {
    "critical": {
        "response_time": "immediate",
        "notification": ["security_team", "management", "legal"],
        "actions": ["isolate", "investigate", "remediate", "report"]
    },
    "high": {
        "response_time": "1 hour",
        "notification": ["security_team", "management"],
        "actions": ["investigate", "remediate", "document"]
    },
    "medium": {
        "response_time": "4 hours",
        "notification": ["security_team"],
        "actions": ["investigate", "remediate"]
    },
    "low": {
        "response_time": "24 hours",
        "notification": ["security_team"],
        "actions": ["document", "monitor"]
    }
}
```

#### 2. Response Playbook
```bash
#!/bin/bash
# incident_response.sh

INCIDENT_TYPE=$1
SEVERITY=$2

case $SEVERITY in
    "critical")
        # Immediate actions
        docker-compose -f docker-compose.prod.yml stop
        notify_security_team "CRITICAL: $INCIDENT_TYPE"
        isolate_affected_systems
        ;;
    "high")
        # High priority actions
        notify_security_team "HIGH: $INCIDENT_TYPE"
        increase_monitoring
        ;;
    "medium")
        # Medium priority actions
        log_incident "$INCIDENT_TYPE"
        monitor_closely
        ;;
    "low")
        # Low priority actions
        log_incident "$INCIDENT_TYPE"
        ;;
esac
```

#### 3. Communication Plan
```yaml
# communication_plan.yml
incident_communications:
  internal:
    - security_team: "immediate"
    - management: "within_1_hour"
    - legal_team: "within_2_hours"
  
  external:
    - users: "within_24_hours"
    - regulators: "within_72_hours"
    - public: "as_needed"
```

## 🔍 Security Auditing

### Audit Configuration

#### 1. Audit Logging
```python
# Audit log configuration
AUDIT_CONFIG = {
    "enabled": True,
    "log_level": "INFO",
    "retention_days": 365,
    "events": [
        "user_login",
        "user_logout",
        "data_access",
        "data_modification",
        "admin_actions",
        "security_events"
    ]
}
```

#### 2. Compliance Monitoring
```bash
# GDPR compliance checks
./scripts/compliance_check.sh

# Security compliance report
./scripts/security_audit.sh --compliance
```

#### 3. Penetration Testing
```bash
# Automated security testing
./scripts/security_scan.sh --full

# Manual penetration testing checklist
./scripts/penetration_test.sh
```

## 🔄 Security Maintenance

### Regular Maintenance Tasks

#### 1. Weekly Tasks
```bash
# Security updates
apt-get update && apt-get upgrade -y
docker system prune -f

# Security scan
./scripts/security_scan.sh

# Backup verification
./scripts/verify_backup.sh
```

#### 2. Monthly Tasks
```bash
# Secret rotation
./scripts/rotate_secrets.sh

# Security audit
./scripts/security_audit.sh

# Compliance review
./scripts/compliance_review.sh
```

#### 3. Quarterly Tasks
```bash
# Penetration testing
./scripts/penetration_test.sh --full

# Security training
./scripts/security_training.sh

# Policy review
./scripts/policy_review.sh
```

## 📊 Security Reporting

### Report Generation

#### 1. Security Dashboard
```bash
# Generate security report
./scripts/generate_security_report.sh --monthly

# Export security metrics
curl -X GET "http://localhost:8000/api/v1/admin/security/report" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o security_report_$(date +%Y%m).json
```

#### 2. Compliance Reports
```bash
# GDPR compliance report
./scripts/gdpr_report.sh

# SOC 2 compliance report
./scripts/soc2_report.sh

# ISO 27001 compliance report
./scripts/iso27001_report.sh
```

## 🛠️ Security Tools

### Essential Security Tools

#### 1. Monitoring Tools
- **Grafana**: Security metrics visualization
- **Prometheus**: Metrics collection
- **ELK Stack**: Log aggregation and analysis
- **Wazuh**: Security information and event management

#### 2. Security Scanning
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Trivy**: Container vulnerability scanning
- **OWASP ZAP**: Web application security testing

#### 3. Backup and Recovery
- **Automated Backups**: Daily database and file backups
- **Backup Verification**: Regular backup integrity checks
- **Disaster Recovery**: Comprehensive recovery procedures
- **Business Continuity**: Minimal downtime procedures

## 📞 Emergency Contacts

### Security Team Contacts
- **Security Lead**: [security@yourdomain.com](mailto:security@yourdomain.com)
- **Incident Response**: [incidents@yourdomain.com](mailto:incidents@yourdomain.com)
- **Emergency Hotline**: +1-XXX-XXX-XXXX

### External Contacts
- **Legal Counsel**: [legal@yourdomain.com](mailto:legal@yourdomain.com)
- **Cyber Insurance**: [insurance@yourdomain.com](mailto:insurance@yourdomain.com)
- **Law Enforcement**: Local cybercrime unit

---

**Last Updated**: {{ git_revision_date_localized }}

For immediate security assistance, contact the security team at [security@yourdomain.com](mailto:security@yourdomain.com).