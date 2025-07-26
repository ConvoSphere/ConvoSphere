# Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for the ChatAssistant project. The tests are organized by type and follow best practices for maintainability and scalability.

## Test Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── backend/         # Backend unit tests
│   │   ├── api/         # API endpoint tests
│   │   ├── services/    # Service layer tests
│   │   ├── models/      # Model tests
│   │   └── utils/       # Utility function tests
│   └── frontend/        # Frontend unit tests
│       ├── components/  # React component tests
│       ├── hooks/       # Custom hook tests
│       ├── store/       # State management tests
│       └── utils/       # Utility function tests
├── integration/         # Integration tests
│   ├── api/            # API integration tests
│   ├── database/       # Database integration tests
│   └── external/       # External service integration tests
├── e2e/                # End-to-end tests
│   ├── user-flows/     # Complete user workflow tests
│   └── scenarios/      # Specific test scenarios
├── performance/        # Performance and load tests
├── security/           # Security and authentication tests
├── blackbox/           # Black box testing
├── fixtures/           # Test data and fixtures
├── conftest.py         # Pytest configuration
├── setup.ts            # Test setup for frontend
└── vitest.config.ts    # Vitest configuration
```

## Test Categories

### Unit Tests (`unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single function, class, or component
- **Speed**: Fast execution
- **Dependencies**: Mocked external dependencies

### Integration Tests (`integration/`)
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Speed**: Medium execution
- **Dependencies**: Real database, mocked external services

### End-to-End Tests (`e2e/`)
- **Purpose**: Test complete user workflows
- **Scope**: Full application stack
- **Speed**: Slow execution
- **Dependencies**: Real environment

### Performance Tests (`performance/`)
- **Purpose**: Test system performance under load
- **Scope**: Load testing, stress testing
- **Speed**: Variable execution time
- **Dependencies**: Test environment

### Security Tests (`security/`)
- **Purpose**: Test security vulnerabilities
- **Scope**: Authentication, authorization, data protection
- **Speed**: Medium execution
- **Dependencies**: Security testing tools

## Running Tests

### Backend Tests
```bash
# Run all backend tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e

# Run tests with coverage
pytest --cov=backend/app --cov-report=html

# Run tests in parallel
pytest -n auto
```

### Frontend Tests
```bash
# Navigate to frontend directory
cd frontend-react

# Run all frontend tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### E2E Tests
```bash
# Run E2E tests
pytest tests/e2e/

# Run specific E2E scenarios
pytest tests/e2e/user-flows/
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- Test discovery paths
- Markers for test categorization
- Coverage settings
- Parallel execution settings

### Vitest Configuration (`vitest.config.ts`)
- Frontend test environment
- Coverage settings
- Test file patterns

## Test Data Management

### Fixtures (`fixtures/`)
- Reusable test data
- Database fixtures
- Mock data for external services

### Test Database
- Separate test database
- Automatic cleanup between tests
- Isolated test environment

## Best Practices

### Writing Tests
1. **Arrange-Act-Assert**: Structure tests clearly
2. **Descriptive Names**: Use clear, descriptive test names
3. **Single Responsibility**: Each test should test one thing
4. **Independent**: Tests should not depend on each other
5. **Fast**: Tests should run quickly

### Test Organization
1. **Group Related Tests**: Use test classes or modules
2. **Consistent Naming**: Follow naming conventions
3. **Documentation**: Document complex test scenarios
4. **Maintenance**: Keep tests up to date with code changes

### Coverage
- **Target**: 80% minimum coverage
- **Focus**: Critical business logic
- **Exclude**: Generated code, configuration files

## Continuous Integration

### GitHub Actions
- Automated test execution on pull requests
- Coverage reporting
- Test result notifications
- Parallel test execution

### Test Reports
- HTML coverage reports
- Test execution summaries
- Performance metrics
- Security scan results

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure test database is running
2. **Environment Variables**: Set required test environment variables
3. **Dependencies**: Install all test dependencies
4. **Permissions**: Ensure proper file permissions

### Debugging Tests
1. **Verbose Output**: Use `-v` flag for detailed output
2. **Debug Mode**: Use `--pdb` for interactive debugging
3. **Logging**: Enable debug logging for troubleshooting
4. **Isolation**: Run tests individually to isolate issues

## Contributing

### Adding New Tests
1. Follow the existing structure
2. Use appropriate test categories
3. Add proper documentation
4. Ensure test independence
5. Update coverage targets if needed

### Test Maintenance
1. Regular review of test quality
2. Update tests when code changes
3. Remove obsolete tests
4. Optimize slow tests
5. Maintain test data freshness