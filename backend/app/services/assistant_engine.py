"""
Assistant Engine for the AI Assistant Platform.

This module provides the core orchestration logic for AI assistants,
including context management, tool execution, and response generation.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from loguru import logger

from app.services.ai_service import AIService, AIResponse
from app.services.assistant_service import AssistantService
from app.services.tool_service import ToolService
from app.services.conversation_service import ConversationService
from app.models.assistant import Assistant
from app.tools.mcp_tool import mcp_manager


@dataclass
class ContextWindow:
    """Context window configuration."""
    max_tokens: int = 4000
    max_messages: int = 50
    include_system_prompt: bool = True
    include_knowledge_context: bool = True
    include_tool_results: bool = True


@dataclass
class AssistantContext:
    """Assistant-specific context."""
    assistant_id: str
    system_prompt: str
    personality: Optional[str] = None
    instructions: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    tools_enabled: bool = True
    knowledge_bases: List[str] = None


class ContextManager:
    """Manages conversation context and memory."""
    
    def __init__(self, conversation_service: ConversationService):
        self.conversation_service = conversation_service
        self.context_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        context_window: ContextWindow,
        assistant_context: AssistantContext
    ) -> List[Dict[str, Any]]:
        """
        Get conversation context within specified window.
        
        Args:
            conversation_id: Conversation ID
            context_window: Context window configuration
            assistant_context: Assistant-specific context
            
        Returns:
            List of context messages
        """
        try:
            # Get conversation history
            messages = self.conversation_service.get_conversation_history(
                conversation_id, 
                limit=context_window.max_messages
            )
            
            # Add system prompt if enabled
            context_messages = []
            if context_window.include_system_prompt:
                system_message = self._create_system_message(assistant_context)
                context_messages.append(system_message)
            
            # Add conversation messages
            context_messages.extend(messages)
            
            # Truncate to token limit if needed
            if context_window.max_tokens > 0:
                context_messages = self._truncate_to_token_limit(
                    context_messages, 
                    context_window.max_tokens
                )
            
            return context_messages
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
    def _create_system_message(self, assistant_context: AssistantContext) -> Dict[str, Any]:
        """Create system message from assistant context."""
        system_parts = [assistant_context.system_prompt]
        
        if assistant_context.personality:
            system_parts.append(f"\nPersonality: {assistant_context.personality}")
        
        if assistant_context.instructions:
            system_parts.append(f"\nInstructions: {assistant_context.instructions}")
        
        return {
            "role": "system",
            "content": "\n".join(system_parts)
        }
    
    def _truncate_to_token_limit(
        self, 
        messages: List[Dict[str, Any]], 
        max_tokens: int
    ) -> List[Dict[str, Any]]:
        """Truncate messages to token limit."""
        # Simple token estimation (4 characters per token)
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        estimated_tokens = total_chars // 4
        
        if estimated_tokens <= max_tokens:
            return messages
        
        # Remove oldest messages until under limit
        while messages and estimated_tokens > max_tokens:
            removed_msg = messages.pop(0)
            if removed_msg.get("role") == "system":
                continue  # Keep system message
            
            removed_chars = len(removed_msg.get("content", ""))
            estimated_tokens -= removed_chars // 4
        
        return messages
    
    async def update_context_cache(
        self, 
        conversation_id: str, 
        context: List[Dict[str, Any]]
    ):
        """Update context cache for conversation."""
        self.context_cache[conversation_id] = context
    
    def get_cached_context(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached context for conversation."""
        return self.context_cache.get(conversation_id)


class ToolExecutor:
    """Executes tools and manages tool results."""
    
    def __init__(self, tool_service: ToolService):
        self.tool_service = tool_service
        self.execution_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def execute_tool_call(
        self, 
        tool_call: Dict[str, Any], 
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Execute a tool call.
        
        Args:
            tool_call: Tool call from AI response
            user_id: User ID for execution context
            conversation_id: Conversation ID for tracking
            
        Returns:
            Tool execution result
        """
        try:
            tool_name = tool_call.get("function", {}).get("name")
            arguments = tool_call.get("function", {}).get("arguments", {})
            
            if not tool_name:
                return {"error": "No tool name provided"}
            
            # Try to execute as regular tool first
            try:
                result = await self.tool_service.execute_tool(tool_name, user_id, **arguments)
                execution_result = {
                    "success": True,
                    "result": result,
                    "tool_type": "regular",
                    "tool_name": tool_name,
                    "execution_time": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.warning(f"Regular tool execution failed for {tool_name}: {e}")
                
                # Try to execute as MCP tool
                try:
                    mcp_result = await mcp_manager.execute_tool(tool_name, **arguments)
                    execution_result = {
                        "success": True,
                        "result": mcp_result,
                        "tool_type": "mcp",
                        "tool_name": tool_name,
                        "execution_time": datetime.utcnow().isoformat()
                    }
                except Exception as mcp_e:
                    logger.warning(f"MCP tool execution failed for {tool_name}: {mcp_e}")
                    execution_result = {
                        "success": False,
                        "error": f"Tool {tool_name} not found or execution failed",
                        "tool_name": tool_name,
                        "execution_time": datetime.utcnow().isoformat()
                    }
            
            # Track execution history
            self._track_execution(conversation_id, execution_result)
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing tool call: {e}")
            return {"error": str(e)}
    
    def _track_execution(self, conversation_id: str, execution_result: Dict[str, Any]):
        """Track tool execution history."""
        if conversation_id not in self.execution_history:
            self.execution_history[conversation_id] = []
        
        self.execution_history[conversation_id].append(execution_result)
    
    def get_execution_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get tool execution history for conversation."""
        return self.execution_history.get(conversation_id, [])
    
    async def prepare_tools_for_assistant(
        self, 
        assistant_id: str, 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Prepare tools for assistant.
        
        Args:
            assistant_id: Assistant ID
            user_id: User ID
            
        Returns:
            List of tool definitions
        """
        try:
            # Get assistant tools
            assistant_tools = self.tool_service.get_tools_for_assistant(assistant_id)
            
            # Get MCP tools
            mcp_tools = mcp_manager.get_all_tools()
            
            # Combine tools
            combined_tools = []
            
            # Add assistant tools
            for tool in assistant_tools:
                if tool.get("status") == "active":
                    tool_def = {
                        "type": "function",
                        "function": {
                            "name": tool.get("name"),
                            "description": tool.get("description", ""),
                            "parameters": tool.get("parameters", {})
                        }
                    }
                    combined_tools.append(tool_def)
            
            # Add MCP tools
            for tool in mcp_tools:
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": tool.get("name"),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("input_schema", {})
                    }
                }
                combined_tools.append(tool_def)
            
            return combined_tools
            
        except Exception as e:
            logger.error(f"Error preparing tools for assistant: {e}")
            return []


class AssistantEngine:
    """Main assistant engine for orchestrating AI interactions."""
    
    def __init__(
        self,
        ai_service: AIService,
        assistant_service: AssistantService,
        conversation_service: ConversationService,
        tool_service: ToolService
    ):
        self.ai_service = ai_service
        self.assistant_service = assistant_service
        self.conversation_service = conversation_service
        self.tool_service = tool_service
        
        # Initialize components
        self.context_manager = ContextManager(conversation_service)
        self.tool_executor = ToolExecutor(tool_service)
    
    async def process_message(
        self,
        message: str,
        conversation_id: str,
        assistant_id: str,
        user_id: str,
        context_window: Optional[ContextWindow] = None,
        use_rag: bool = True,
        use_tools: bool = True
    ) -> AIResponse:
        """
        Process user message and generate AI response.
        
        Args:
            message: User message
            conversation_id: Conversation ID
            assistant_id: Assistant ID
            user_id: User ID
            context_window: Context window configuration
            use_rag: Whether to use RAG
            use_tools: Whether to enable tools
            
        Returns:
            AIResponse: Generated response
        """
        try:
            # Get assistant context
            assistant = self.assistant_service.get_assistant(assistant_id)
            if not assistant:
                return AIResponse(
                    content="Assistant not found.",
                    message_type="text",
                    metadata={"error": "assistant_not_found"}
                )
            
            # Create assistant context
            assistant_context = AssistantContext(
                assistant_id=str(assistant.id),
                system_prompt=assistant.system_prompt,
                personality=assistant.personality,
                instructions=assistant.instructions,
                model=assistant.model,
                temperature=float(assistant.temperature),
                max_tokens=int(assistant.max_tokens),
                tools_enabled=assistant.tools_enabled
            )
            
            # Set default context window if not provided
            if not context_window:
                context_window = ContextWindow(
                    max_tokens=assistant_context.max_tokens,
                    max_messages=50,
                    include_system_prompt=True,
                    include_knowledge_context=use_rag,
                    include_tool_results=True
                )
            
            # Get conversation context
            context_messages = await self.context_manager.get_conversation_context(
                conversation_id, 
                context_window, 
                assistant_context
            )
            
            # Add user message
            context_messages.append({
                "role": "user",
                "content": message
            })
            
            # Prepare tools if enabled
            tools = None
            if use_tools and assistant_context.tools_enabled:
                tools = await self.tool_executor.prepare_tools_for_assistant(
                    assistant_id, 
                    user_id
                )
            
            # Generate AI response
            if use_rag:
                response = await self.ai_service.chat_completion_with_rag(
                    messages=context_messages,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    model=assistant_context.model,
                    temperature=assistant_context.temperature,
                    max_tokens=assistant_context.max_tokens,
                    use_knowledge_base=True,
                    use_tools=use_tools,
                    max_context_chunks=5
                )
            else:
                response = await self.ai_service.chat_completion(
                    messages=context_messages,
                    model=assistant_context.model,
                    temperature=assistant_context.temperature,
                    max_tokens=assistant_context.max_tokens,
                    tools=tools,
                    user_id=user_id,
                    conversation_id=conversation_id
                )
            
            # Process response and handle tool calls
            return await self._process_ai_response(
                response, 
                user_id, 
                conversation_id,
                assistant_context
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return AIResponse(
                content=f"Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Anfrage: {str(e)}",
                message_type="text",
                metadata={"error": str(e)}
            )
    
    async def _process_ai_response(
        self,
        response: Dict[str, Any],
        user_id: str,
        conversation_id: str,
        assistant_context: AssistantContext
    ) -> AIResponse:
        """Process AI response and handle tool calls."""
        content = ""
        tool_calls = []
        tool_results = []
        
        if "choices" in response and response["choices"]:
            choice = response["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            # Check for tool calls
            if "tool_calls" in message:
                tool_calls = message["tool_calls"]
                
                # Execute tool calls
                for tool_call in tool_calls:
                    tool_result = await self.tool_executor.execute_tool_call(
                        tool_call, 
                        user_id, 
                        conversation_id
                    )
                    tool_results.append(tool_result)
                    
                    # Add tool result to content
                    if tool_result.get("success"):
                        content += f"\n\nTool-Ausführung ({tool_result.get('tool_type', 'unknown')}):\n"
                        content += str(tool_result.get("result", ""))
                    else:
                        content += f"\n\nTool-Fehler: {tool_result.get('error', 'Unknown error')}"
        
        # Prepare metadata
        metadata = {
            "model_used": response.get("model", "unknown"),
            "tokens_used": response.get("usage", {}).get("total_tokens", 0),
            "has_tool_calls": len(tool_calls) > 0,
            "tool_calls_count": len(tool_calls),
            "assistant_id": assistant_context.assistant_id,
            "tool_results": tool_results
        }
        
        return AIResponse(
            content=content,
            message_type="text",
            metadata=metadata,
            tool_calls=tool_calls if tool_calls else None
        )
    
    async def get_assistant_context(self, assistant_id: str) -> Optional[AssistantContext]:
        """Get assistant context."""
        assistant = self.assistant_service.get_assistant(assistant_id)
        if not assistant:
            return None
        
        return AssistantContext(
            assistant_id=str(assistant.id),
            system_prompt=assistant.system_prompt,
            personality=assistant.personality,
            instructions=assistant.instructions,
            model=assistant.model,
            temperature=float(assistant.temperature),
            max_tokens=int(assistant.max_tokens),
            tools_enabled=assistant.tools_enabled
        )
    
    def get_context_manager(self) -> ContextManager:
        """Get context manager."""
        return self.context_manager
    
    def get_tool_executor(self) -> ToolExecutor:
        """Get tool executor."""
        return self.tool_executor 