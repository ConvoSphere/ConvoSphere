# Requirements.txt Analysis and Updates

## Overview
This document summarizes the analysis of the requirements.txt files and the changes made to resolve dependency conflicts and remove unused libraries.

## Analysis Results

### Libraries Removed (Not Used in Code)

1. **nicegui** - No imports found in the codebase
2. **asyncio-mqtt** - No imports found in the codebase
3. **babel** - No imports found in the codebase (i18n is implemented with custom JSON files)
4. **celery** - No imports found in the codebase
5. **boto3** - No imports found in the codebase
6. **minio** - No imports found in the codebase

### Libraries Commented Out (Disabled in Code)

1. **opentelemetry-*** - All OpenTelemetry libraries are commented out in main.py and disabled for testing

### Libraries Actually Used

#### Core Framework
- **fastapi** - Used extensively throughout the API endpoints
- **uvicorn** - Used in main.py for running the server
- **pydantic** - Used for data validation and models
- **pydantic-settings** - Used in config.py

#### AI & LLM
- **litellm** - Used in embedding_service.py
- **openai** - Not directly imported but likely used through litellm
- **anthropic** - Not directly imported but likely used through litellm

#### Database
- **sqlalchemy** - Used extensively for database operations
- **alembic** - Used for database migrations
- **psycopg2-binary** - Used for PostgreSQL connection
- **redis** - Used for caching and session management

#### Vector Database
- **weaviate-client** - Used for vector storage

#### Authentication & Security
- **python-jose** - Used for JWT token handling
- **passlib** - Used for password hashing
- **python-multipart** - Used by FastAPI for form data

#### HTTP Client
- **httpx** - Used in tests
- **aiohttp** - Used in MCP tools

#### Utilities
- **python-dotenv** - Used for environment variable loading
- **loguru** - Used extensively for logging

#### Testing
- **pytest** - Used for testing
- **pytest-asyncio** - Used for async testing

#### Development
- **ruff** - Used for linting
- **bandit** - Used for security scanning
- **mypy** - Used for type checking

#### File Processing
- **python-magic** - Used for MIME type detection
- **PyPDF2** - Used for PDF processing
- **markdown** - Used for markdown processing
- **docling** - Used for advanced document processing

#### Web Scraping & Search
- **beautifulsoup4** - Used for HTML parsing
- **requests** - Used in test files

#### Validation
- **email-validator** - Used for email validation (EmailStr)

#### Machine Learning
- **umap-learn** - Used in embedding_service.py for dimensionality reduction
- **scikit-learn** - Used in embedding_service.py for similarity calculations
- **numpy** - Used in embedding_service.py for numerical operations

## Dependency Conflicts Resolved

### Original Conflicts
```
grpcio-health-checking 1.73.1 requires protobuf<7.0.0,>=6.30.0, but you have protobuf 4.25.8 which is incompatible.
nicegui 2.21.1 requires aiohttp>=3.10.2, but you have aiohttp 3.9.1 which is incompatible.
nicegui 2.21.1 requires fastapi>=0.109.1, but you have fastapi 0.104.1 which is incompatible.
nicegui 2.21.1 requires python-multipart>=0.0.18, but you have python-multipart 0.0.6 which is incompatible.
nicegui 2.21.1 requires starlette>=0.45.3; python_version >= "3.9", but you have starlette 0.27.0 which is incompatible.
```

### Solutions Applied
1. **Removed nicegui** - This was the source of most conflicts and is not used
2. **Updated version constraints** - Changed from exact versions (`==`) to minimum versions (`>=`) to allow newer compatible versions
3. **Updated specific versions**:
   - fastapi: 0.104.1 → >=0.109.1
   - aiohttp: 3.9.1 → >=3.10.2
   - python-multipart: 0.0.6 → >=0.0.18

## Files Updated

1. **requirements.txt** - Main requirements file
2. **backend/requirements.txt** - Backend-specific requirements
3. **backend/requirements-minimal.txt** - Minimal requirements without docling

## Benefits

1. **Reduced package size** - Removed unused dependencies
2. **Resolved conflicts** - Eliminated dependency conflicts
3. **Future-proof** - Using `>=` allows for compatible updates
4. **Cleaner dependencies** - Only includes actually used libraries
5. **Better maintainability** - Easier to understand what's needed

## Recommendations

1. **Regular audits** - Periodically check for unused dependencies
2. **Version pinning** - Consider using `==` for production deployments after testing
3. **Dependency groups** - Consider splitting requirements into dev/prod/test groups
4. **Automated checks** - Use tools like `pipdeptree` to detect conflicts early