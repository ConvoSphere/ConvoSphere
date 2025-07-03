# Tools Integration

## Overview

The AI Assistant Platform provides a comprehensive tools system that allows assistants to interact with external services, perform calculations, access data, and execute various tasks through a unified interface.

## Tool Architecture

### Base Tool System

The platform implements a flexible tool system that supports both built-in tools and external integrations through the Model Context Protocol (MCP).

```python
# Base tool interface
class BaseTool:
    def __init__(self, name: str, description: str, parameters: Dict):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    async def execute(self, **kwargs) -> Dict:
        """Execute the tool with given parameters."""
        raise NotImplementedError
    
    def get_schema(self) -> Dict:
        """Get tool schema for AI model."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
```

### Tool Registry

```python
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """List all available tools."""
        return [tool.get_schema() for tool in self.tools.values()]
    
    def get_tools_for_assistant(self, assistant_id: str) -> List[Dict]:
        """Get tools available for specific assistant."""
        # Filter tools based on assistant permissions
        return self.list_tools()
```

## Built-in Tools

### File Operations

#### File Reader Tool

```python
class FileReaderTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read content from a file",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path"]
            }
        )
    
    async def execute(self, file_path: str, encoding: str = "utf-8") -> Dict:
        """Read file content."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "file_size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

#### File Writer Tool

```python
class FileWriterTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to file"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Write mode (w: overwrite, a: append)",
                        "default": "w"
                    }
                },
                "required": ["file_path", "content"]
            }
        )
    
    async def execute(self, file_path: str, content: str, mode: str = "w") -> Dict:
        """Write content to file."""
        try:
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode("utf-8"))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

### Web Search Tools

#### Web Search Tool

```python
class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    
    async def execute(self, query: str, num_results: int = 5) -> Dict:
        """Perform web search."""
        try:
            # Use DuckDuckGo or similar search API
            results = await self._search_duckduckgo(query, num_results)
            return {
                "success": True,
                "results": results,
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict]:
        """Search using DuckDuckGo API."""
        # Implementation using duckduckgo-search library
        pass
```

### Calculation Tools

#### Calculator Tool

```python
import math
import re

class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculate",
            description="Perform mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        )
    
    async def execute(self, expression: str) -> Dict:
        """Evaluate mathematical expression."""
        try:
            # Sanitize expression for security
            sanitized_expr = self._sanitize_expression(expression)
            result = eval(sanitized_expr, {"__builtins__": {}}, math.__dict__)
            
            return {
                "success": True,
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sanitize_expression(self, expression: str) -> str:
        """Sanitize mathematical expression."""
        # Remove dangerous characters and functions
        dangerous_patterns = [
            r'__.*__',
            r'import\s+',
            r'exec\s*\(',
            r'eval\s*\(',
            r'open\s*\(',
            r'file\s*\('
        ]
        
        for pattern in dangerous_patterns:
            expression = re.sub(pattern, '', expression, flags=re.IGNORECASE)
        
        return expression
```

### API Tools

#### HTTP Request Tool

```python
import aiohttp

class HTTPRequestTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="http_request",
            description="Make HTTP requests to external APIs",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to make request to"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE)",
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers"
                    },
                    "data": {
                        "type": "object",
                        "description": "Request data (for POST/PUT)"
                    }
                },
                "required": ["url"]
            }
        )
    
    async def execute(self, url: str, method: str = "GET", 
                     headers: Dict = None, data: Dict = None) -> Dict:
        """Make HTTP request."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, json=data
                ) as response:
                    response_data = await response.text()
                    
                    return {
                        "success": True,
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "data": response_data
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

## Model Context Protocol (MCP) Integration

### MCP Server Implementation

The platform integrates with external tools through the Model Context Protocol, allowing seamless communication with various services.

#### MCP Server Setup

```python
# app/tools/example_mcp_server.py
import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
    Tool, TextContent, ImageContent
)

class ExampleMCPServer:
    def __init__(self):
        self.server = Server("example-mcp-server")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        self.server.list_tools(self._handle_list_tools)
        self.server.call_tool(self._handle_call_tool)
    
    async def _handle_list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """Handle list tools request."""
        tools = [
            Tool(
                name="get_weather",
                description="Get weather information for a location",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name"
                        }
                    },
                    "required": ["location"]
                }
            ),
            Tool(
                name="get_stock_price",
                description="Get current stock price",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            )
        ]
        return ListToolsResult(tools=tools)
    
    async def _handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool execution request."""
        if request.name == "get_weather":
            return await self._get_weather(request.arguments)
        elif request.name == "get_stock_price":
            return await self._get_stock_price(request.arguments)
        else:
            raise ValueError(f"Unknown tool: {request.name}")
    
    async def _get_weather(self, arguments: Dict) -> CallToolResult:
        """Get weather information."""
        location = arguments.get("location")
        # Implement weather API call
        weather_data = await self._fetch_weather(location)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Weather in {location}: {weather_data}"
                )
            ]
        )
    
    async def _get_stock_price(self, arguments: Dict) -> CallToolResult:
        """Get stock price."""
        symbol = arguments.get("symbol")
        # Implement stock API call
        price_data = await self._fetch_stock_price(symbol)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Stock price for {symbol}: {price_data}"
                )
            ]
        )

async def main():
    """Run MCP server."""
    server = ExampleMCPServer()
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="example-mcp-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
```

#### MCP Client Integration

```python
# app/tools/mcp_tool.py
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp.types import CallToolRequest

class MCPToolClient:
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.session = None
    
    async def connect(self):
        """Connect to MCP server."""
        self.session = ClientSession(
            stdio_client(self.server_path),
            "mcp-client"
        )
        await self.session.initialize()
    
    async def list_tools(self) -> List[Dict]:
        """List available tools from MCP server."""
        if not self.session:
            await self.connect()
        
        result = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
            for tool in result.tools
        ]
    
    async def call_tool(self, name: str, arguments: Dict) -> Dict:
        """Call tool on MCP server."""
        if not self.session:
            await self.connect()
        
        request = CallToolRequest(name=name, arguments=arguments)
        result = await self.session.call_tool(request)
        
        # Extract text content from result
        text_content = ""
        for content in result.content:
            if hasattr(content, 'text'):
                text_content += content.text
        
        return {
            "success": True,
            "result": text_content
        }
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.session:
            await self.session.close()
```

### Tool Service Integration

```python
# app/services/tool_service.py
from typing import List, Dict, Optional
from app.tools.mcp_tool import MCPToolClient

class ToolService:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.mcp_clients: Dict[str, MCPToolClient] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in tools."""
        self.tool_registry.register_tool(FileReaderTool())
        self.tool_registry.register_tool(FileWriterTool())
        self.tool_registry.register_tool(WebSearchTool())
        self.tool_registry.register_tool(CalculatorTool())
        self.tool_registry.register_tool(HTTPRequestTool())
    
    async def register_mcp_server(self, name: str, server_path: str):
        """Register MCP server."""
        client = MCPToolClient(server_path)
        await client.connect()
        self.mcp_clients[name] = client
        
        # Register tools from MCP server
        tools = await client.list_tools()
        for tool_data in tools:
            mcp_tool = MCPTool(name, tool_data, client)
            self.tool_registry.register_tool(mcp_tool)
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute tool by name."""
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        try:
            result = await tool.execute(**arguments)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_tools(self) -> List[Dict]:
        """Get list of available tools."""
        return self.tool_registry.list_tools()
    
    async def cleanup(self):
        """Cleanup MCP connections."""
        for client in self.mcp_clients.values():
            await client.disconnect()
```

## Tool Management

### Assistant Tool Assignment

```python
# Assistant tool configuration
class AssistantToolConfig:
    def __init__(self, assistant_id: str):
        self.assistant_id = assistant_id
        self.enabled_tools: List[str] = []
        self.tool_permissions: Dict[str, List[str]] = {}
    
    def enable_tool(self, tool_name: str, permissions: List[str] = None):
        """Enable tool for assistant."""
        if tool_name not in self.enabled_tools:
            self.enabled_tools.append(tool_name)
        
        if permissions:
            self.tool_permissions[tool_name] = permissions
    
    def disable_tool(self, tool_name: str):
        """Disable tool for assistant."""
        if tool_name in self.enabled_tools:
            self.enabled_tools.remove(tool_name)
        
        if tool_name in self.tool_permissions:
            del self.tool_permissions[tool_name]
    
    def get_enabled_tools(self) -> List[Dict]:
        """Get enabled tools with schemas."""
        tools = []
        for tool_name in self.enabled_tools:
            tool = tool_registry.get_tool(tool_name)
            if tool:
                tool_schema = tool.get_schema()
                tool_schema["permissions"] = self.tool_permissions.get(tool_name, [])
                tools.append(tool_schema)
        return tools
```

### Tool Usage Tracking

```python
class ToolUsageTracker:
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_tool_usage(
        self,
        assistant_id: str,
        tool_name: str,
        arguments: Dict,
        result: Dict,
        execution_time: float
    ):
        """Log tool usage for analytics."""
        usage_entry = ToolUsage(
            assistant_id=assistant_id,
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            execution_time=execution_time,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(usage_entry)
        await self.db.commit()
    
    async def get_tool_usage_stats(self, assistant_id: str = None) -> Dict:
        """Get tool usage statistics."""
        query = select(ToolUsage)
        if assistant_id:
            query = query.where(ToolUsage.assistant_id == assistant_id)
        
        result = await self.db.execute(query)
        usages = result.scalars().all()
        
        stats = {}
        for usage in usages:
            if usage.tool_name not in stats:
                stats[usage.tool_name] = {
                    "total_uses": 0,
                    "successful_uses": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0
                }
            
            stats[usage.tool_name]["total_uses"] += 1
            stats[usage.tool_name]["total_time"] += usage.execution_time
            
            if usage.result.get("success", False):
                stats[usage.tool_name]["successful_uses"] += 1
        
        # Calculate averages
        for tool_stats in stats.values():
            if tool_stats["total_uses"] > 0:
                tool_stats["avg_time"] = tool_stats["total_time"] / tool_stats["total_uses"]
        
        return stats
```

## Tool Development

### Creating Custom Tools

```python
# Example custom tool
class CustomAPITool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_api",
            description="Custom API integration tool",
            parameters={
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "API endpoint"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method",
                        "default": "GET"
                    },
                    "data": {
                        "type": "object",
                        "description": "Request data"
                    }
                },
                "required": ["endpoint"]
            }
        )
    
    async def execute(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Execute custom API call."""
        try:
            # Implement custom API logic
            result = await self._call_custom_api(endpoint, method, data)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _call_custom_api(self, endpoint: str, method: str, data: Dict) -> Dict:
        """Make custom API call."""
        # Implementation specific to your API
        pass
```

### Tool Testing

```python
import pytest
from app.tools.base import BaseTool

class TestTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="test_tool",
            description="Test tool for unit testing",
            parameters={
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                },
                "required": ["input"]
            }
        )
    
    async def execute(self, input: str) -> Dict:
        return {"success": True, "result": f"Processed: {input}"}

@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution."""
    tool = TestTool()
    result = await tool.execute(input="test input")
    
    assert result["success"] is True
    assert result["result"] == "Processed: test input"

@pytest.mark.asyncio
async def test_tool_schema():
    """Test tool schema generation."""
    tool = TestTool()
    schema = tool.get_schema()
    
    assert schema["name"] == "test_tool"
    assert "input" in schema["parameters"]["properties"]
```

## Best Practices

### Tool Design
1. **Clear naming** - Use descriptive tool names
2. **Comprehensive documentation** - Provide detailed descriptions
3. **Parameter validation** - Validate all inputs
4. **Error handling** - Return meaningful error messages
5. **Security** - Sanitize inputs and outputs

### Performance
1. **Async execution** - Use async/await for I/O operations
2. **Caching** - Cache results when appropriate
3. **Timeouts** - Implement reasonable timeouts
4. **Resource management** - Clean up resources properly

### Security
1. **Input validation** - Validate all parameters
2. **Sandboxing** - Limit tool capabilities
3. **Audit logging** - Log all tool executions
4. **Permission checks** - Verify user permissions

### Integration
1. **Standard interfaces** - Follow consistent patterns
2. **Error handling** - Handle failures gracefully
3. **Monitoring** - Track tool usage and performance
4. **Documentation** - Maintain up-to-date documentation 