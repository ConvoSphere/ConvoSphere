#!/usr/bin/env python3
"""
Script to start the example MCP server for testing.

This script starts the example MCP server that provides test tools
for the AI Assistant Platform MCP integration.
"""

import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.tools.example_mcp_server import main


if __name__ == "__main__":
    print("Starting Example MCP Server...")
    print("Server will be available at: http://localhost:8080")
    print("Health check: http://localhost:8080/health")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        sys.exit(1) 