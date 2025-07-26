"""
Metadata extractor.

This module extracts metadata from documents.
"""

import os
from datetime import datetime
from typing import Any


class MetadataExtractor:
    """Extracts metadata from documents."""

    def extract(self, file_path: str, content: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata from a document."""
        file_stat = os.stat(file_path)

        metadata = {
            "file_name": os.path.basename(file_path),
            "file_size": file_stat.st_size,
            "created_time": datetime.fromtimestamp(file_stat.st_ctime),
            "modified_time": datetime.fromtimestamp(file_stat.st_mtime),
            "file_path": file_path,
        }

        # Add content-specific metadata
        if "page_count" in content:
            metadata["page_count"] = content["page_count"]

        if "character_count" in content:
            metadata["character_count"] = content["character_count"]

        if "image_size" in content:
            metadata["image_size"] = content["image_size"]

        if "paragraph_count" in content:
            metadata["paragraph_count"] = content["paragraph_count"]

        return metadata
