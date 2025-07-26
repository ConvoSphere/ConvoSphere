"""
Text extractor.

This module extracts text content from processed documents.
"""

from typing import Dict, Any


class TextExtractor:
    """Extracts text content from processed documents."""
    
    def extract(self, content: Dict[str, Any]) -> str:
        """Extract text content from processed document content."""
        if "text" in content:
            return content["text"]
        else:
            raise ValueError("No text content found in document")
