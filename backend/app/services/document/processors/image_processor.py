"""
Image document processor.

This module handles image document processing using OCR.
"""

import pytesseract
from PIL import Image
from typing import Dict, Any


class ImageProcessor:
    """Processes image documents using OCR."""
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """Process an image file and extract text using OCR."""
        try:
            image = Image.open(file_path)
            text_content = pytesseract.image_to_string(image)
            
            return {
                "text": text_content,
                "file_path": file_path,
                "image_size": image.size,
                "mode": image.mode
            }
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
