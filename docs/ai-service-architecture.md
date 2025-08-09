# AI Service Architecture Documentation

## Overview

The AI Service has been refactored into a modular architecture that separates concerns, improves maintainability, and enables easy extension. This document describes the new architecture, its components, and how they work together.

## Architecture Principles

### 1. Separation of Concerns
- **Core Logic**: Request building, response handling, and chat processing
- **Middleware**: RAG integration, tool management, and cost tracking
- **Types**: Strongly typed data structures for all AI operations

### 2. Modularity
- Each component has a single responsibility
- Components can be tested independently
- Easy to add new features without modifying existing code

### 3. Backward Compatibility
- All existing API endpoints continue to work
- No breaking changes for existing integrations
- Gradual migration path available

### 4. Type Safety
- Comprehensive type definitions using dataclasses
- Runtime type validation
- Better IDE support and error detection

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AIService (Orchestrator)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Request   │  │  Response   │  │    Chat     │            │
│  │  Builder    │  │  Handler    │  │  Processor  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                     │
├─────────────────────────────────────────────────────────────────┤
│                        Middleware Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │     RAG     │  │    Tool     │  │    Cost     │            │
│  │ Middleware  │  │ Middleware  │  │ Middleware  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                     │
├─────────────────────────────────────────────────────────────────┤
│                         Types Layer                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    AI Types                             │    │
│  │  - ProviderType, ModelType                             │    │
│  │  - ChatRequest, ChatResponse                           │    │
│  │  - EmbeddingRequest, EmbeddingResponse                 │    │
│  │  - RAGContext, ToolInfo, ToolCall                      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Core Components

#### 1. RequestBuilder (`core/request_builder.py`)
**Responsibility**: Building and validating AI service requests

**Key Features**:
- Parameter validation (messages, user_id, provider, etc.)
- Default model selection
- Request ID generation
- Type-safe request construction

**Methods**:
- `build_chat_request()`: Create chat completion requests
- `build_embedding_request()`: Create embedding requests
- `_validate_messages()`: Validate message format
- `_validate_provider()`: Validate provider support

#### 2. ResponseHandler (`core/response_handler.py`)
**Responsibility**: Processing and validating AI service responses

**Key Features**:
- Response validation
- Error handling and transformation
- Usage information extraction
- Metrics logging

**Methods**:
- `create_chat_response()`: Create structured chat responses
- `create_stream_response()`: Create streaming responses
- `create_embedding_response()`: Create embedding responses
- `handle_provider_error()`: Transform provider errors
- `handle_validation_error()`: Transform validation errors

#### 3. ChatProcessor (`core/chat_processor.py`)
**Responsibility**: Orchestrating chat processing logic

**Key Features**:
- Coordinates request building and response handling
- Manages provider interactions
- Handles streaming responses
- Error recovery

**Methods**:
- `process_chat_completion()`: Process synchronous chat requests
- `process_chat_completion_stream()`: Process streaming chat requests
- `process_embeddings()`: Process embedding requests
- `get_available_providers()`: Get supported providers

### Middleware Components

#### 1. RAGMiddleware (`middleware/rag_middleware.py`)
**Responsibility**: Retrieval-Augmented Generation integration

**Key Features**:
- Knowledge base integration
- Context enrichment
- Source extraction
- Relevance scoring

**Methods**:
- `process()`: Enhance messages with RAG context
- `should_apply_rag()`: Determine if RAG should be applied
- `_extract_user_messages()`: Extract user messages for RAG
- `_create_context_summary()`: Create context summaries

#### 2. ToolMiddleware (`middleware/tool_middleware.py`)
**Responsibility**: Tool integration and execution

**Key Features**:
- Tool availability management
- Tool call parsing
- Tool execution
- Result formatting

**Methods**:
- `process()`: Add tool information to messages
- `execute_tools_from_response()`: Execute tools from AI responses
- `_format_tool_prompt()`: Format tool descriptions
- `_extract_tool_calls()`: Parse tool calls from responses

#### 3. CostMiddleware (`middleware/cost_middleware.py`)
**Responsibility**: Cost tracking and usage monitoring

**Key Features**:
- Cost estimation
- Usage tracking
- Cost limits
- Usage statistics

**Methods**:
- `track_cost()`: Track request costs
- `track_streaming_cost()`: Track streaming costs
- `estimate_cost()`: Estimate costs before execution
- `get_cost_summary()`: Get cost summaries
- `check_cost_limit()`: Check cost limits

### Types Layer

#### AI Types (`types/ai_types.py`)
**Responsibility**: Type definitions for all AI operations

**Key Components**:
- **Enums**: `ProviderType`, `ModelType`
- **Config Classes**: `ProviderConfig`, `ChatConfig`
- **Request Classes**: `ChatRequest`, `EmbeddingRequest`
- **Response Classes**: `ChatResponse`, `ChatStreamResponse`, `EmbeddingResponse`
- **Context Classes**: `RAGContext`, `ToolInfo`, `ToolCall`
- **Info Classes**: `ModelInfo`, `CostInfo`

## Request Flow

### 1. Chat Completion Flow

```
User Request
    ↓
AIService.chat_completion()
    ↓
_apply_middleware()
    ├── RAGMiddleware.process() (if enabled)
    └── ToolMiddleware.process() (if enabled)
    ↓
ChatProcessor.process_chat_completion()
    ├── RequestBuilder.build_chat_request()
    ├── Provider Interaction
    └── ResponseHandler.create_chat_response()
    ↓
CostMiddleware.track_cost()
    ↓
Response to User
```

### 2. Streaming Flow

```
User Request
    ↓
AIService.chat_completion_stream()
    ↓
_apply_middleware()
    ↓
ChatProcessor.process_chat_completion_stream()
    ├── RequestBuilder.build_chat_request()
    ├── Provider Streaming
    └── ResponseHandler.create_stream_response()
    ↓
CostMiddleware.track_streaming_cost()
    ↓
Stream Response to User
```

### 3. Embedding Flow

```
User Request
    ↓
AIService.get_embeddings()
    ↓
ChatProcessor.process_embeddings()
    ├── RequestBuilder.build_embedding_request()
    ├── Provider Interaction
    └── ResponseHandler.create_embedding_response()
    ↓
CostMiddleware.track_cost()
    ↓
Response to User
```

## Error Handling

### 1. Validation Errors
- **Location**: RequestBuilder
- **Handling**: ResponseHandler.handle_validation_error()
- **Response**: User-friendly error messages

### 2. Provider Errors
- **Location**: ChatProcessor
- **Handling**: ResponseHandler.handle_provider_error()
- **Response**: Provider-specific error messages

### 3. Middleware Errors
- **Location**: Individual middleware components
- **Handling**: Graceful degradation
- **Response**: Continue without middleware features

### 4. System Errors
- **Location**: AIService
- **Handling**: Exception wrapping
- **Response**: Generic error messages

## Configuration

### Provider Configuration
```python
provider_config = ProviderConfig(
    api_key="your-api-key",
    base_url="https://api.openai.com",
    timeout=60,
    max_retries=5
)
```

### Chat Configuration
```python
chat_config = ChatConfig(
    temperature=0.7,
    max_tokens=1000,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
)
```

### Middleware Configuration
```python
# RAG Configuration
rag_middleware.max_context_chunks = 5

# Cost Configuration
cost_middleware.set_cost_limits(
    daily_limit=10.0,
    monthly_limit=100.0
)
```

## Testing Strategy

### 1. Unit Tests
- **Core Components**: Test individual components in isolation
- **Middleware**: Test middleware logic with mocked dependencies
- **Types**: Test type validation and conversion

### 2. Integration Tests
- **Pipeline Tests**: Test complete request flows
- **Middleware Integration**: Test middleware interactions
- **Error Scenarios**: Test error handling across components

### 3. Performance Tests
- **Response Time**: Measure end-to-end response times
- **Throughput**: Test concurrent request handling
- **Memory Usage**: Monitor memory consumption

## Migration Guide

### From Old AI Service

#### 1. Import Changes
```python
# Old
from backend.app.services.ai_service import AIService

# New
from backend.app.services.ai.ai_service_refactored import AIService
```

#### 2. API Compatibility
```python
# All existing method calls continue to work
ai_service = AIService(db)

# Chat completion (unchanged)
response = await ai_service.chat_completion(
    messages=messages,
    user_id=user_id,
    provider="openai"
)

# Embeddings (unchanged)
embeddings = await ai_service.get_embeddings(
    texts=texts,
    provider="openai"
)
```

#### 3. New Features
```python
# New: Enhanced error handling
try:
    response = await ai_service.chat_completion(...)
except ValueError as e:
    # Validation errors
    print(f"Validation error: {e}")
except Exception as e:
    # Provider or system errors
    print(f"Service error: {e}")

# New: Cost tracking
cost_summary = ai_service.get_cost_summary(user_id, days=30)
print(f"Total cost: ${cost_summary['total_cost']}")

# New: Usage statistics
usage_stats = ai_service.get_model_usage_stats(user_id, days=30)
print(f"GPT-4 requests: {usage_stats['gpt-4']['total_requests']}")
```

## Performance Considerations

### 1. Caching
- **Request Caching**: Cache similar requests
- **Response Caching**: Cache common responses
- **Cost Caching**: Cache cost calculations

### 2. Async Operations
- **Concurrent Processing**: Process multiple requests concurrently
- **Streaming**: Use streaming for large responses
- **Background Tasks**: Handle cost tracking asynchronously

### 3. Resource Management
- **Connection Pooling**: Reuse provider connections
- **Memory Management**: Efficient data structure usage
- **Timeout Handling**: Proper timeout configuration

## Security Considerations

### 1. Input Validation
- **Message Validation**: Validate all user inputs
- **Parameter Validation**: Validate all parameters
- **Type Safety**: Use strong typing throughout

### 2. Error Handling
- **Information Disclosure**: Don't expose internal errors
- **Logging**: Log errors without sensitive data
- **Rate Limiting**: Implement rate limiting

### 3. Cost Control
- **Cost Limits**: Enforce cost limits per user
- **Usage Monitoring**: Monitor usage patterns
- **Alerting**: Alert on unusual usage

## Future Enhancements

### 1. Provider Integration
- **Provider Factory**: Dynamic provider loading
- **Provider Plugins**: Plugin-based provider support
- **Provider Fallback**: Automatic provider switching

### 2. Advanced Features
- **Function Calling**: Native function calling support
- **Vision Models**: Image processing capabilities
- **Audio Models**: Speech-to-text and text-to-speech

### 3. Monitoring and Observability
- **Metrics Collection**: Comprehensive metrics
- **Tracing**: Distributed tracing support
- **Dashboard**: Real-time monitoring dashboard

## Conclusion

The new modular AI Service architecture provides:

1. **Better Maintainability**: Clear separation of concerns
2. **Improved Testability**: Isolated components
3. **Enhanced Extensibility**: Easy to add new features
4. **Strong Type Safety**: Comprehensive type definitions
5. **Backward Compatibility**: No breaking changes
6. **Better Error Handling**: Comprehensive error management
7. **Cost Control**: Built-in cost tracking and limits

This architecture serves as a solid foundation for future AI service enhancements while maintaining compatibility with existing integrations.