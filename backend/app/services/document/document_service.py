"""
Main document processing service.

This service coordinates document processing operations.
"""

from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from .extractors.metadata_extractor import MetadataExtractor
from .extractors.table_extractor import TableExtractor
from .extractors.text_extractor import TextExtractor
from .processors.image_processor import ImageProcessor
from .processors.pdf_processor import PDFProcessor
from .processors.text_processor import TextProcessor
from .processors.word_processor import WordProcessor
from .validators.content_validator import ContentValidator
from .validators.file_validator import FileValidator


class DocumentService:
    """Main document service that coordinates all document processing."""

    def __init__(self, db: Session):
        self.db = db
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
        self.image_processor = ImageProcessor()
        self.word_processor = WordProcessor()
        self.text_extractor = TextExtractor()
        self.metadata_extractor = MetadataExtractor()
        self.table_extractor = TableExtractor()
        self.file_validator = FileValidator()
        self.content_validator = ContentValidator()

    def process_document(self, file_path: str, user_id: int) -> dict[str, Any]:
        """Process a document and extract its content."""
        # Validate file
        if not self.file_validator.validate_file(file_path):
            raise ValueError("Invalid file")

        # Determine file type and process accordingly
        file_extension = Path(file_path).suffix.lower()

        if file_extension == ".pdf":
            content = self.pdf_processor.process(file_path)
        elif file_extension in [".txt", ".md"]:
            content = self.text_processor.process(file_path)
        elif file_extension in [".jpg", ".jpeg", ".png"]:
            content = self.image_processor.process(file_path)
        elif file_extension in [".doc", ".docx"]:
            content = self.word_processor.process(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Extract text and metadata
        extracted_text = self.text_extractor.extract(content)
        metadata = self.metadata_extractor.extract(file_path, content)
        tables = self.table_extractor.extract(content)

        # Validate content
        if not self.content_validator.validate_content(extracted_text):
            raise ValueError("Invalid content")

        return {
            "text": extracted_text,
            "metadata": metadata,
            "tables": tables,
            "file_type": file_extension,
        }

    def batch_process(
        self, file_paths: list[str], user_id: int
    ) -> list[dict[str, Any]]:
        """Process multiple documents in batch."""
        results = []

        for file_path in file_paths:
            try:
                result = self.process_document(file_path, user_id)
                results.append(
                    {"file_path": file_path, "success": True, "result": result}
                )
            except Exception as e:
                results.append(
                    {"file_path": file_path, "success": False, "error": str(e)}
                )

        return results
