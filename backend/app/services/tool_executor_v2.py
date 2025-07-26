"""
Enhanced Tool Executor with Pydantic validation and caching.

This module provides a comprehensive tool execution framework with
validation, caching, monitoring, and dependency management.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from backend.app.core.exceptions import ToolError
from backend.app.services.tool_service import tool_service
from backend.app.tools.mcp_tool import mcp_manager
from loguru import logger
from pydantic import BaseModel, Field


class ToolExecutionRequest(BaseModel):
    """Request for tool execution with validation."""

    tool_name: str = Field(..., min_length=1, max_length=200, description="Tool name")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments",
    )
    user_id: str = Field(..., description="User ID")
    conversation_id: str = Field(..., description="Conversation ID")
    priority: int = Field(default=1, ge=1, le=10, description="Execution priority")
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Timeout in seconds",
    )
    cache_result: bool = Field(default=True, description="Whether to cache the result")
    retry_count: int = Field(default=0, ge=0, le=3, description="Retry count")

    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate tool name."""
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class ToolExecutionResult(BaseModel):
    """Result of tool execution with metadata."""

    execution_id: str = Field(..., description="Unique execution ID")
    tool_name: str = Field(..., description="Tool name")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Input arguments",
    )
    result: Any = Field(None, description="Execution result")
    error: str | None = Field(None, description="Error message")
    status: str = Field(
        default="pending",
        pattern="^(pending|running|completed|failed|cancelled)$",
        description="Execution status",
    )
    start_time: datetime | None = Field(None, description="Start time")
    end_time: datetime | None = Field(None, description="End time")
    execution_time: float | None = Field(
        None,
        ge=0,
        description="Execution time in seconds",
    )
    tokens_used: int | None = Field(None, ge=0, description="Tokens used")
    cache_hit: bool = Field(default=False, description="Whether result was from cache")
    user_id: str = Field(..., description="User ID")
    conversation_id: str = Field(..., description="Conversation ID")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class ToolCache:
    """Cache for tool execution results."""

    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.cache: dict[str, dict[str, Any]] = {}
        self.access_times: dict[str, datetime] = {}

    def _generate_cache_key(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Generate cache key for tool execution."""
        # Create a deterministic key from tool name and arguments
        args_str = json.dumps(arguments, sort_keys=True)
        return f"{tool_name}:{hash(args_str)}"

    def get(self, tool_name: str, arguments: dict[str, Any]) -> Any | None:
        """Get cached result if available and not expired."""
        cache_key = self._generate_cache_key(tool_name, arguments)

        if cache_key not in self.cache:
            return None

        cached_data = self.cache[cache_key]
        cached_time = cached_data.get("cached_at")

        # Check if cache is expired
        if cached_time and datetime.now() - cached_time > timedelta(
            hours=self.ttl_hours,
        ):
            del self.cache[cache_key]
            del self.access_times[cache_key]
            return None

        # Update access time for LRU
        self.access_times[cache_key] = datetime.now()
        return cached_data.get("result")

    def set(self, tool_name: str, arguments: dict[str, Any], result: Any) -> None:
        """Cache tool execution result."""
        cache_key = self._generate_cache_key(tool_name, arguments)

        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[cache_key] = {
            "result": result,
            "cached_at": datetime.now(),
            "tool_name": tool_name,
            "arguments": arguments,
        }
        self.access_times[cache_key] = datetime.now()

    def _evict_lru(self) -> None:
        """Evict least recently used cache entry."""
        if not self.access_times:
            return

        # Find least recently used entry
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]

    def clear(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.access_times.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_hours": self.ttl_hours,
            "hit_rate": self._calculate_hit_rate(),
        }

    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)."""
        # This would need to be implemented with actual hit/miss tracking
        return 0.0


class ToolDependencyManager:
    """Manage tool dependencies and execution order."""

    def __init__(self):
        self.dependencies: dict[str, list[str]] = {}
        self.execution_order: list[str] = []

    def add_dependency(self, tool_name: str, depends_on: list[str]) -> None:
        """Add dependencies for a tool."""
        self.dependencies[tool_name] = depends_on

    def get_execution_order(self, tools: list[str]) -> list[str]:
        """Get optimal execution order for tools."""
        # Simple topological sort for dependencies
        visited = set()
        temp_visited = set()
        order = []

        def visit(tool: str) -> None:
            if tool in temp_visited:
                raise ValueError(f"Circular dependency detected for tool: {tool}")
            if tool in visited:
                return

            temp_visited.add(tool)

            # Visit dependencies first
            for dep in self.dependencies.get(tool, []):
                if dep in tools:  # Only visit if dependency is in our tool list
                    visit(dep)

            temp_visited.remove(tool)
            visited.add(tool)
            order.append(tool)

        for tool in tools:
            if tool not in visited:
                visit(tool)

        return order

    def validate_dependencies(self, tools: list[str]) -> bool:
        """Validate that all dependencies are available."""
        for tool in tools:
            deps = self.dependencies.get(tool, [])
            for dep in deps:
                if dep not in tools:
                    logger.warning(
                        f"Tool {tool} depends on {dep} which is not available",
                    )
                    return False
        return True


class EnhancedToolExecutor:
    """Enhanced tool executor with validation, caching, and monitoring."""

    def __init__(self):
        self.cache = ToolCache()
        self.dependency_manager = ToolDependencyManager()
        self.execution_history: list[ToolExecutionResult] = []
        self.active_executions: dict[str, asyncio.Task] = {}
        self.max_concurrent_executions = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrent_executions)

        # Initialize dependencies for common tools
        self._initialize_dependencies()

    def _initialize_dependencies(self) -> None:
        """Initialize common tool dependencies."""
        # Example dependencies
        self.dependency_manager.add_dependency("web_search", [])
        self.dependency_manager.add_dependency("file_reader", [])
        self.dependency_manager.add_dependency("data_analyzer", ["file_reader"])
        self.dependency_manager.add_dependency(
            "report_generator",
            ["data_analyzer", "web_search"],
        )

    async def execute_tool(
        self,
        request: ToolExecutionRequest,
    ) -> ToolExecutionResult:
        """
        Execute a tool with validation, caching, and monitoring.

        Args:
            request: Tool execution request with validation

        Returns:
            ToolExecutionResult: Execution result with metadata

        Raises:
            ToolError: If tool execution fails
            ValidationError: If request validation fails
        """
        execution_id = str(uuid4())

        # Create execution result
        result = ToolExecutionResult(
            execution_id=execution_id,
            tool_name=request.tool_name,
            arguments=request.arguments,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            status="pending",
        )

        try:
            # Check cache first
            if request.cache_result:
                cached_result = self.cache.get(request.tool_name, request.arguments)
                if cached_result is not None:
                    result.result = cached_result
                    result.status = "completed"
                    result.cache_hit = True
                    result.end_time = datetime.now()
                    result.execution_time = 0.0
                    logger.info(f"Cache hit for tool {request.tool_name}")
                    return result

            # Execute tool with semaphore for concurrency control
            async with self.semaphore:
                return await self._execute_tool_internal(request, result)

        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            result.end_time = datetime.now()
            if result.start_time:
                result.execution_time = (
                    result.end_time - result.start_time
                ).total_seconds()

            logger.error(f"Tool execution failed: {e}")
            raise ToolError(
                f"Tool execution failed: {str(e)}",
                request.tool_name,
                request.arguments,
            )

        finally:
            # Store execution history
            self.execution_history.append(result)
            if len(self.execution_history) > 1000:  # Keep last 1000 executions
                self.execution_history = self.execution_history[-1000:]

    async def _execute_tool_internal(
        self,
        request: ToolExecutionRequest,
        result: ToolExecutionResult,
    ) -> ToolExecutionResult:
        """Internal tool execution with timeout and retry logic."""
        result.status = "running"
        result.start_time = datetime.now()

        # Try to execute tool with retries
        last_error = None
        for attempt in range(request.retry_count + 1):
            try:
                # Execute with timeout
                tool_result = await asyncio.wait_for(
                    self._execute_single_tool(request),
                    timeout=request.timeout,
                )

                result.result = tool_result
                result.status = "completed"
                result.end_time = datetime.now()
                result.execution_time = (
                    result.end_time - result.start_time
                ).total_seconds()

                # Cache result if requested
                if request.cache_result:
                    self.cache.set(request.tool_name, request.arguments, tool_result)

                logger.info(
                    f"Tool {request.tool_name} executed successfully in {result.execution_time:.2f}s",
                )
                return result

            except TimeoutError:
                last_error = f"Tool execution timed out after {request.timeout}s"
                logger.warning(
                    f"Tool {request.tool_name} timed out on attempt {attempt + 1}",
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Tool {request.tool_name} failed on attempt {attempt + 1}: {e}",
                )

                if attempt < request.retry_count:
                    await asyncio.sleep(2**attempt)  # Exponential backoff

        # All attempts failed
        result.status = "failed"
        result.error = last_error
        result.end_time = datetime.now()
        result.execution_time = (result.end_time - result.start_time).total_seconds()

        raise ToolError(
            f"Tool execution failed after {request.retry_count + 1} attempts: {last_error}",
        )

    async def _execute_single_tool(self, request: ToolExecutionRequest) -> Any:
        """Execute a single tool (regular or MCP)."""
        tool_name = request.tool_name
        arguments = request.arguments

        # Try regular tool first
        try:
            return await tool_service.execute_tool(
                tool_name,
                request.user_id,
                **arguments,
            )
        except Exception as e:
            logger.debug(f"Regular tool {tool_name} failed: {e}")

        # Try MCP tool
        try:
            return await mcp_manager.execute_tool(tool_name, **arguments)
        except Exception as e:
            logger.debug(f"MCP tool {tool_name} failed: {e}")

        # Both failed
        raise ToolError(f"Tool {tool_name} not found or execution failed")

    async def execute_tools_batch(
        self,
        requests: list[ToolExecutionRequest],
    ) -> list[ToolExecutionResult]:
        """
        Execute multiple tools with dependency management.

        Args:
            requests: List of tool execution requests

        Returns:
            List[ToolExecutionResult]: Execution results
        """
        tool_names = [req.tool_name for req in requests]

        # Get optimal execution order
        execution_order = self.dependency_manager.get_execution_order(tool_names)

        # Group requests by execution order
        ordered_requests = []
        for tool_name in execution_order:
            for req in requests:
                if req.tool_name == tool_name:
                    ordered_requests.append(req)
                    break

        # Execute tools in order
        results = []
        for request in ordered_requests:
            try:
                result = await self.execute_tool(request)
                results.append(result)
            except Exception as e:
                # Create failed result
                failed_result = ToolExecutionResult(
                    execution_id=str(uuid4()),
                    tool_name=request.tool_name,
                    arguments=request.arguments,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    status="failed",
                    error=str(e),
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                )
                results.append(failed_result)

        return results

    def get_available_tools(self) -> list[dict[str, Any]]:
        """Get list of available tools with metadata."""
        tools = []

        # Get regular tools
        if tool_service is not None:
            try:
                regular_tools = tool_service.get_available_tools()
                for tool in regular_tools:
                    tools.append(
                        {
                            "name": tool.get("name"),
                            "description": tool.get("description", ""),
                            "category": tool.get("category", "general"),
                            "type": "regular",
                            "dependencies": self.dependency_manager.dependencies.get(
                                tool.get("name"),
                                [],
                            ),
                        },
                    )
            except Exception as e:
                logger.warning(f"Error getting regular tools: {e}")
        else:
            # Return empty list for tests when tool_service is not initialized
            logger.debug("tool_service not initialized, returning empty tool list")

        # Get MCP tools
        try:
            mcp_tools = mcp_manager.get_all_tools()
            for tool in mcp_tools:
                tools.append(
                    {
                        "name": tool.get("name"),
                        "description": tool.get("description", ""),
                        "category": tool.get("category", "mcp"),
                        "type": "mcp",
                        "dependencies": self.dependency_manager.dependencies.get(
                            tool.get("name"),
                            [],
                        ),
                    },
                )
        except Exception as e:
            logger.warning(f"Error getting MCP tools: {e}")

        return tools

    def get_execution_stats(self) -> dict[str, Any]:
        """Get tool execution statistics."""
        total_executions = len(self.execution_history)
        successful_executions = len(
            [r for r in self.execution_history if r.status == "completed"],
        )
        failed_executions = len(
            [r for r in self.execution_history if r.status == "failed"],
        )

        avg_execution_time = 0.0
        if successful_executions > 0:
            execution_times = [
                r.execution_time for r in self.execution_history if r.execution_time
            ]
            if execution_times:
                avg_execution_time = sum(execution_times) / len(execution_times)

        cache_stats = self.cache.get_stats()

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": (
                (successful_executions / total_executions * 100)
                if total_executions > 0
                else 0
            ),
            "average_execution_time": avg_execution_time,
            "cache_stats": cache_stats,
            "active_executions": len(self.active_executions),
            "max_concurrent_executions": self.max_concurrent_executions,
        }

    def clear_cache(self) -> None:
        """Clear tool execution cache."""
        self.cache.clear()
        logger.info("Tool execution cache cleared")

    def get_recent_executions(
        self,
        limit: int = 50,
        tool_name: str | None = None,
        user_id: str | None = None,
    ) -> list[ToolExecutionResult]:
        """Get recent tool executions with optional filtering."""
        executions = self.execution_history.copy()

        if tool_name:
            executions = [e for e in executions if e.tool_name == tool_name]

        if user_id:
            executions = [e for e in executions if e.user_id == user_id]

        # Sort by start time (most recent first)
        executions.sort(key=lambda x: x.start_time or datetime.min, reverse=True)

        return executions[:limit]


# Global enhanced tool executor instance
enhanced_tool_executor = EnhancedToolExecutor()

# Alias for backward compatibility
tool_executor = enhanced_tool_executor
