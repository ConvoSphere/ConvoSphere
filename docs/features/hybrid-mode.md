# Hybrid Mode Feature

## Overview

The Hybrid Mode feature enables intelligent switching between Chat and Agent modes based on query complexity, available tools, and conversation context. This provides users with the optimal interaction experience while maintaining full control over mode selection.

## Features

### Core Functionality

- **Automatic Mode Switching**: Intelligently switches between Chat and Agent modes based on analysis
- **Manual Mode Control**: Users can manually override automatic decisions
- **Structured Output**: Provides detailed reasoning and decision-making process
- **Agent Memory**: Maintains context and memory across conversations
- **Progress Visualization**: Real-time feedback on processing steps
- **Configuration Management**: Customizable thresholds and settings

### Modes

#### Chat Mode
- **Purpose**: Direct conversational responses
- **Characteristics**: 
  - Simple, friendly responses
  - No tool usage
  - Fast processing
  - Ideal for casual conversation and simple questions

#### Agent Mode
- **Purpose**: Tool-enabled responses with reasoning
- **Characteristics**:
  - Step-by-step reasoning
  - Tool execution capabilities
  - External resource access
  - Detailed analysis and actions

#### Auto Mode
- **Purpose**: Automatic mode selection
- **Characteristics**:
  - Smart switching based on query analysis
  - Complexity assessment
  - Context awareness
  - Tool relevance evaluation

## Architecture

### Components

#### Backend Components

1. **HybridModeManager** (`backend/app/services/hybrid_mode_manager.py`)
   - Core management service
   - Mode decision logic
   - State management
   - Integration with other services

2. **ComplexityAnalyzer**
   - Analyzes query complexity
   - Evaluates multiple factors:
     - Message length
     - Keyword complexity
     - Context dependency
     - Multi-step indicators

3. **AgentMemoryManager**
   - Manages conversation memory
   - Context retention
   - Relevance scoring
   - Memory cleanup

4. **AgentReasoningEngine**
   - Generates reasoning steps
   - Tool relevance analysis
   - Context evaluation
   - Decision confidence calculation

#### Frontend Components

1. **HybridModeSelector** (`frontend-react/src/components/chat/HybridModeSelector.tsx`)
   - Mode selection interface
   - Configuration management
   - Visual mode indicators

2. **AgentReasoningDisplay** (`frontend-react/src/components/chat/AgentReasoningDisplay.tsx`)
   - Shows reasoning process
   - Expandable thought steps
   - Mode decision visualization

3. **ProgressVisualization** (`frontend-react/src/components/chat/ProgressVisualization.tsx`)
   - Real-time progress tracking
   - Step-by-step visualization
   - Tool usage indicators

### Data Models

#### Schemas (`backend/app/schemas/hybrid_mode.py`)

```python
class ConversationMode(str, Enum):
    CHAT = "chat"
    AGENT = "agent"
    AUTO = "auto"

class ModeDecision(BaseModel):
    conversation_id: UUID
    user_message: str
    current_mode: ConversationMode
    recommended_mode: ConversationMode
    reason: ModeDecisionReason
    confidence: float
    complexity_score: float
    reasoning_steps: List[AgentReasoning]
    # ... additional fields

class StructuredResponse(BaseModel):
    content: str
    mode_decision: ModeDecision
    tool_calls: List[Dict[str, Any]]
    reasoning_process: List[AgentReasoning]
    # ... additional fields
```

## API Endpoints

### Hybrid Mode Management

#### Initialize Hybrid Mode
```http
POST /api/v1/hybrid-mode/conversations/{conversation_id}/initialize
```

#### Change Mode
```http
POST /api/v1/hybrid-mode/conversations/{conversation_id}/mode/change
```

#### Get Mode Status
```http
GET /api/v1/hybrid-mode/conversations/{conversation_id}/mode/status
```

#### Get Mode Decision
```http
POST /api/v1/hybrid-mode/conversations/{conversation_id}/mode/decide
```

#### Update Configuration
```http
PUT /api/v1/hybrid-mode/conversations/{conversation_id}/config
```

#### Get Mode History
```http
GET /api/v1/hybrid-mode/conversations/{conversation_id}/mode/history
```

#### Get Statistics
```http
GET /api/v1/hybrid-mode/stats
```

#### Get Available Modes
```http
GET /api/v1/hybrid-mode/modes
```

### Enhanced Chat Endpoints

#### Send Message with Hybrid Mode
```http
POST /api/v1/chat/conversations/{conversation_id}/messages
```

Response includes structured output with mode decision and reasoning.

## Configuration

### Hybrid Mode Settings

```python
class HybridModeConfig(BaseModel):
    auto_mode_enabled: bool = True
    complexity_threshold: float = 0.7
    confidence_threshold: float = 0.8
    context_window_size: int = 10
    memory_retention_hours: int = 24
    reasoning_steps_max: int = 5
    tool_relevance_threshold: float = 0.6
```

### Configuration Parameters

- **auto_mode_enabled**: Enable/disable automatic mode switching
- **complexity_threshold**: Threshold for switching to agent mode (0.0-1.0)
- **confidence_threshold**: Minimum confidence for mode decisions (0.0-1.0)
- **context_window_size**: Number of messages to consider for context
- **memory_retention_hours**: How long to retain conversation memory
- **reasoning_steps_max**: Maximum number of reasoning steps to generate
- **tool_relevance_threshold**: Threshold for tool relevance (0.0-1.0)

## Usage Examples

### Basic Usage

1. **Create a conversation** - Hybrid mode is automatically initialized
2. **Send messages** - System automatically decides the best mode
3. **View reasoning** - Expand reasoning steps to see decision process
4. **Override mode** - Manually switch modes using the selector

### Advanced Configuration

```javascript
// Configure hybrid mode settings
const config = {
  auto_mode_enabled: true,
  complexity_threshold: 0.6,
  confidence_threshold: 0.75,
  context_window_size: 15,
  memory_retention_hours: 48,
  reasoning_steps_max: 8,
  tool_relevance_threshold: 0.5
};

// Update configuration
await fetch(`/api/v1/hybrid-mode/conversations/${conversationId}/config`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(config)
});
```

### Force Specific Mode

```javascript
// Force agent mode for a message
const response = await fetch(`/api/v1/chat/conversations/${conversationId}/messages`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Analyze this data",
    force_mode: "agent"
  })
});
```

## Decision Logic

### Complexity Analysis

The system analyzes query complexity based on:

1. **Message Length**: Longer messages indicate higher complexity
2. **Keywords**: Complex action words (analyze, generate, research, etc.)
3. **Context Dependency**: Number of previous messages
4. **Multi-step Indicators**: Sequential action words (first, then, next, etc.)

### Tool Relevance

Evaluates available tools against user query:

1. **Keyword Matching**: Tool names vs. query content
2. **Action Alignment**: Tool capabilities vs. requested actions
3. **Context Relevance**: Tool usage in conversation history

### Context Evaluation

Assesses conversation context:

1. **Message History**: Recent conversation patterns
2. **Agent Indicators**: Previous tool usage or complex requests
3. **Topic Continuity**: Related queries requiring agent capabilities

## Integration

### With Existing Services

#### AssistantEngine Integration
- Enhanced with hybrid mode decision making
- Structured response generation
- Mode-aware tool execution

#### ConversationService Integration
- Mode metadata storage
- History tracking
- Context preservation

#### ToolExecutor Integration
- Mode-aware tool availability
- Execution tracking
- Result integration

### Frontend Integration

#### Chat Interface
- Mode selector component
- Reasoning display
- Progress visualization
- Configuration panel

#### Styling
- Mode-specific visual indicators
- Responsive design
- Dark mode support
- Accessibility features

## Testing

### Unit Tests

Comprehensive test coverage for:

- Complexity analysis
- Memory management
- Reasoning generation
- Mode decision logic
- State management

### Integration Tests

End-to-end testing of:

- Complete workflow
- API endpoints
- Frontend components
- Error handling

### Performance Tests

- Memory usage
- Response times
- Scalability
- Resource consumption

## Monitoring and Analytics

### Metrics

- Mode distribution
- Decision accuracy
- User satisfaction
- Performance metrics

### Logging

- Mode changes
- Decision reasoning
- Error tracking
- Usage patterns

## Security Considerations

### Access Control

- User-specific mode configurations
- Conversation isolation
- Permission validation

### Data Privacy

- Memory retention policies
- Context cleanup
- Sensitive data handling

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Improved decision accuracy
   - User preference learning
   - Adaptive thresholds

2. **Advanced Memory Management**
   - Long-term memory
   - Cross-conversation context
   - Memory optimization

3. **Enhanced Reasoning**
   - Multi-agent collaboration
   - Advanced reasoning chains
   - External knowledge integration

4. **Customization Options**
   - User-defined rules
   - Custom thresholds
   - Personalized modes

### Roadmap

- **Phase 1**: Core functionality (✅ Complete)
- **Phase 2**: Advanced reasoning and memory
- **Phase 3**: Machine learning integration
- **Phase 4**: Multi-agent collaboration

## Troubleshooting

### Common Issues

1. **Mode not switching automatically**
   - Check configuration settings
   - Verify complexity thresholds
   - Review conversation context

2. **Reasoning not displayed**
   - Ensure agent mode is active
   - Check frontend component loading
   - Verify API responses

3. **Performance issues**
   - Monitor memory usage
   - Check reasoning step limits
   - Review tool execution times

### Debug Information

Enable debug logging to see:

- Decision reasoning
- Complexity scores
- Tool relevance
- Memory operations

## Support

For technical support and questions:

- Check the API documentation
- Review the test suite
- Consult the troubleshooting guide
- Contact the development team

## Contributing

To contribute to the hybrid mode feature:

1. Review the architecture documentation
2. Follow the coding standards
3. Add comprehensive tests
4. Update documentation
5. Submit pull requests

## License

This feature is part of the main project and follows the same licensing terms. 