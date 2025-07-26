#!/usr/bin/env python3
"""
Script to fix import paths in service files.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import statements in a service file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update import patterns
    replacements = [
        # Update relative imports to absolute imports
        (r'from app\.', 'from backend.app.'),
        (r'import app\.', 'import backend.app.'),
    ]
    
    original_content = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed imports in {file_path}")

def fix_service_imports():
    """Fix imports in all service files."""
    services_dir = Path("backend/app/services")
    
    # Fix imports in all Python files in services directory
    for service_file in services_dir.rglob("*.py"):
        if service_file.name != "__init__.py":
            fix_imports_in_file(service_file)

if __name__ == "__main__":
    fix_service_imports()