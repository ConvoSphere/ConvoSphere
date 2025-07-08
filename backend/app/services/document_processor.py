"""
Document processor service.

This module provides functionality for processing different document types,
extracting text content, and preparing documents for embedding generation.
Uses Docling for advanced document processing with fallback to traditional methods.
"""

import io
import logging
from typing import List, Dict, Any
from pathlib import Path

# Keep minimal imports for fallback processing
import magic

from app.core.config import settings
from .docling_processor import docling_processor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing different document types using Docling with fallbacks."""
    
    SUPPORTED_TYPES = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'text/plain': 'txt',
        'text/markdown': 'md',
        'text/html': 'html',
        'text/csv': 'csv',
        'application/json': 'json',
        'application/xml': 'xml',
        'image/jpeg': 'image',
        'image/png': 'image',
        'image/gif': 'image',
        'image/bmp': 'image',
        'image/tiff': 'image',
        'image/webp': 'image',
        'audio/wav': 'audio',
        'audio/mpeg': 'audio',
        'audio/mp4': 'audio',
        'audio/flac': 'audio'
    }
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
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
            elif ext == '.pptx':
                return 'pptx'
            elif ext == '.xlsx':
                return 'xlsx'
            elif ext == '.txt':
                return 'txt'
            elif ext == '.md':
                return 'md'
            elif ext == '.html':
                return 'html'
            elif ext == '.csv':
                return 'csv'
            elif ext == '.json':
                return 'json'
            elif ext == '.xml':
                return 'xml'
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                return 'image'
            elif ext in ['.wav', '.mp3', '.m4a', '.flac']:
                return 'audio'
            
            logger.warning(f"Unsupported file type: {mime_type} for file {filename}")
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return 'unknown'
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extract text content from document using Docling with fallbacks.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Extracted text content
        """
        try:
            file_type = self.detect_file_type(file_content, filename)
            
            # Use Docling for all supported formats
            if docling_processor.is_available():
                supported_formats = docling_processor.get_supported_formats()
                if file_type in supported_formats:
                    logger.info(f"Using Docling for {file_type} file: {filename}")
                    result = docling_processor.process_document(file_content, filename)
                    if result['success']:
                        return result['text']
                    else:
                        logger.warning(f"Docling processing failed for {filename}: {result.get('error')}")
            
            # Fallback to traditional processing only for unsupported formats
            if file_type == 'txt':
                return self._extract_txt_text(file_content)
            else:
                logger.warning(f"No processing method available for {file_type} file: {filename}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
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
        Process a document completely using Docling with fallbacks.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Processing result with metadata and chunks
        """
        try:
            file_type = self.detect_file_type(file_content, filename)
            
            # Use Docling for all supported formats
            if docling_processor.is_available():
                supported_formats = docling_processor.get_supported_formats()
                if file_type in supported_formats:
                    logger.info(f"Using Docling for advanced processing of {file_type} file: {filename}")
                    result = docling_processor.process_document(file_content, filename)
                    if result['success']:
                        # Add additional metadata
                        result['metadata'].update({
                            'processing_engine': 'docling',
                            'file_size': len(file_content),
                            'processing_success': True
                        })
                        return result
                    else:
                        logger.warning(f"Docling processing failed for {filename}: {result.get('error')}")
            
            # Fallback to basic text processing for unsupported formats
            if file_type == 'txt':
                text = self._extract_txt_text(file_content)
                
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
                    'file_type': file_type,
                    'file_size': len(file_content),
                    'text_length': len(text),
                    'word_count': len(text.split()),
                    'chunk_count': len(chunks),
                    'processing_engine': 'traditional',
                    'processing_success': True
                }
                
                return {
                    'success': True,
                    'text': text,
                    'chunks': chunks,
                    'tables': [],
                    'figures': [],
                    'formulas': [],
                    'metadata': metadata
                }
            else:
                return {
                    'success': False,
                    'error': f'No processing method available for {file_type} files',
                    'chunks': [],
                    'metadata': {}
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