"""
Content validator.

This module validates document content.
"""

import re


class ContentValidator:
    """Validates document content."""

    def validate_content(self, text: str) -> bool:
        """Validate document content."""
        if not text or not text.strip():
            return False

        # Check for minimum content length
        if len(text.strip()) < 10:
            return False

        # Check for excessive whitespace
        if len(re.findall(r"\s{10,}", text)) > 0:
            return False

        # Check for suspicious content patterns
        suspicious_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"data:text/html",
            r"vbscript:",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False

        return True
