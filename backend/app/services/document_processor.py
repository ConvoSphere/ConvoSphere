"""
Document processor service.

This module provides functionality for processing different document types,
extracting text content, and preparing documents for embedding generation.
"""

import io
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import magic
import markdown
import pypdf
import tiktoken
from docx import Document

from app.core.config import get_settings

from .docling_processor import docling_processor

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Document chunk with enhanced metadata."""

    content: str
    chunk_id: str
    start_position: int
    end_position: int
    token_count: int
    word_count: int
    chunk_type: str = "text"
    metadata: dict[str, Any] = None
    importance_score: float = 1.0
    language: str = "en"
    entities: list[str] = None


@dataclass
class DocumentMetadata:
    """Enhanced document metadata."""

    file_type: str
    file_size: int
    text_length: int
    word_count: int
    chunk_count: int
    processing_engine: str
    processing_success: bool
    language: str = "en"
    title: str | None = None
    author: str | None = None
    creation_date: datetime | None = None
    modification_date: datetime | None = None
    keywords: list[str] = None
    summary: str | None = None
    reading_time_minutes: float | None = None
    complexity_score: float | None = None
    topics: list[str] = None
    entities: list[str] = None


class DocumentProcessor:
    """Service for processing different document types."""

    SUPPORTED_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
        "text/markdown": "md",
        "text/html": "html",
        "image/jpeg": "image",
        "image/png": "image",
        "image/gif": "image",
        "image/bmp": "image",
        "image/tiff": "image",
    }

    def __init__(self):
        settings = get_settings()
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.min_chunk_size = 50  # Minimum chunk size in words
        self.max_chunk_size = 1000  # Maximum chunk size in words

        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        except Exception as e:
            logger.warning(f"Could not initialize tokenizer: {e}")
            self.tokenizer = None

        # Chunking strategies
        self.chunking_strategies = {
            "semantic": self._semantic_chunking,
            "fixed": self._fixed_chunking,
            "paragraph": self._paragraph_chunking,
            "sentence": self._sentence_chunking,
        }

    def detect_file_type(self, file_content: bytes, filename: str) -> str:
        """
        Detect file type from content and filename.

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Detected file type
        """
        try:
            # Use python-magic to detect MIME type
            mime_type = magic.from_buffer(file_content, mime=True)

            if mime_type in self.SUPPORTED_TYPES:
                return self.SUPPORTED_TYPES[mime_type]

            # Fallback to file extension
            ext = Path(filename).suffix.lower()
            if ext == ".pdf":
                return "pdf"
            if ext == ".docx":
                return "docx"
            if ext == ".txt":
                return "txt"
            if ext == ".md":
                return "md"
            if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
                return "image"

            logger.warning(f"Unsupported file type: {mime_type} for file {filename}")
            return "unknown"

        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return "unknown"

    def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extract text content from document.

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Extracted text content
        """
        try:
            file_type = self.detect_file_type(file_content, filename)

            # Try Docling first if available and supported
            if docling_processor.is_available():
                supported_formats = docling_processor.get_supported_formats()
                if file_type in supported_formats:
                    logger.info(f"Using Docling for {file_type} file: {filename}")
                    result = docling_processor.process_document(file_content, filename)
                    if result["success"]:
                        return result["text"]
                    logger.warning(
                        f"Docling processing failed for {filename}: {result.get('error')}",
                    )

            # Fallback to traditional processing
            if file_type == "pdf":
                return self._extract_pdf_text(file_content)
            if file_type == "docx":
                return self._extract_docx_text(file_content)
            if file_type == "txt":
                return self._extract_txt_text(file_content)
            if file_type == "md":
                return self._extract_markdown_text(file_content)
            if file_type == "html":
                return self._extract_html_text(file_content)
            if file_type == "image":
                return self._extract_image_text(file_content)
            return ""

        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            return ""

    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = pypdf.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""

    def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""

    def _extract_txt_text(self, file_content: bytes) -> str:
        """Extract text from plain text file."""
        try:
            # Try different encodings
            encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

            for encoding in encodings:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue

            # If all encodings fail, use latin-1 as fallback
            return file_content.decode("latin-1", errors="ignore")

        except Exception as e:
            logger.error(f"Error extracting text file content: {e}")
            return ""

    def _extract_markdown_text(self, file_content: bytes) -> str:
        """Extract text from markdown file."""
        try:
            # First get raw text
            raw_text = self._extract_txt_text(file_content)

            # Convert markdown to plain text
            html = markdown.markdown(raw_text)

            # Simple HTML to text conversion
            import re

            text = re.sub(r"<[^>]+>", "", html)
            text = re.sub(r"\n\s*\n", "\n\n", text)

            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting markdown text: {e}")
            return ""

    def _extract_html_text(self, file_content: bytes) -> str:
        """Extract text from HTML file."""
        try:
            from bs4 import BeautifulSoup

            raw_text = self._extract_txt_text(file_content)
            soup = BeautifulSoup(raw_text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return " ".join(chunk for chunk in chunks if chunk)


        except Exception as e:
            logger.error(f"Error extracting HTML text: {e}")
            return ""

    def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            # For now, return empty string
            # In a real implementation, this would use OCR libraries like Tesseract
            # or cloud OCR services like Google Vision API
            logger.info("OCR extraction not implemented yet")
            return ""

        except Exception as e:
            logger.error(f"Error extracting image text: {e}")
            return ""

    def chunk_text(
        self,
        text: str,
        strategy: str = "semantic",
        chunk_size: int | None = None,
        overlap: int | None = None,
    ) -> list[DocumentChunk]:
        """
        Split text into chunks using different strategies.

        Args:
            text: Text to chunk
            strategy: Chunking strategy ("semantic", "fixed", "paragraph", "sentence")
            chunk_size: Override default chunk size
            overlap: Override default overlap

        Returns:
            List of document chunks
        """
        if not text:
            return []

        # Use provided parameters or defaults
        size = chunk_size or self.chunk_size
        overlap_size = overlap or self.chunk_overlap

        # Get chunking strategy
        chunking_func = self.chunking_strategies.get(strategy, self._semantic_chunking)

        # Create chunks
        raw_chunks = chunking_func(text, size, overlap_size)

        # Convert to DocumentChunk objects
        document_chunks = []
        for i, chunk_data in enumerate(raw_chunks):
            chunk = DocumentChunk(
                content=chunk_data["content"],
                chunk_id=f"chunk_{i}",
                start_position=chunk_data.get("start_position", 0),
                end_position=chunk_data.get("end_position", len(chunk_data["content"])),
                token_count=self._count_tokens(chunk_data["content"]),
                word_count=len(chunk_data["content"].split()),
                chunk_type=chunk_data.get("type", "text"),
                metadata=chunk_data.get("metadata", {}),
                importance_score=self._calculate_importance(chunk_data["content"]),
                language=self._detect_language(chunk_data["content"]),
                entities=self._extract_entities(chunk_data["content"]),
            )
            document_chunks.append(chunk)

        return document_chunks

    def _semantic_chunking(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[dict[str, Any]]:
        """Semantic chunking that respects paragraph and sentence boundaries."""
        # Split into paragraphs first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        current_start = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If adding this paragraph would exceed chunk size
            if (
                len(current_chunk) + len(paragraph) > chunk_size * 5
            ):  # Approximate word length
                if current_chunk:
                    chunks.append(
                        {
                            "content": current_chunk.strip(),
                            "start_position": current_start,
                            "end_position": current_start + len(current_chunk),
                            "type": "semantic",
                        },
                    )

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, overlap)
                current_chunk = overlap_text + paragraph
                current_start = current_start + len(current_chunk) - len(overlap_text)
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph

        # Add final chunk
        if current_chunk:
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "start_position": current_start,
                    "end_position": current_start + len(current_chunk),
                    "type": "semantic",
                },
            )

        return chunks

    def _fixed_chunking(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[dict[str, Any]]:
        """Fixed-size chunking with overlap."""
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunks.append(
                {
                    "content": chunk_text,
                    "start_position": start,
                    "end_position": end,
                    "type": "fixed",
                },
            )

            start = end - overlap
            if start >= len(words):
                break

        return chunks

    def _paragraph_chunking(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[dict[str, Any]]:
        """Chunk by paragraphs."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []

        for i, paragraph in enumerate(paragraphs):
            chunks.append(
                {
                    "content": paragraph,
                    "start_position": i,
                    "end_position": i + 1,
                    "type": "paragraph",
                    "metadata": {"paragraph_index": i},
                },
            )

        return chunks

    def _sentence_chunking(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[dict[str, Any]]:
        """Chunk by sentences."""
        # Simple sentence splitting
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""
        sentence_count = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size * 5:
                if current_chunk:
                    chunks.append(
                        {
                            "content": current_chunk.strip(),
                            "start_position": sentence_count
                            - len(current_chunk.split("."))
                            + 1,
                            "end_position": sentence_count,
                            "type": "sentence",
                        },
                    )
                current_chunk = sentence
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
            sentence_count += 1

        if current_chunk:
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "start_position": sentence_count
                    - len(current_chunk.split("."))
                    + 1,
                    "end_position": sentence_count,
                    "type": "sentence",
                },
            )

        return chunks

    def _get_overlap_text(self, text: str, overlap_words: int) -> str:
        """Get overlap text from the end of a chunk."""
        words = text.split()
        if len(words) <= overlap_words:
            return text

        overlap_words_list = words[-overlap_words:]
        return " ".join(overlap_words_list)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Fallback: approximate token count
        return len(text.split()) * 1.3

    def _calculate_importance(self, text: str) -> float:
        """Calculate importance score for a chunk."""
        # Simple heuristics for importance
        score = 1.0

        # Boost for headers
        if text.startswith("#") or text.isupper():
            score += 0.5

        # Boost for numbers and dates
        if re.search(r"\d+", text):
            score += 0.2

        # Boost for technical terms
        technical_terms = [
            "api",
            "function",
            "class",
            "method",
            "error",
            "config",
            "database",
        ]
        for term in technical_terms:
            if term.lower() in text.lower():
                score += 0.1

        return min(score, 2.0)  # Cap at 2.0

    def _detect_language(self, text: str) -> str:
        """Detect language of text."""
        # Simple language detection
        german_chars = set("äöüßÄÖÜ")
        text_chars = set(text)

        if german_chars.intersection(text_chars):
            return "de"
        return "en"

    def _extract_entities(self, text: str) -> list[str]:
        """Extract named entities from text."""
        entities = []

        # Extract URLs
        urls = re.findall(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            text,
        )
        entities.extend(urls)

        # Extract email addresses
        emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text,
        )
        entities.extend(emails)

        # Extract potential names (capitalized words)
        names = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text)
        entities.extend(names)

        return list(set(entities))  # Remove duplicates

    def _create_enhanced_metadata(
        self,
        file_type: str,
        file_content: bytes,
        text: str,
        chunks: list[DocumentChunk],
    ) -> dict[str, Any]:
        """Create enhanced metadata for document."""
        # Basic metadata
        metadata = {
            "file_type": file_type,
            "file_size": len(file_content),
            "text_length": len(text),
            "word_count": len(text.split()),
            "chunk_count": len(chunks),
            "processing_engine": "enhanced",
            "processing_success": True,
            "processing_timestamp": datetime.now().isoformat(),
        }

        # Language detection
        languages = [chunk.language for chunk in chunks if chunk.language]
        if languages:
            primary_language = max(set(languages), key=languages.count)
            metadata["language"] = primary_language
            metadata["language_distribution"] = {
                lang: languages.count(lang) for lang in set(languages)
            }

        # Extract title (first line or first chunk)
        if chunks:
            first_chunk = chunks[0].content
            lines = first_chunk.split("\n")
            if lines:
                potential_title = lines[0].strip()
                if len(potential_title) < 200 and not potential_title.startswith("#"):
                    metadata["title"] = potential_title

        # Calculate reading time (average 200 words per minute)
        word_count = len(text.split())
        metadata["reading_time_minutes"] = round(word_count / 200, 1)

        # Calculate complexity score
        avg_sentence_length = self._calculate_avg_sentence_length(text)
        metadata["complexity_score"] = min(
            avg_sentence_length / 20, 1.0,
        )  # Normalize to 0-1

        # Extract topics from chunks
        topics = self._extract_topics(chunks)
        if topics:
            metadata["topics"] = topics

        # Extract all entities
        all_entities = []
        for chunk in chunks:
            if chunk.entities:
                all_entities.extend(chunk.entities)
        if all_entities:
            metadata["entities"] = list(set(all_entities))

        # Calculate average importance score
        if chunks:
            avg_importance = sum(chunk.importance_score for chunk in chunks) / len(
                chunks,
            )
            metadata["average_importance_score"] = round(avg_importance, 2)

        # Extract keywords (simple approach)
        keywords = self._extract_keywords(text)
        if keywords:
            metadata["keywords"] = keywords

        return metadata

    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length."""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)

    def _extract_topics(self, chunks: list[DocumentChunk]) -> list[str]:
        """Extract topics from document chunks."""
        # Simple topic extraction based on common technical terms
        technical_terms = {
            "programming": [
                "api",
                "function",
                "class",
                "method",
                "code",
                "programming",
            ],
            "database": ["database", "sql", "query", "table", "schema"],
            "web": ["web", "http", "html", "css", "javascript", "frontend", "backend"],
            "ai": ["ai", "machine learning", "neural", "model", "training"],
            "devops": ["deployment", "docker", "kubernetes", "ci/cd", "infrastructure"],
            "security": ["security", "authentication", "authorization", "encryption"],
        }

        all_text = " ".join(chunk.content.lower() for chunk in chunks)
        found_topics = []

        for topic, terms in technical_terms.items():
            for term in terms:
                if term in all_text:
                    found_topics.append(topic)
                    break

        return list(set(found_topics))

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Remove common stop words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "this",
            "that",
            "these",
            "those",
            "a",
            "an",
            "as",
            "from",
            "not",
            "no",
            "yes",
            "if",
            "then",
            "else",
            "when",
            "where",
            "why",
            "how",
            "what",
            "which",
        }

        # Count word frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top 10 keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]

    def process_pdf(self, file_path: str) -> str:
        """Process PDF document and extract text."""
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
            return self._extract_pdf_text(file_content)
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return ""

    def process_docx(self, file_path: str) -> str:
        """Process DOCX document and extract text."""
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
            return self._extract_docx_text(file_content)
        except Exception as e:
            logger.error(f"Error processing DOCX {file_path}: {e}")
            return ""

    def process_txt(self, file_path: str) -> str:
        """Process TXT document and extract text."""
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
            return self._extract_txt_text(file_content)
        except Exception as e:
            logger.error(f"Error processing TXT {file_path}: {e}")
            return ""

    def process_document(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """
        Process a document completely.

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Processing result with metadata and chunks
        """
        try:
            file_type = self.detect_file_type(file_content, filename)

            # Try Docling first if available and supported
            if docling_processor.is_available():
                supported_formats = docling_processor.get_supported_formats()
                if file_type in supported_formats:
                    logger.info(
                        f"Using Docling for advanced processing of {file_type} file: {filename}",
                    )
                    result = docling_processor.process_document(file_content, filename)
                    if result["success"]:
                        # Add additional metadata
                        result["metadata"].update(
                            {
                                "processing_engine": "docling",
                                "file_size": len(file_content),
                                "processing_success": True,
                            },
                        )
                        return result
                    logger.warning(
                        f"Docling processing failed for {filename}: {result.get('error')}",
                    )

            # Fallback to traditional processing
            # Extract text
            text = self.extract_text(file_content, filename)

            if not text:
                return {
                    "success": False,
                    "error": "No text content extracted",
                    "chunks": [],
                    "metadata": {},
                }

            # Create chunks with enhanced processing
            document_chunks = self.chunk_text(text, strategy="semantic")

            # Convert to legacy format for compatibility
            chunks = []
            for chunk in document_chunks:
                chunks.append(
                    {
                        "content": chunk.content,
                        "start_word": chunk.start_position,
                        "end_word": chunk.end_position,
                        "token_count": chunk.token_count,
                        "metadata": {
                            "chunk_id": chunk.chunk_id,
                            "chunk_type": chunk.chunk_type,
                            "importance_score": chunk.importance_score,
                            "language": chunk.language,
                            "entities": chunk.entities,
                            **(chunk.metadata or {}),
                        },
                    },
                )

            # Create enhanced metadata
            metadata = self._create_enhanced_metadata(
                file_type,
                file_content,
                text,
                document_chunks,
            )

            return {
                "success": True,
                "text": text,
                "chunks": chunks,
                "tables": [],
                "figures": [],
                "formulas": [],
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunks": [],
                "metadata": {},
            }


# Global document processor instance
document_processor = DocumentProcessor()
