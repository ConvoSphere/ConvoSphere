# MCP (Model Context Protocol) Integration

## Overview

The AI Assistant Platform now supports MCP (Model Context Protocol) integration, allowing you to connect to external MCP servers and use their tools within the platform. This enables powerful extensibility and integration with a wide range of external services and tools.

## What is MCP?

The Model Context Protocol is a standardized protocol that allows AI applications to connect to external tools and services using a common interface. It enables:

- **Standardized Tool Integration**: Connect to any MCP-compliant server
- **Extensibility**: Add new capabilities without modifying the core platform
- **Interoperability**: Use tools from different providers seamlessly
- **Resource Access**: Access external resources and data sources

## Features

### MCP Server Management
- **Add/Remove Servers**: Connect to and disconnect from MCP servers
- **Server Status**: Monitor connection status and health
- **Server Information**: View server details, tool counts, and resource counts

### MCP Tool Integration
- **Automatic Discovery**: Tools are automatically discovered from connected servers
- **Schema Conversion**: MCP JSON schemas are converted to platform tool parameters
- **Tool Execution**: Execute MCP tools directly from the platform
- **Result Handling**: Process and display tool execution results

### Resource Management
- **Resource Discovery**: List available resources from MCP servers
- **Resource Reading**: Access and read external resources
- **Content Display**: View resource content in various formats

## Usage

### Adding an MCP Server

1. Navigate to the **MCP Tools** page in the platform
2. Click **"Add Server"** button
3. Enter the server details:
   - **Server ID**: Unique identifier for the server
   - **Server URL**: HTTP endpoint of the MCP server
   - **Server Name**: Optional display name
4. Click **"Add Server"** to connect

### Using MCP Tools

1. **View Available Tools**: All tools from connected servers are listed automatically
2. **Execute Tools**: Click **"Execute"** on any tool to run it
3. **Provide Parameters**: Enter required parameters in the execution dialog
4. **View Results**: Tool execution results are displayed in a dialog

### Managing Resources

1. **List Resources**: View available resources from each server
2. **Read Resources**: Access resource content directly
3. **Resource Types**: Support for various MIME types (JSON, Markdown, etc.)

## Example MCP Server

The platform includes an example MCP server for testing:

### Starting the Example Server

```bash
# From the project root
python scripts/start_mcp_server.py
```

The example server provides these tools:

- **get_weather**: Get weather information for a location
- **calculate**: Perform mathematical calculations
- **translate_text**: Translate text between languages
- **get_time**: Get current time for a timezone

### Example Server Endpoints

- **MCP Protocol**: `http://localhost:8080/`
- **Health Check**: `http://localhost:8080/health`

## API Endpoints

### MCP Server Management

```
POST /api/v1/mcp/servers          # Add MCP server
GET  /api/v1/mcp/servers          # List MCP servers
DELETE /api/v1/mcp/servers/{id}   # Remove MCP server
```

### MCP Tools

```
GET  /api/v1/mcp/tools            # List MCP tools
GET  /api/v1/mcp/tools/{id}       # Get MCP tool details
POST /api/v1/mcp/tools/{id}/execute # Execute MCP tool
```

### MCP Resources

```
GET  /api/v1/mcp/servers/{id}/resources           # List server resources
POST /api/v1/mcp/servers/{id}/resources/{uri}/read # Read resource
```

## Configuration

### Backend Configuration

The MCP integration is configured in the backend:

```python
# Global MCP server manager
from app.tools.mcp_tool import mcp_manager

# Add server
await mcp_manager.add_server("example", "http://localhost:8080", "Example Server")

# Get tools
tools = mcp_manager.get_all_tools()

# Execute tool
result = await mcp_manager.execute_tool("example_get_weather", {"location": "Berlin"})
```

### Frontend Configuration

The frontend provides a user interface for MCP management:

```python
# MCP Tools page
from pages.mcp_tools import MCPToolsPage

# API client methods
await api_client.get_mcp_servers()
await api_client.add_mcp_server(server_data)
await api_client.execute_mcp_tool(tool_id, arguments)
```

## Security Considerations

### Authentication
- MCP server connections are managed per user session
- Server credentials should be stored securely
- Consider implementing server authentication

### Tool Execution
- Validate tool parameters before execution
- Implement rate limiting for tool calls
- Monitor tool execution for security issues

### Resource Access
- Validate resource URIs before access
- Implement content filtering for resources
- Consider implementing resource access controls

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify server URL is correct
   - Check if MCP server is running
   - Ensure network connectivity

2. **Tool Execution Errors**
   - Verify tool parameters match schema
   - Check MCP server logs for errors
   - Ensure tool is available on server

3. **Resource Access Issues**
   - Verify resource URI is correct
   - Check resource permissions
   - Ensure resource exists on server

### Debugging

Enable debug logging for MCP operations:

```python
import logging
logging.getLogger("app.tools.mcp_tool").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Persistent Server Storage**: Save server configurations to database
- **Server Authentication**: Support for authenticated MCP servers
- **Tool Caching**: Cache tool schemas and results
- **Batch Operations**: Execute multiple tools in sequence
- **WebSocket Support**: Real-time MCP communication

### Integration Ideas
- **GitHub MCP Server**: Access repositories and code
- **Database MCP Server**: Query databases directly
- **File System MCP Server**: Access local files
- **Web Search MCP Server**: Perform web searches
- **Email MCP Server**: Send and read emails

## Contributing

To add new MCP server integrations:

1. **Create MCP Server**: Implement MCP protocol compliance
2. **Define Tools**: Create tool schemas and implementations
3. **Test Integration**: Verify with the platform
4. **Document**: Add usage examples and documentation

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [PydanticAI MCP Support](https://ai.pydantic.dev/mcp/) 