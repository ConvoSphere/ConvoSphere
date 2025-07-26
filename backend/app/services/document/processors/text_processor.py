"""
Text document processor.

This module handles text document processing.
"""

from typing import Any


class TextProcessor:
    """Processes text documents."""

    def process(self, file_path: str) -> dict[str, Any]:
        """Process a text file and extract its content."""
        try:
            with open(file_path, encoding="utf-8") as file:
                content = file.read()

            return {
                "text": content,
                "file_path": file_path,
                "character_count": len(content),
            }
        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")
