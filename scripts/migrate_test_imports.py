#!/usr/bin/env python3
"""
Script to update import paths in migrated test files.
"""

import re
from pathlib import Path


def update_imports_in_file(file_path):
    """Update import statements in a test file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Update common import patterns
    replacements = [
        # Update relative imports
        (r"from \.\.", "from backend"),
        (r"from \.", "from backend.app"),
        # Update specific imports that might be broken
        (r"from app\.", "from backend.app."),
        (r"import app\.", "import backend.app."),
    ]

    original_content = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated imports in {file_path}")


def migrate_test_imports():
    """Migrate all test files in the tests directory."""
    tests_dir = Path("tests")

    for test_file in tests_dir.rglob("*.py"):
        if test_file.name.startswith("test_"):
            update_imports_in_file(test_file)


if __name__ == "__main__":
    migrate_test_imports()
