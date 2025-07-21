# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the AI Assistant Platform. These workflows automate testing, code quality checks, documentation deployment, and CI/CD processes.

## 📋 Available Workflows

### 1. **Documentation Deployment** (`docs.yml`)
Automatically builds and deploys documentation to GitHub Pages.

**Triggers:**
- Push to `main` or `master` branch
- Changes to `docs/`, `mkdocs.yml`, or workflow file
- Manual trigger

**Features:**
- Builds MkDocs documentation with Material theme
- Deploys to GitHub Pages
- Includes Mermaid diagrams and plugins
- Automatic versioning with git revision dates

**Usage:**
```bash
# Documentation will be automatically deployed when you push to main
git push origin main

# Manual deployment
# Go to Actions tab → Deploy Documentation → Run workflow
```

### 2. **Code Quality Checks** (`code-quality.yml`)
Comprehensive code quality and security checks.

**Triggers:**
- Push to `main`, `master`, or `develop` branch
- Pull requests to main branches
- Manual trigger

**Checks:**
- **Ruff**: Linting and formatting
- **Bandit**: Security vulnerability scanning
- **MyPy**: Type checking
- **Pytest**: Unit tests with coverage
- **Documentation**: Build verification

**Features:**
- Parallel job execution for faster feedback
- Artifact uploads for reports
- Quality summary with GitHub step summaries
- Coverage reporting

**Usage:**
```bash
# Automatic on push/PR
git push origin feature-branch

# Manual run
# Go to Actions tab → Code Quality Checks → Run workflow
```

### 3. **CI/CD Pipeline** (`ci-cd.yml`)
Complete CI/CD pipeline for testing, building, and deployment.

**Triggers:**
- Push to `main` or `master` branch
- Pull requests to main branches
- Manual trigger

**Pipeline Stages:**
1. **Test and Build**: Comprehensive testing with services
2. **Build Images**: Docker image building and pushing
3. **Deploy Staging**: Automatic staging deployment
4. **Deploy Production**: Manual approval deployment
5. **Performance Testing**: Load and performance tests
6. **Security Scanning**: Vulnerability scanning with Trivy

**Features:**
- Full service testing (PostgreSQL, Redis, Weaviate)
- Docker image building with caching
- Multi-environment deployment
- Security vulnerability scanning
- Performance testing

## 🚀 Quick Start

### 1. Enable GitHub Pages
1. Go to repository Settings → Pages
2. Source: "GitHub Actions"
3. Save

### 2. Set up Environments (Optional)
For staging and production deployments:

1. Go to repository Settings → Environments
2. Create `staging` environment
3. Create `production` environment with protection rules

### 3. Configure Secrets (if needed)
Go to repository Settings → Secrets and variables → Actions:

- `DOCKER_REGISTRY_TOKEN`: For private Docker registry
- `DEPLOYMENT_SSH_KEY`: For server deployments
- `KUBECONFIG`: For Kubernetes deployments

## 📊 Workflow Status

### Documentation Deployment
- ✅ Automatic deployment to GitHub Pages
- ✅ MkDocs Material theme
- ✅ Mermaid diagram support
- ✅ Search functionality
- ✅ Mobile responsive

### Code Quality
- ✅ Ruff linting and formatting
- ✅ Bandit security scanning
- ✅ MyPy type checking
- ✅ Pytest with coverage
- ✅ Parallel execution
- ✅ Artifact reports

### CI/CD Pipeline
- ✅ Full service testing
- ✅ Docker image building
- ✅ Multi-environment deployment
- ✅ Security scanning
- ✅ Performance testing

## 🔧 Configuration

### Environment Variables
Workflows use these environment variables:

```yaml
# Database
DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
REDIS_URL: redis://localhost:6379
WEAVIATE_URL: http://localhost:8080

# Security
SECRET_KEY: test-secret-key
DEBUG: true

# Docker
REGISTRY: ghcr.io
IMAGE_NAME: ${{ github.repository }}
```

### Service Configuration
Services are configured with health checks:

- **PostgreSQL**: Health check with `pg_isready`
- **Redis**: Health check with `redis-cli ping`
- **Weaviate**: Health check with HTTP endpoint

## 📈 Monitoring and Reports

### Coverage Reports
- HTML coverage reports in `htmlcov/`
- XML coverage for CI integration
- Coverage badges and summaries

### Security Reports
- Bandit JSON reports
- Trivy vulnerability scanning
- SARIF format for GitHub Security tab

### Performance Reports
- Load testing results
- Benchmark comparisons
- Performance regression detection

## 🛠️ Local Development

### Running Workflows Locally
```bash
# Install dependencies
make install

# Run code quality checks
make code-quality

# Run tests
make test

# Build documentation
make docs-build

# Serve documentation locally
make docs-serve
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
make pre-commit-install

# Run hooks on all files
make pre-commit-run

# Update hooks
make pre-commit-update
```

## 🔍 Troubleshooting

### Common Issues

1. **Documentation Build Fails**
   - Check MkDocs configuration
   - Verify all dependencies are installed
   - Check for syntax errors in markdown files

2. **Tests Fail**
   - Ensure all services are running
   - Check environment variables
   - Verify database migrations

3. **Docker Build Fails**
   - Check Dockerfile syntax
   - Verify build context
   - Check for missing files

4. **Security Scan Issues**
   - Review Bandit/Trivy reports
   - Address high-severity vulnerabilities
   - Suppress false positives if needed

### Debugging Workflows

1. **Enable Debug Logging**
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
   ```

2. **Check Workflow Logs**
   - Go to Actions tab
   - Click on failed workflow
   - Review step logs

3. **Re-run Failed Jobs**
   - Use "Re-run jobs" option
   - Check for transient issues

## 📚 Related Documentation

- [MkDocs Configuration](../mkdocs.yml)
- [Pre-commit Configuration](../.pre-commit-config.yaml)
- [PyProject Configuration](../pyproject.toml)
- [Makefile](../Makefile)

## 🤝 Contributing

When contributing to workflows:

1. Test changes locally first
2. Use `workflow_dispatch` for testing
3. Update documentation
4. Follow the existing patterns
5. Add appropriate error handling

## 📄 License

These workflows are part of the AI Assistant Platform and follow the same license terms.