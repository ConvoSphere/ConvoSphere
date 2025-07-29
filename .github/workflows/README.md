# GitHub Actions Workflows

This directory contains the GitHub Actions workflows for the Convosphere project. The workflows are designed to handle warnings gracefully while failing only on actual errors.

## Workflow Overview

### 1. CI/CD Pipeline (`ci-cd.yml`)
**Purpose:** Main continuous integration and deployment pipeline
**Triggers:** Push to main/master, Pull requests to main/master
**Features:**
- Quick validation with linting and security checks
- Docker image building and pushing
- Staging and production deployment
- Security scanning with Trivy

### 2. Comprehensive Test Pipeline (`test-pipeline.yml`)
**Purpose:** Comprehensive testing suite
**Triggers:** Push to main/develop, Pull requests to main/develop, Daily schedule
**Features:**
- Unit tests (Backend & Frontend)
- Integration tests
- Performance tests
- Security tests
- E2E tests
- Coverage reporting

### 3. Linting Pipeline (`lint-only.yml`)
**Purpose:** Dedicated linting and code quality checks
**Triggers:** Push to main/develop, Pull requests to main/develop
**Features:**
- Python linting (Ruff, Black, isort)
- TypeScript linting (ESLint)
- Security checks (Bandit)
- Type checking (MyPy)

## Warning vs Error Handling

### Philosophy
The workflows are designed to **fail only on actual errors** while **showing warnings for information**. This allows development to continue while maintaining code quality awareness.

### Error Classification

#### Python Linting (Ruff)
- **Errors:** Codes starting with `E` (pycodestyle errors) or `F` (pyflakes)
- **Warnings:** All other codes (style, complexity, etc.)

#### TypeScript Linting (ESLint)
- **Errors:** Issues with `severity: 2`
- **Warnings:** Issues with `severity: 1`

#### Type Checking (MyPy)
- **Errors:** Issues with `severity: "error"`
- **Warnings:** Issues with `severity: "note"` or `severity: "warning"`

#### Security (Bandit)
- **Errors:** High severity issues
- **Warnings:** Medium and low severity issues

#### Tests
- **Errors:** Actual test failures (`FAILED`, `ERROR`)
- **Warnings:** Pytest warnings, deprecation warnings, etc.

### How It Works

1. **Linting Steps:**
   ```bash
   # Run linter with output capture
   ruff check backend/ --output-format=json > ruff-report.json || true
   
   # Analyze results and fail only on errors
   python -c "
   import json
   with open('ruff-report.json', 'r') as f:
       data = json.load(f)
   errors = [issue for issue in data if issue.get('code', '').startswith(('E', 'F'))]
   if errors:
       print(f'Found {len(errors)} errors')
       exit(1)
   "
   ```

2. **Test Steps:**
   ```bash
   # Run tests with output capture
   pytest tests/ -v --tb=short -q > test-output.txt 2>&1 || true
   
   # Check for actual failures
   if grep -q "FAILED\|ERROR" test-output.txt; then
       echo "Found test failures"
       exit 1
   fi
   ```

3. **PR Comments:**
   - Automatic comments on PRs with detailed linting results
   - Shows counts of errors vs warnings
   - Provides context about what constitutes errors vs warnings

## Configuration

### Python Linting
- **Tool:** Ruff
- **Config:** `pyproject.toml`
- **Exit Codes:** 
  - `0`: No issues or only warnings
  - `1`: Errors found

### TypeScript Linting
- **Tool:** ESLint
- **Config:** `frontend-react/eslint.config.js`
- **Exit Codes:**
  - `0`: No issues or only warnings
  - `1`: Errors found

### Security Scanning
- **Tool:** Bandit
- **Config:** `pyproject.toml`
- **Exit Codes:**
  - `0`: No high severity issues
  - `1`: High severity issues found

## Benefits

1. **Development Velocity:** Teams can continue development while being aware of code quality issues
2. **Gradual Improvement:** Warnings provide guidance for incremental code quality improvements
3. **Clear Feedback:** PR comments clearly distinguish between blocking errors and informational warnings
4. **Maintainable Standards:** Prevents pipeline failures due to minor style issues while maintaining high standards

## Usage

### For Developers
1. Push code to trigger workflows
2. Check PR comments for linting results
3. Address errors (blocking) and warnings (informational) as appropriate
4. Use the detailed reports in artifacts for comprehensive analysis

### For Maintainers
1. Monitor workflow results in GitHub Actions tab
2. Review security scan results
3. Use coverage reports to maintain test quality
4. Adjust warning/error thresholds in configuration files as needed

## Customization

### Adding New Linters
1. Add the tool to the appropriate workflow
2. Configure exit code analysis for error vs warning distinction
3. Update the summary generation script
4. Add to PR comment template

### Adjusting Thresholds
- **Python:** Modify `pyproject.toml` ruff configuration
- **TypeScript:** Modify `frontend-react/eslint.config.js`
- **Security:** Modify `pyproject.toml` bandit configuration

### Changing Error/Warning Classification
Update the analysis scripts in the workflow files to change how issues are classified as errors vs warnings.