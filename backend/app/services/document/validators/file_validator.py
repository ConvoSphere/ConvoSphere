"""
File validator.

This module validates document files.
"""

from pathlib import Path

import magic


class FileValidator:
    """Validates document files."""

    SUPPORTED_TYPES = [
        "application/pdf",
        "text/plain",
        "text/markdown",
        "image/jpeg",
        "image/png",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ]

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    def validate_file(self, file_path: str) -> bool:
        """Validate a file for processing."""
        path = Path(file_path)
        if not path.exists():
            return False

        if not path.is_file():
            return False

        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            return False

        mime_type = magic.from_file(file_path, mime=True)
        return mime_type in self.SUPPORTED_TYPES
