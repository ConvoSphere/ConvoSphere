"""
Text extractor.

This module extracts text content from processed documents.
"""

from typing import Any


class TextExtractor:
    """Extracts text content from processed documents."""

    def extract(self, content: dict[str, Any]) -> str:
        """Extract text content from processed document content."""
        if "text" in content:
            return content["text"]
        raise ValueError("No text content found in document")
