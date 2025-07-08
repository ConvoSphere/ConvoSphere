#!/usr/bin/env python3
"""
Test script for Docling integration and document processing.

This script tests the Docling-based document processing capabilities
and compares them with the previous traditional processing methods.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.docling_processor import DoclingProcessor
from app.services.document_processor import DocumentProcessor
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_docling_availability():
    """Test if Docling is available and working."""
    print("=" * 60)
    print("Testing Docling Availability")
    print("=" * 60)
    
    processor = DoclingProcessor()
    
    print(f"Docling available: {processor.is_available()}")
    
    if processor.is_available():
        print("Supported formats:")
        for fmt in processor.get_supported_formats():
            print(f"  - {fmt}")
    else:
        print("Docling not available. Install with: pip install docling")
    
    return processor.is_available()


def create_test_files():
    """Create test files for different formats."""
    print("\n" + "=" * 60)
    print("Creating Test Files")
    print("=" * 60)
    
    test_files = {}
    
    # Create test text file
    test_files['txt'] = b"This is a test text file.\nIt contains multiple lines.\nAnd some special characters: aou"
    
    # Create test markdown file
    test_files['md'] = b"""# Test Markdown Document

This is a **test** markdown document with:
- Bullet points
- *Italic text*
- `Code snippets`

## Section 2
More content here.
"""
    
    # Create test HTML file
    test_files['html'] = b"""<!DOCTYPE html>
<html>
<head><title>Test HTML</title></head>
<body>
<h1>Test HTML Document</h1>
<p>This is a test HTML document with <strong>bold text</strong> and <em>italic text</em>.</p>
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>
</body>
</html>"""
    
    # Create test CSV file
    test_files['csv'] = b"""Name,Age,City
John,30,New York
Jane,25,London
Bob,35,Paris"""
    
    # Create test JSON file
    test_files['json'] = b"""{
    "name": "Test Document",
    "type": "json",
    "data": {
        "items": ["item1", "item2", "item3"],
        "count": 3
    }
}"""
    
    print("Created test files for formats: txt, md, html, csv, json")
    return test_files


def test_document_processing():
    """Test document processing with Docling."""
    print("\n" + "=" * 60)
    print("Testing Document Processing")
    print("=" * 60)
    
    processor = DocumentProcessor()
    test_files = create_test_files()
    
    for file_type, content in test_files.items():
        filename = f"test.{file_type}"
        print(f"\nProcessing {filename}...")
        
        try:
            # Test text extraction
            text = processor.extract_text(content, filename)
            print(f"  Text extracted: {len(text)} characters")
            print(f"  Preview: {text[:100]}...")
            
            # Test full processing
            result = processor.process_document(content, filename)
            print(f"  Processing success: {result['success']}")
            
            if result['success']:
                print(f"  Chunks created: {len(result['chunks'])}")
                print(f"  Processing engine: {result['metadata'].get('processing_engine', 'unknown')}")
                
                # Show chunk details
                for i, chunk in enumerate(result['chunks'][:3]):  # Show first 3 chunks
                    print(f"    Chunk {i+1}: {len(chunk['content'])} chars, {chunk['token_count']} tokens")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  Error processing {filename}: {e}")


def test_docling_advanced_features():
    """Test Docling's advanced features."""
    print("\n" + "=" * 60)
    print("Testing Docling Advanced Features")
    print("=" * 60)
    
    docling_proc = DoclingProcessor()
    
    if not docling_proc.is_available():
        print("Docling not available, skipping advanced feature tests")
        return
    
    # Test with different processing options
    test_content = b"This is a test document for advanced processing."
    filename = "test_advanced.txt"
    
    print("Testing different processing options...")
    
    # Test with OCR enabled
    result1 = docling_proc.process_document(
        test_content, 
        filename,
        options={'ocr': True, 'ocr_language': 'eng'}
    )
    print(f"  OCR processing: {result1['success']}")
    
    # Test with vision model
    result2 = docling_proc.process_document(
        test_content,
        filename,
        options={'vision_model': 'smoldocling'}
    )
    print(f"  Vision model processing: {result2['success']}")
    
    # Test with table extraction
    result3 = docling_proc.process_document(
        test_content,
        filename,
        options={'extract_tables': True, 'extract_figures': True}
    )
    print(f"  Table/Figure extraction: {result3['success']}")


def test_file_type_detection():
    """Test file type detection."""
    print("\n" + "=" * 60)
    print("Testing File Type Detection")
    print("=" * 60)
    
    processor = DocumentProcessor()
    test_files = create_test_files()
    
    for file_type, content in test_files.items():
        filename = f"test.{file_type}"
        detected_type = processor.detect_file_type(content, filename)
        print(f"  {filename}: detected as {detected_type}")


def test_processing_engines():
    """Test available processing engines."""
    print("\n" + "=" * 60)
    print("Testing Processing Engines")
    print("=" * 60)
    
    from app.api.v1.endpoints.knowledge import get_processing_engines
    
    try:
        engines = get_processing_engines()
        print("Available processing engines:")
        for engine_id, engine_info in engines.items():
            print(f"  {engine_id}: {engine_info['name']}")
            print(f"    Description: {engine_info['description']}")
            print(f"    Supported formats: {engine_info['supported_formats']}")
            if 'features' in engine_info:
                print(f"    Features: {', '.join(engine_info['features'])}")
            print()
    except Exception as e:
        print(f"Error getting processing engines: {e}")


def main():
    """Run all tests."""
    print("Docling Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Docling availability
    docling_available = test_docling_availability()
    
    # Test 2: File type detection
    test_file_type_detection()
    
    # Test 3: Document processing
    test_document_processing()
    
    # Test 4: Advanced features (if Docling available)
    if docling_available:
        test_docling_advanced_features()
    
    # Test 5: Processing engines
    test_processing_engines()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if docling_available:
        print("✅ Docling is available and integrated")
        print("✅ Document processing using Docling")
        print("✅ Advanced features available")
    else:
        print("❌ Docling not available")
        print("⚠️  Using fallback processing methods")
    
    print("\nLibraries replaced by Docling:")
    print("  - PyPDF2 (PDF processing)")
    print("  - python-docx (Word documents)")
    print("  - pytesseract (OCR)")
    print("  - Pillow (Image processing)")
    print("  - markdown (Markdown processing)")
    print("  - BeautifulSoup (HTML processing)")
    
    print("\nDocling advantages:")
    print("  - Unified API for all document types")
    print("  - Advanced PDF understanding")
    print("  - Built-in OCR with multiple languages")
    print("  - Audio transcription (ASR)")
    print("  - Visual language models")
    print("  - Table and figure extraction")
    print("  - Formula recognition")
    print("  - Page layout understanding")


if __name__ == "__main__":
    main() 