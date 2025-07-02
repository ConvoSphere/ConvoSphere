"""
Document processor service.

This module provides functionality for processing different document types,
extracting text content, and preparing documents for embedding generation.
"""

import os
import io
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import PyPDF2
from docx import Document
import markdown
from PIL import Image
import textract
import magic

from core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing different document types."""
    
    SUPPORTED_TYPES = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'text/plain': 'txt',
        'text/markdown': 'md',
        'text/html': 'html',
        'image/jpeg': 'image',
        'image/png': 'image',
        'image/gif': 'image',
        'image/bmp': 'image',
        'image/tiff': 'image'
    }
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
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
            if ext == '.pdf':
                return 'pdf'
            elif ext == '.docx':
                return 'docx'
            elif ext == '.txt':
                return 'txt'
            elif ext == '.md':
                return 'md'
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                return 'image'
            
            logger.warning(f"Unsupported file type: {mime_type} for file {filename}")
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return 'unknown'
    
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
            
            if file_type == 'pdf':
                return self._extract_pdf_text(file_content)
            elif file_type == 'docx':
                return self._extract_docx_text(file_content)
            elif file_type == 'txt':
                return self._extract_txt_text(file_content)
            elif file_type == 'md':
                return self._extract_markdown_text(file_content)
            elif file_type == 'html':
                return self._extract_html_text(file_content)
            elif file_type == 'image':
                return self._extract_image_text(file_content)
            else:
                # Try textract as fallback
                return self._extract_with_textract(file_content, filename)
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            return ""
    
    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
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
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use latin-1 as fallback
            return file_content.decode('latin-1', errors='ignore')
            
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
            text = re.sub(r'<[^>]+>', '', html)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting markdown text: {e}")
            return ""
    
    def _extract_html_text(self, file_content: bytes) -> str:
        """Extract text from HTML file."""
        try:
            from bs4 import BeautifulSoup
            
            raw_text = self._extract_txt_text(file_content)
            soup = BeautifulSoup(raw_text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
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
    
    def _extract_with_textract(self, file_content: bytes, filename: str) -> str:
        """Extract text using textract library."""
        try:
            # Save temporary file
            temp_path = f"/tmp/{filename}"
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            # Extract text
            text = textract.process(temp_path).decode('utf-8')
            
            # Clean up
            os.remove(temp_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting with textract: {e}")
            return ""
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Text content to chunk
            
        Returns:
            List of text chunks with metadata
        """
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            # Single chunk
            chunks.append({
                'content': text,
                'start_word': 0,
                'end_word': len(words),
                'token_count': len(words)
            })
        else:
            # Multiple chunks with overlap
            start = 0
            while start < len(words):
                end = min(start + self.chunk_size, len(words))
                
                chunk_words = words[start:end]
                chunk_text = ' '.join(chunk_words)
                
                chunks.append({
                    'content': chunk_text,
                    'start_word': start,
                    'end_word': end,
                    'token_count': len(chunk_words)
                })
                
                # Move start position with overlap
                start = end - self.chunk_overlap
                if start >= len(words):
                    break
        
        return chunks
    
    def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a document completely.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Processing result with metadata and chunks
        """
        try:
            # Extract text
            text = self.extract_text(file_content, filename)
            
            if not text:
                return {
                    'success': False,
                    'error': 'No text content extracted',
                    'chunks': [],
                    'metadata': {}
                }
            
            # Create chunks
            chunks = self.chunk_text(text)
            
            # Calculate metadata
            metadata = {
                'file_type': self.detect_file_type(file_content, filename),
                'file_size': len(file_content),
                'text_length': len(text),
                'word_count': len(text.split()),
                'chunk_count': len(chunks),
                'processing_success': True
            }
            
            return {
                'success': True,
                'text': text,
                'chunks': chunks,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            return {
                'success': False,
                'error': str(e),
                'chunks': [],
                'metadata': {}
            }


# Global document processor instance
document_processor = DocumentProcessor() 