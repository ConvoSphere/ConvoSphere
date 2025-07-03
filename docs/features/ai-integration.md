# AI Integration

## Overview

The AI Assistant Platform integrates with multiple AI providers through LiteLLM, providing a unified interface for different language models and ensuring high availability through fallback mechanisms.

## Supported Providers

### OpenAI
- **Models**: GPT-4, GPT-3.5-turbo, GPT-4-turbo
- **Features**: Chat completion, function calling, streaming
- **Configuration**: API key required

### Anthropic (Claude)
- **Models**: Claude-3-opus, Claude-3-sonnet, Claude-3-haiku
- **Features**: Chat completion, tool use, streaming
- **Configuration**: API key required

### Local Models
- **Models**: Ollama, LM Studio, vLLM
- **Features**: Local deployment, privacy-focused
- **Configuration**: Local endpoint URL

## Configuration

### Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Local Models
OLLAMA_BASE_URL=http://localhost:11434
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# Default Configuration
DEFAULT_AI_MODEL=gpt-4
DEFAULT_AI_PROVIDER=openai
```

### Provider Configuration

```python
# app/core/config.py
class AISettings(BaseSettings):
    # Provider API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Local Model Endpoints
    ollama_base_url: str = "http://localhost:11434"
    lm_studio_base_url: str = "http://localhost:1234/v1"
    
    # Default Settings
    default_model: str = "gpt-4"
    default_provider: str = "openai"
    
    # Fallback Configuration
    fallback_models: List[str] = ["gpt-3.5-turbo", "claude-3-haiku"]
    max_retries: int = 3
    timeout: int = 30
```

## LiteLLM Integration

### Service Implementation

```python
# app/services/ai_service.py
import litellm
from typing import Dict, List, Optional

class AIService:
    def __init__(self):
        self.configure_providers()
    
    def configure_providers(self):
        """Configure AI providers with LiteLLM."""
        # Configure OpenAI
        if settings.openai_api_key:
            litellm.set_verbose = True
            litellm.api_key = settings.openai_api_key
        
        # Configure Anthropic
        if settings.anthropic_api_key:
            litellm.anthropic_key = settings.anthropic_api_key
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict:
        """Generate chat completion with fallback support."""
        model = model or settings.default_model
        
        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )
            return response
        except Exception as e:
            logger.warning(f"Primary model {model} failed: {e}")
            return await self._fallback_completion(
                messages, temperature, max_tokens, tools
            )
    
    async def _fallback_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        tools: Optional[List[Dict]]
    ) -> Dict:
        """Try fallback models if primary model fails."""
        for fallback_model in settings.fallback_models:
            try:
                response = await litellm.acompletion(
                    model=fallback_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools
                )
                logger.info(f"Fallback to {fallback_model} successful")
                return response
            except Exception as e:
                logger.warning(f"Fallback model {fallback_model} failed: {e}")
                continue
        
        raise Exception("All AI models failed")
```

## Model Management

### Assistant Configuration

```python
# Assistant model configuration
class AssistantCreate(BaseModel):
    name: str
    description: str
    model: str = "gpt-4"
    provider: str = "openai"
    temperature: float = 0.7
    max_tokens: Optional[int] = 4000
    system_prompt: str
    tools: List[str] = []
```

### Model Selection

```python
# Dynamic model selection based on requirements
def select_model(
    complexity: str = "medium",
    cost_sensitive: bool = False,
    speed_priority: bool = False
) -> str:
    """Select appropriate model based on requirements."""
    if cost_sensitive:
        return "gpt-3.5-turbo"
    elif speed_priority:
        return "claude-3-haiku"
    elif complexity == "high":
        return "gpt-4"
    else:
        return "claude-3-sonnet"
```

## Streaming Support

### Real-time Responses

```python
async def stream_chat_completion(
    self,
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """Stream chat completion responses."""
    try:
        async for chunk in litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True
        ):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        yield "Sorry, I encountered an error while processing your request."
```

## Tool Integration

### Function Calling

```python
# Tool definitions for function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Execute with tools
response = await ai_service.chat_completion(
    messages=messages,
    model="gpt-4",
    tools=tools
)
```

## Cost Management

### Token Tracking

```python
class TokenTracker:
    def __init__(self):
        self.usage = {}
    
    def track_usage(self, model: str, tokens_used: int, cost: float):
        """Track token usage and costs."""
        if model not in self.usage:
            self.usage[model] = {"tokens": 0, "cost": 0.0}
        
        self.usage[model]["tokens"] += tokens_used
        self.usage[model]["cost"] += cost
    
    def get_usage_report(self) -> Dict:
        """Generate usage report."""
        return {
            "total_tokens": sum(u["tokens"] for u in self.usage.values()),
            "total_cost": sum(u["cost"] for u in self.usage.values()),
            "by_model": self.usage
        }
```

### Cost Optimization

```python
def optimize_for_cost(
    messages: List[Dict[str, str]],
    max_cost: float = 0.10
) -> str:
    """Select cost-effective model based on message length."""
    total_tokens = sum(len(msg["content"].split()) for msg in messages)
    
    if total_tokens < 1000:
        return "gpt-3.5-turbo"  # Cheaper for short conversations
    elif total_tokens < 4000:
        return "claude-3-haiku"  # Good balance
    else:
        return "gpt-4"  # Best quality for complex conversations
```

## Error Handling

### Provider Failures

```python
class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass

class RateLimitError(AIProviderError):
    """Rate limit exceeded."""
    pass

class QuotaExceededError(AIProviderError):
    """API quota exceeded."""
    pass

async def handle_provider_error(error: Exception) -> str:
    """Handle different types of provider errors."""
    if "rate limit" in str(error).lower():
        return "Rate limit exceeded. Please try again later."
    elif "quota" in str(error).lower():
        return "API quota exceeded. Please check your account."
    elif "authentication" in str(error).lower():
        return "Authentication failed. Please check API keys."
    else:
        return "AI service temporarily unavailable. Please try again."
```

## Performance Monitoring

### Response Time Tracking

```python
import time
from functools import wraps

def track_performance(func):
    """Decorator to track AI response times."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Log performance metrics
            logger.info(f"AI response time: {response_time:.2f}s")
            
            return result
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"AI error after {response_time:.2f}s: {e}")
            raise
    
    return wrapper
```

## Best Practices

### Model Selection
1. **Use appropriate models** for different use cases
2. **Implement fallback chains** for reliability
3. **Monitor costs** and optimize usage
4. **Cache responses** when appropriate

### Error Handling
1. **Implement retry logic** with exponential backoff
2. **Provide meaningful error messages** to users
3. **Log errors** for debugging and monitoring
4. **Graceful degradation** when services are unavailable

### Security
1. **Validate API keys** and rotate them regularly
2. **Sanitize inputs** before sending to AI providers
3. **Monitor usage** for unusual patterns
4. **Implement rate limiting** to prevent abuse

## Future Enhancements

### Planned Features
- **Multi-modal support** for images and documents
- **Fine-tuning capabilities** for custom models
- **Advanced caching** with semantic similarity
- **Cost prediction** before API calls
- **Model performance analytics** and comparison 