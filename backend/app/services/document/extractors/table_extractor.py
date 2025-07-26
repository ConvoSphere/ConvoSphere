"""
Table extractor.

This module extracts tables from documents.
"""

import re
from typing import Any


class TableExtractor:
    """Extracts tables from documents."""

    def extract(self, content: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract tables from document content."""
        text = content.get("text", "")
        tables = []

        # Simple table detection using regex patterns
        # This is a basic implementation - could be enhanced with more sophisticated parsing

        # Look for table-like structures
        lines = text.split("\n")
        current_table = []

        for line in lines:
            # Check if line contains table-like content (multiple columns separated by spaces/tabs)
            if re.match(r"^[\w\s]+\s{2,}[\w\s]+", line.strip()):
                current_table.append(line.strip())
            elif current_table:
                # End of table detected
                if len(current_table) > 1:  # At least header + one row
                    tables.append({
                        "rows": current_table,
                        "row_count": len(current_table)
                    })
                current_table = []

        # Handle table at end of document
        if current_table and len(current_table) > 1:
            tables.append({
                "rows": current_table,
                "row_count": len(current_table)
            })

        return tables
