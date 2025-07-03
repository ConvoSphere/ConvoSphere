# MCP API

## Overview

The MCP (Model Context Protocol) API allows integration with external MCP servers, enabling dynamic tool and resource management.

## Endpoints

### POST /mcp/servers
Add and connect to an MCP server.

**Request:**
```json
{
  "server_id": "example",
  "server_url": "http://localhost:8080",
  "server_name": "Example Server"
}
```
**Response:**
```json
{
  "server_id": "example",
  "server_name": "Example Server",
  "server_url": "http://localhost:8080",
  "is_connected": true,
  "tool_count": 4,
  "resource_count": 2
}
```
**Errors:**
- 400 Bad Request: Connection failed
- 500 Internal Server Error: Server not found after connection

---

### GET /mcp/servers
List all connected MCP servers.

**Response:**
```json
[
  {
    "server_id": "example",
    "server_name": "Example Server",
    "server_url": "http://localhost:8080",
    "is_connected": true,
    "tool_count": 4,
    "resource_count": 2
  }
]
```

---

### DELETE /mcp/servers/{server_id}
Remove an MCP server connection.

**Response:**
```json
{
  "message": "MCP server example removed successfully"
}
```
**Errors:**
- 404 Not Found: MCP server not found

---

### GET /mcp/tools
List all available MCP tools.

**Response:**
```json
[
  {
    "id": "example_get_weather",
    "name": "Get Weather",
    "description": "Get weather information for a location",
    "category": "utility",
    "server_name": "Example Server",
    "parameters": [
      { "name": "location", "type": "string", "required": true }
    ]
  }
]
```

---

### GET /mcp/tools/{tool_id}
Get details for a specific MCP tool.

**Response:**
```json
{
  "id": "example_get_weather",
  "name": "Get Weather",
  "description": "Get weather information for a location",
  "category": "utility",
  "server_name": "Example Server",
  "parameters": [
    { "name": "location", "type": "string", "required": true }
  ]
}
```
**Errors:**
- 404 Not Found: Tool does not exist

---

### POST /mcp/tools/{tool_id}/execute
Execute an MCP tool.

**Request:**
```json
{
  "arguments": {
    "location": "Berlin"
  }
}
```
**Response:**
```json
{
  "result": "The weather in Berlin is sunny and 25°C."
}
```
**Errors:**
- 400 Bad Request: Validation error
- 404 Not Found: Tool does not exist

---

### GET /mcp/servers/{server_id}/resources
List resources from an MCP server.

**Response:**
```json
[
  {
    "uri": "resource1",
    "type": "json",
    "description": "Sample resource"
  }
]
```

---

### POST /mcp/servers/{server_id}/resources/{resource_uri}/read
Read a resource from an MCP server.

**Response:**
```json
{
  "content": "..."
}
```
**Errors:**
- 404 Not Found: Resource does not exist 