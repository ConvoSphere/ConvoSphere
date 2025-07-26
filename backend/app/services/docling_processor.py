"""
Docling processor service for advanced document processing.

This module provides advanced document processing capabilities using Docling,
including PDF understanding, OCR, visual language models, and more.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    from docling import DocumentConverter

    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logging.warning("Docling not available. Install with: pip install docling")

from backend.app.core.config import get_settings

if TYPE_CHECKING:
    from docling.document import DoclingDocument

logger = logging.getLogger(__name__)


class DoclingProcessor:
    """Advanced document processor using Docling."""

    def __init__(self):
        self.docling_available = DOCLING_AVAILABLE
        if self.docling_available:
            self.converter = DocumentConverter()
        else:
            logger.warning("Docling not available. Using fallback processing.")

    def is_available(self) -> bool:
        """Check if Docling is available."""
        return self.docling_available

    def get_supported_formats(self) -> list[str]:
        """Get list of supported document formats."""
        if not self.docling_available:
            return []

        return [
            # Document formats
            "pdf",
            "docx",
            "pptx",
            "xlsx",
            "html",
            # Audio formats
            "wav",
            "mp3",
            "m4a",
            "flac",
            # Image formats
            "png",
            "jpg",
            "jpeg",
            "tiff",
            "bmp",
            "gif",
            "webp",
            # Text formats
            "txt",
            "md",
            "csv",
            "xml",
            "json",
        ]

    def process_document(
        self,
        file_content: bytes,
        filename: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process document using Docling with advanced features.

        Args:
            file_content: File content as bytes
            filename: Original filename
            options: Processing options

        Returns:
            Processing result with metadata and content
        """
        if not self.docling_available:
            return {
                "success": False,
                "error": "Docling not available",
                "content": "",
                "metadata": {},
            }

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(filename).suffix,
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Default options
            default_options = {
                "ocr": True,
                "ocr_language": "eng+deu",  # English + German
                "vision_model": None,  # Use local vision model if available
                "asr": True,  # Automatic Speech Recognition for audio
                "extract_tables": True,
                "extract_figures": True,
                "extract_formulas": True,
                "reading_order": True,
                "page_layout": True,
            }

            if options:
                default_options.update(options)

            # Process document with Docling
            docling_doc = self.converter.convert(
                temp_file_path,
                **default_options,
            )

            # Extract content and metadata
            result = self._extract_docling_content(docling_doc, filename)

            # Clean up temporary file
            os.unlink(temp_file_path)

            return result

        except Exception as e:
            logger.exception(f"Error processing document {filename} with Docling: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {},
            }

    def _extract_docling_content(
        self,
        doc: "DoclingDocument",
        filename: str,
    ) -> dict[str, Any]:
        """
        Extract content and metadata from Docling document.

        Args:
            doc: Docling document object
            filename: Original filename

        Returns:
            Extracted content and metadata
        """
        try:
            # Extract text content
            text_content = doc.text if hasattr(doc, "text") else ""

            # Extract metadata
            metadata = {
                "file_type": Path(filename).suffix.lower().lstrip("."),
                "file_size": len(text_content),
                "word_count": len(text_content.split()),
                "processing_engine": "docling",
                "docling_version": "0.1.0",
            }

            # Extract additional metadata if available
            if hasattr(doc, "metadata"):
                metadata.update(doc.metadata)

            # Extract tables if available
            tables = []
            if hasattr(doc, "tables") and doc.tables:
                for i, table in enumerate(doc.tables):
                    tables.append(
                        {
                            "id": f"table_{i}",
                            "content": str(table),
                            "position": getattr(table, "position", None),
                        },
                    )

            # Extract figures if available
            figures = []
            if hasattr(doc, "figures") and doc.figures:
                for i, figure in enumerate(doc.figures):
                    figures.append(
                        {
                            "id": f"figure_{i}",
                            "caption": getattr(figure, "caption", ""),
                            "position": getattr(figure, "position", None),
                        },
                    )

            # Extract formulas if available
            formulas = []
            if hasattr(doc, "formulas") and doc.formulas:
                for i, formula in enumerate(doc.formulas):
                    formulas.append(
                        {
                            "id": f"formula_{i}",
                            "content": str(formula),
                            "position": getattr(formula, "position", None),
                        },
                    )

            # Create chunks from content
            chunks = self._create_chunks_from_docling(doc)

            return {
                "success": True,
                "text": text_content,
                "chunks": chunks,
                "tables": tables,
                "figures": figures,
                "formulas": formulas,
                "metadata": metadata,
            }

        except Exception as e:
            logger.exception(f"Error extracting Docling content: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {},
            }

    def _create_chunks_from_docling(
        self,
        doc: "DoclingDocument",
    ) -> list[dict[str, Any]]:
        """
        Create chunks from Docling document with advanced features.

        Args:
            doc: Docling document object

        Returns:
            List of chunks with metadata
        """
        chunks = []

        try:
            # If document has pages, process each page
            if hasattr(doc, "pages") and doc.pages:
                for page_num, page in enumerate(doc.pages):
                    # Extract text from page
                    page_text = page.text if hasattr(page, "text") else ""

                    if page_text.strip():
                        chunks.append(
                            {
                                "content": page_text,
                                "page_number": page_num + 1,
                                "chunk_type": "page",
                                "start_word": 0,
                                "end_word": len(page_text.split()),
                                "token_count": len(page_text.split()),
                            },
                        )

                        # Extract tables from page
                        if hasattr(page, "tables") and page.tables:
                            for table_num, table in enumerate(page.tables):
                                table_text = f"Table {table_num + 1}: {str(table)}"
                                chunks.append(
                                    {
                                        "content": table_text,
                                        "page_number": page_num + 1,
                                        "chunk_type": "table",
                                        "table_id": f"table_{page_num}_{table_num}",
                                        "start_word": 0,
                                        "end_word": len(table_text.split()),
                                        "token_count": len(table_text.split()),
                                    },
                                )

                        # Extract figures from page
                        if hasattr(page, "figures") and page.figures:
                            for fig_num, figure in enumerate(page.figures):
                                fig_text = f"Figure {fig_num + 1}: {getattr(figure, 'caption', '')}"
                                chunks.append(
                                    {
                                        "content": fig_text,
                                        "page_number": page_num + 1,
                                        "chunk_type": "figure",
                                        "figure_id": f"figure_{page_num}_{fig_num}",
                                        "start_word": 0,
                                        "end_word": len(fig_text.split()),
                                        "token_count": len(fig_text.split()),
                                    },
                                )

            # If no pages, create chunks from full text
            else:
                full_text = doc.text if hasattr(doc, "text") else ""
                if full_text.strip():
                    # Simple chunking for full text
                    words = full_text.split()
                    chunk_size = get_settings().chunk_size
                    chunk_overlap = get_settings().chunk_overlap

                    for i in range(0, len(words), chunk_size - chunk_overlap):
                        chunk_words = words[i : i + chunk_size]
                        chunk_text = " ".join(chunk_words)

                        chunks.append(
                            {
                                "content": chunk_text,
                                "chunk_type": "text",
                                "start_word": i,
                                "end_word": min(i + chunk_size, len(words)),
                                "token_count": len(chunk_words),
                            },
                        )

            return chunks

        except Exception as e:
            logger.exception(f"Error creating chunks from Docling document: {e}")
            return []

    def process_audio(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """
        Process audio files with ASR (Automatic Speech Recognition).

        Args:
            file_content: Audio file content
            filename: Audio filename

        Returns:
            Processing result with transcribed text
        """
        if not self.docling_available:
            return {
                "success": False,
                "error": "Docling not available",
                "content": "",
                "metadata": {},
            }

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(filename).suffix,
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Process audio with ASR
            docling_doc = self.converter.convert(
                temp_file_path,
                asr=True,
                asr_model="whisper",  # Use Whisper for ASR
            )

            # Extract transcribed text
            transcribed_text = docling_doc.text if hasattr(docling_doc, "text") else ""

            # Clean up temporary file
            os.unlink(temp_file_path)

            return {
                "success": True,
                "text": transcribed_text,
                "chunks": [
                    {
                        "content": transcribed_text,
                        "chunk_type": "audio_transcription",
                        "start_word": 0,
                        "end_word": len(transcribed_text.split()),
                        "token_count": len(transcribed_text.split()),
                    },
                ],
                "metadata": {
                    "file_type": "audio",
                    "processing_engine": "docling_asr",
                    "asr_model": "whisper",
                },
            }

        except Exception as e:
            logger.exception(f"Error processing audio {filename} with Docling: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {},
            }

    def process_image(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """
        Process images with visual language models.

        Args:
            file_content: Image file content
            filename: Image filename

        Returns:
            Processing result with image analysis
        """
        if not self.docling_available:
            return {
                "success": False,
                "error": "Docling not available",
                "content": "",
                "metadata": {},
            }

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(filename).suffix,
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Process image with vision model
            docling_doc = self.converter.convert(
                temp_file_path,
                vision_model="smoldocling",  # Use SmolDocling for vision
                ocr=True,
            )

            # Extract image analysis
            image_text = docling_doc.text if hasattr(docling_doc, "text") else ""

            # Clean up temporary file
            os.unlink(temp_file_path)

            return {
                "success": True,
                "text": image_text,
                "chunks": [
                    {
                        "content": image_text,
                        "chunk_type": "image_analysis",
                        "start_word": 0,
                        "end_word": len(image_text.split()),
                        "token_count": len(image_text.split()),
                    },
                ],
                "metadata": {
                    "file_type": "image",
                    "processing_engine": "docling_vision",
                    "vision_model": "smoldocling",
                },
            }

        except Exception as e:
            logger.exception(f"Error processing image {filename} with Docling: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {},
            }


# Global Docling processor instance
docling_processor = DoclingProcessor()
