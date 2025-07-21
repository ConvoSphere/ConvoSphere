"""
File tools for the AI Assistant Platform.

This module provides tools for file reading and writing operations.
"""

from typing import Any

from .base import BaseTool


class FileReadTool(BaseTool):
    """Tool for reading files."""

    name = "file_read"
    description = "Read content from a file"
    parameters = {
        "file_path": {
            "type": "string",
            "description": "Path to the file to read",
        },
    }

    async def execute(self, file_path: str) -> dict[str, Any]:
        """Read a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
            }


class FileWriteTool(BaseTool):
    """Tool for writing files."""

    name = "file_write"
    description = "Write content to a file"
    parameters = {
        "file_path": {
            "type": "string",
            "description": "Path to the file to write",
        },
        "content": {
            "type": "string",
            "description": "Content to write to the file",
        },
    }

    async def execute(self, file_path: str, content: str) -> dict[str, Any]:
        """Write to a file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
            }
