#!/usr/bin/env python3
"""
Simple test script for Docling integration.

This script tests basic Docling functionality without depending on
the full application configuration.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_docling_import():
    """Test if Docling can be imported."""
    print("=" * 60)
    print("Testing Docling Import")
    print("=" * 60)
    
    try:
        from docling import DocumentConverter
        from docling.document import DoclingDocument
        print("✅ Docling imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Docling: {e}")
        return False


def test_docling_basic_functionality():
    """Test basic Docling functionality."""
    print("\n" + "=" * 60)
    print("Testing Basic Docling Functionality")
    print("=" * 60)
    
    try:
        from docling import DocumentConverter
        
        # Create converter
        converter = DocumentConverter()
        print("✅ DocumentConverter created successfully")
        
        # Test with a simple text file
        test_content = b"This is a test document for Docling processing."
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Process document
            doc = converter.convert(temp_file_path)
            print("✅ Document processing successful")
            
            # Check if document has text
            if hasattr(doc, 'text') and doc.text:
                print(f"✅ Text extracted: {len(doc.text)} characters")
                print(f"   Preview: {doc.text[:100]}...")
            else:
                print("⚠️  No text extracted from document")
            
            # Check document properties
            print(f"✅ Document type: {type(doc).__name__}")
            
            return True
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ Error testing Docling functionality: {e}")
        return False


def test_docling_formats():
    """Test Docling with different formats."""
    print("\n" + "=" * 60)
    print("Testing Docling with Different Formats")
    print("=" * 60)
    
    try:
        from docling import DocumentConverter
        
        converter = DocumentConverter()
        
        # Test formats
        test_formats = {
            'txt': b"This is a plain text file.\nWith multiple lines.\nAnd some content.",
            'md': b"""# Test Markdown

This is a **test** markdown document with:
- Bullet points
- *Italic text*
- `Code snippets`

## Section 2
More content here.
""",
            'html': b"""<!DOCTYPE html>
<html>
<head><title>Test HTML</title></head>
<body>
<h1>Test HTML Document</h1>
<p>This is a test HTML document with <strong>bold text</strong>.</p>
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>
</body>
</html>""",
            'csv': b"""Name,Age,City
John,30,New York
Jane,25,London
Bob,35,Paris""",
            'json': b"""{
    "name": "Test Document",
    "type": "json",
    "data": {
        "items": ["item1", "item2"],
        "count": 2
    }
}"""
        }
        
        results = {}
        
        for format_name, content in test_formats.items():
            print(f"\nTesting {format_name} format...")
            
            with tempfile.NamedTemporaryFile(mode='wb', suffix=f'.{format_name}', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Process document
                doc = converter.convert(temp_file_path)
                
                if hasattr(doc, 'text') and doc.text:
                    print(f"  ✅ Success: {len(doc.text)} characters extracted")
                    results[format_name] = True
                else:
                    print(f"  ⚠️  No text extracted")
                    results[format_name] = False
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results[format_name] = False
            finally:
                os.unlink(temp_file_path)
        
        # Summary
        print(f"\nFormat test summary:")
        successful = sum(results.values())
        total = len(results)
        print(f"  {successful}/{total} formats processed successfully")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ Error testing formats: {e}")
        return False


def test_docling_advanced_features():
    """Test Docling's advanced features."""
    print("\n" + "=" * 60)
    print("Testing Docling Advanced Features")
    print("=" * 60)
    
    try:
        from docling import DocumentConverter
        
        converter = DocumentConverter()
        
        # Test with different options
        test_content = b"This is a test document for advanced processing."
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Test with OCR enabled (for text files, this should work normally)
            print("Testing with OCR enabled...")
            doc1 = converter.convert(temp_file_path, ocr=True)
            print("  ✅ OCR processing completed")
            
            # Test with different options
            print("Testing with various options...")
            doc2 = converter.convert(
                temp_file_path,
                extract_tables=True,
                extract_figures=True,
                reading_order=True
            )
            print("  ✅ Advanced options processing completed")
            
            return True
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ Error testing advanced features: {e}")
        return False


def main():
    """Run all tests."""
    print("Docling Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Import
    import_success = test_docling_import()
    
    if not import_success:
        print("\n❌ Docling import failed. Cannot continue tests.")
        return
    
    # Test 2: Basic functionality
    basic_success = test_docling_basic_functionality()
    
    # Test 3: Different formats
    format_success = test_docling_formats()
    
    # Test 4: Advanced features
    advanced_success = test_docling_advanced_features()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    print(f"✅ Import: {'Passed' if import_success else 'Failed'}")
    print(f"✅ Basic Functionality: {'Passed' if basic_success else 'Failed'}")
    print(f"✅ Format Support: {'Passed' if format_success else 'Failed'}")
    print(f"✅ Advanced Features: {'Passed' if advanced_success else 'Failed'}")
    
    overall_success = import_success and basic_success and format_success and advanced_success
    
    if overall_success:
        print("\n🎉 All tests passed! Docling is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\nLibraries that can be replaced by Docling:")
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