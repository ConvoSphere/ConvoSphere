"""
Image document processor.

This module handles image document processing using OCR.
"""

from typing import Any

import pytesseract
from PIL import Image


class ImageProcessor:
    """Processes image documents using OCR."""

    def process(self, file_path: str) -> dict[str, Any]:
        """Process an image file and extract text using OCR."""
        try:
            image = Image.open(file_path)
            text_content = pytesseract.image_to_string(image)

            return {
                "text": text_content,
                "file_path": file_path,
                "image_size": image.size,
                "mode": image.mode,
            }
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
