#!/usr/bin/env python3
"""
Fix Import Issues Script
========================

This script removes local imports that are already imported at the top of the file.
"""

import re
import sys
from pathlib import Path


def fix_imports_in_file(file_path: str) -> None:
    """Fix import issues in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Get all imports at the top of the file
    top_imports = set()
    lines = content.split('\n')
    
    for line in lines:
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            # Extract module name
            if line.strip().startswith('import '):
                module = line.strip()[7:].split()[0]
                top_imports.add(module)
            elif line.strip().startswith('from '):
                parts = line.strip()[5:].split(' import ')
                if len(parts) == 2:
                    module = parts[0]
                    items = parts[1].split(', ')
                    for item in items:
                        top_imports.add(f"{module}.{item.strip()}")
    
    # Remove local imports that are already at the top
    new_lines = []
    skip_next_empty = False
    
    for line in lines:
        # Skip import lines that are already at the top
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            if 'app.core.database' in line or 'app.core.security' in line or 'app.models.user' in line:
                skip_next_empty = True
                continue
            elif 'import secrets' in line or 'import string' in line:
                skip_next_empty = True
                continue
        
        # Skip empty line after removed import
        if skip_next_empty and line.strip() == '':
            skip_next_empty = False
            continue
        
        skip_next_empty = False
        new_lines.append(line)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Fixed imports in {file_path}")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        fix_imports_in_file(file_path)
    else:
        print("Usage: python scripts/fix_imports.py <file_path>")


if __name__ == "__main__":
    main()