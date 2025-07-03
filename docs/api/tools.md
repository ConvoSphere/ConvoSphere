# Tools API

## Overview

Tool endpoints allow you to list, configure, and execute tools available to assistants. Tools can be internal or provided via MCP servers.

## Endpoints

### GET /tools
List all available tools.

**Response:**
```json
{
  "items": [
    {
      "id": "web_search",
      "name": "Web Search",
      "description": "Search the web for information",
      "category": "search",
      "parameters": {
        "query": { "type": "string", "required": true }
      }
    }
  ]
}
```
**Errors:**
- 401 Unauthorized: Invalid token

---

### GET /tools/{tool_id}
Get details for a specific tool.

**Response:**
```json
{
  "id": "web_search",
  "name": "Web Search",
  "description": "Search the web for information",
  "category": "search",
  "parameters": {
    "query": { "type": "string", "required": true }
  }
}
```
**Errors:**
- 404 Not Found: Tool does not exist

---

### POST /tools/{tool_id}/execute
Execute a tool with the given parameters.

**Request:**
```json
{
  "arguments": {
    "query": "What is the weather in Berlin?"
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
- 400 Bad Request: Validation error or missing parameters
- 404 Not Found: Tool does not exist
- 429 Too Many Requests: Rate limit exceeded 