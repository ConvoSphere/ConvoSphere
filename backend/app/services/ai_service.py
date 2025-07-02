"""
AI service for LiteLLM integration and AI model management.

This module provides AI model integration using LiteLLM for generating
assistant responses and managing different AI providers.
"""

from typing import List, Dict, Any, Optional
from litellm import completion, acompletion
from loguru import logger

from app.core.config import settings
from app.services.weaviate_service import weaviate_service


class AIService:
    """Service for AI model interactions using LiteLLM."""
    
    def __init__(self):
        self.default_model = settings.litellm_model
        self.default_max_tokens = settings.litellm_max_tokens
        self.default_temperature = settings.litellm_temperature
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate AI response using LiteLLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: AI model to use (defaults to configured model)
            temperature: Model temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for LiteLLM
            
        Returns:
            Dict[str, Any]: AI response with content and metadata
        """
        try:
            # Use defaults if not provided
            model = model or self.default_model
            temperature = temperature or self.default_temperature
            max_tokens = max_tokens or self.default_max_tokens
            
            # Prepare completion parameters
            completion_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Generate response
            response = await acompletion(**completion_params)
            
            # Extract response data
            result = {
                "content": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
                "metadata": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            }
            
            logger.info(f"AI response generated using model {model}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            raise
    
    def generate_response_sync(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate AI response synchronously.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: AI model to use (defaults to configured model)
            temperature: Model temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for LiteLLM
            
        Returns:
            Dict[str, Any]: AI response with content and metadata
        """
        try:
            # Use defaults if not provided
            model = model or self.default_model
            temperature = temperature or self.default_temperature
            max_tokens = max_tokens or self.default_max_tokens
            
            # Prepare completion parameters
            completion_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Generate response
            response = completion(**completion_params)
            
            # Extract response data
            result = {
                "content": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
                "metadata": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            }
            
            logger.info(f"AI response generated using model {model}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            raise
    
    async def generate_assistant_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        assistant_config: Optional[Dict[str, Any]] = None,
        rag_enabled: bool = True,
        rag_limit: int = 3
    ) -> Dict[str, Any]:
        """
        Generate assistant response with context and configuration.
        Optionally use RAG (Retrieval-Augmented Generation) with Weaviate.
        """
        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # RAG: Fetch relevant knowledge and add to context
        rag_context = ""
        rag_metadata = None
        if rag_enabled:
            knowledge_results = weaviate_service.semantic_search_knowledge(user_message, limit=rag_limit)
            if knowledge_results:
                rag_context = "\n\n".join([k["content"] for k in knowledge_results if "content" in k])
                rag_metadata = knowledge_results
                if rag_context:
                    # Add as system message for context
                    messages.insert(1, {"role": "system", "content": f"Relevant knowledge:\n{rag_context}"})
        
        # Extract assistant configuration
        model = assistant_config.get("model") if assistant_config else None
        temperature = assistant_config.get("temperature") if assistant_config else None
        max_tokens = assistant_config.get("max_tokens") if assistant_config else None
        
        # Generate response
        result = await self.generate_response(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Attach RAG metadata if used
        if rag_context:
            result["rag_context"] = rag_context
            result["rag_metadata"] = rag_metadata
        
        return result
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available AI models.
        
        Returns:
            List[Dict[str, Any]]: List of available models with metadata
        """
        # This would typically query LiteLLM's model list
        # For now, return a static list of common models
        return [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "openai",
                "max_tokens": 8192,
                "supports_functions": True,
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "openai",
                "max_tokens": 4096,
                "supports_functions": True,
            },
            {
                "id": "claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "anthropic",
                "max_tokens": 200000,
                "supports_functions": True,
            },
            {
                "id": "claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "provider": "anthropic",
                "max_tokens": 200000,
                "supports_functions": True,
            },
            {
                "id": "gemini-pro",
                "name": "Gemini Pro",
                "provider": "google",
                "max_tokens": 32768,
                "supports_functions": False,
            },
        ]
    
    def validate_model(self, model: str) -> bool:
        """
        Validate if a model is available.
        
        Args:
            model: Model ID to validate
            
        Returns:
            bool: True if model is available
        """
        available_models = [m["id"] for m in self.get_available_models()]
        return model in available_models 