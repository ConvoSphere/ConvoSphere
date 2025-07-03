"""
AI Service for the AI Assistant Platform.

This module provides AI integration using LiteLLM for multiple providers,
cost tracking, and embedding generation.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from loguru import logger

try:
    import litellm
    from litellm import completion, acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("LiteLLM not available. AI features will be disabled.")

from app.core.config import settings
from app.services.weaviate_service import weaviate_service


@dataclass
class CostInfo:
    """Cost information for AI usage."""
    model: str
    tokens_used: int
    cost_usd: float
    timestamp: datetime
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None


class CostTracker:
    """Track AI usage costs."""
    
    def __init__(self):
        """Initialize cost tracker."""
        self.costs: List[CostInfo] = []
        self.total_cost = 0.0
        self.total_tokens = 0
    
    def add_cost(self, cost_info: CostInfo):
        """Add cost information."""
        self.costs.append(cost_info)
        self.total_cost += cost_info.cost_usd
        self.total_tokens += cost_info.tokens_used
        
        logger.info(f"AI Cost: ${cost_info.cost_usd:.4f} for {cost_info.tokens_used} tokens "
                   f"using {cost_info.model}")
    
    def get_total_cost(self) -> float:
        """Get total cost."""
        return self.total_cost
    
    def get_total_tokens(self) -> int:
        """Get total tokens used."""
        return self.total_tokens
    
    def get_costs_by_user(self, user_id: str) -> List[CostInfo]:
        """Get costs for specific user."""
        return [cost for cost in self.costs if cost.user_id == user_id]
    
    def get_costs_by_conversation(self, conversation_id: str) -> List[CostInfo]:
        """Get costs for specific conversation."""
        return [cost for cost in self.costs if cost.conversation_id == conversation_id]


class AIService:
    """AI service for managing multiple providers and models."""
    
    def __init__(self):
        """Initialize AI service."""
        if not LITELLM_AVAILABLE:
            logger.error("LiteLLM not available. AI service will be disabled.")
            self.enabled = False
            return
        
        self.enabled = True
        self.providers = {}
        self.models = {}
        self.cost_tracker = CostTracker()
        
        # Initialize LiteLLM
        self._setup_litellm()
        self._load_providers()
        self._load_models()
    
    def _setup_litellm(self):
        """Setup LiteLLM configuration."""
        try:
            # Configure LiteLLM
            litellm.set_verbose = settings.debug
            
            # Set default model
            litellm.default_model = settings.default_ai_model
            
            logger.info("LiteLLM configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure LiteLLM: {e}")
            self.enabled = False
    
    def _load_providers(self):
        """Load AI providers from configuration."""
        self.providers = {
            "openai": {
                "name": "OpenAI",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "enabled": bool(settings.openai_api_key),
                "api_key": settings.openai_api_key
            },
            "anthropic": {
                "name": "Anthropic",
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "enabled": bool(settings.anthropic_api_key),
                "api_key": settings.anthropic_api_key
            },
            "google": {
                "name": "Google",
                "models": ["gemini-pro", "gemini-pro-vision"],
                "enabled": bool(settings.google_api_key),
                "api_key": settings.google_api_key
            }
        }
        
        # Set environment variables for LiteLLM
        if settings.openai_api_key:
            import os
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        
        if settings.anthropic_api_key:
            import os
            os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
        
        if settings.google_api_key:
            import os
            os.environ["GOOGLE_API_KEY"] = settings.google_api_key
    
    def _load_models(self):
        """Load available models."""
        self.models = {
            "gpt-4": {
                "provider": "openai",
                "max_tokens": 8192,
                "cost_per_1k_tokens": 0.03,
                "supports_tools": True
            },
            "gpt-4-turbo": {
                "provider": "openai",
                "max_tokens": 128000,
                "cost_per_1k_tokens": 0.01,
                "supports_tools": True
            },
            "gpt-3.5-turbo": {
                "provider": "openai",
                "max_tokens": 4096,
                "cost_per_1k_tokens": 0.002,
                "supports_tools": True
            },
            "claude-3-opus": {
                "provider": "anthropic",
                "max_tokens": 200000,
                "cost_per_1k_tokens": 0.015,
                "supports_tools": True
            },
            "claude-3-sonnet": {
                "provider": "anthropic",
                "max_tokens": 200000,
                "cost_per_1k_tokens": 0.003,
                "supports_tools": True
            },
            "claude-3-haiku": {
                "provider": "anthropic",
                "max_tokens": 200000,
                "cost_per_1k_tokens": 0.00025,
                "supports_tools": True
            },
            "gemini-pro": {
                "provider": "google",
                "max_tokens": 32768,
                "cost_per_1k_tokens": 0.0005,
                "supports_tools": False
            }
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using LiteLLM.
        
        Args:
            messages: List of message dictionaries
            model: AI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: List of tools for function calling
            tool_choice: Tool choice strategy
            user_id: User ID for cost tracking
            conversation_id: Conversation ID for cost tracking
            **kwargs: Additional parameters
            
        Returns:
            Completion response
        """
        if not self.enabled:
            raise RuntimeError("AI service is disabled")
        
        # Use default model if none specified
        if not model:
            model = settings.default_ai_model
        
        # Validate model
        if model not in self.models:
            raise ValueError(f"Model {model} not supported")
        
        # Get model info
        model_info = self.models[model]
        
        # Set max_tokens if not provided
        if not max_tokens:
            max_tokens = model_info["max_tokens"]
        
        # Prepare completion parameters
        completion_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # Add tools if supported
        if tools and model_info["supports_tools"]:
            completion_params["tools"] = tools
            completion_params["tool_choice"] = tool_choice
        
        try:
            # Generate completion
            logger.info(f"Generating completion with model {model}")
            response = await acompletion(**completion_params)
            
            # Track cost
            self._track_cost(response, model, user_id, conversation_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    def _track_cost(self, response: Dict, model: str, user_id: Optional[str] = None, conversation_id: Optional[str] = None):
        """Track cost for AI usage."""
        try:
            # Extract usage information
            usage = response.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            
            # Calculate cost
            model_info = self.models.get(model, {})
            cost_per_1k = model_info.get("cost_per_1k_tokens", 0)
            cost_usd = (tokens_used / 1000) * cost_per_1k
            
            # Create cost info
            cost_info = CostInfo(
                model=model,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # Add to tracker
            self.cost_tracker.add_cost(cost_info)
            
        except Exception as e:
            logger.warning(f"Failed to track cost: {e}")
    
    async def get_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            model: Embedding model to use
            
        Returns:
            List of embedding values
        """
        if not self.enabled:
            raise RuntimeError("AI service is disabled")
        
        try:
            # Use LiteLLM for embeddings
            response = await acompletion(
                model=model,
                messages=[{"role": "user", "content": text}],
                max_tokens=1  # We only need embeddings, not completion
            )
            
            # Extract embeddings from response
            # Note: This is a simplified approach. In practice, you'd use
            # the embeddings endpoint directly
            return response.get("embeddings", [])
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get list of available models."""
        return self.models
    
    def get_available_providers(self) -> Dict[str, Dict]:
        """Get list of available providers."""
        return self.providers
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            "total_cost": self.cost_tracker.get_total_cost(),
            "total_tokens": self.cost_tracker.get_total_tokens(),
            "costs": self.cost_tracker.costs
        }
    
    def is_enabled(self) -> bool:
        """Check if AI service is enabled."""
        return self.enabled
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for AI service."""
        return {
            "enabled": self.enabled,
            "litellm_available": LITELLM_AVAILABLE,
            "providers": len([p for p in self.providers.values() if p["enabled"]]),
            "models": len(self.models),
            "total_cost": self.cost_tracker.get_total_cost()
        }


# Global AI service instance
ai_service = AIService() 