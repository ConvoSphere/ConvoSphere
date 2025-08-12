"""
File validator.

This module validates document files.
"""

import mimetypes
from pathlib import Path

try:
    import magic  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    magic = None


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

        mime_type = self._detect_mime(file_path)
        if mime_type is None:
            return False
        return mime_type in self.SUPPORTED_TYPES

    def _detect_mime(self, file_path: str) -> str | None:
        """Detect MIME type using libmagic if available, else mimetypes as fallback."""
        if magic is not None:
            try:
                return magic.from_file(file_path, mime=True)
            except Exception:
                pass
        guessed, _ = mimetypes.guess_type(file_path)
        return guessed
