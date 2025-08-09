"""Helper utilities for CLI commands."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional


def get_alembic_path() -> Optional[str]:
    """Get Alembic executable path."""
    return shutil.which("alembic")


def run_alembic_command(command: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run Alembic command."""
    if not cwd:
        cwd = Path(__file__).parent.parent.parent
    
    return subprocess.run(
        command,
        check=False,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def get_database_url() -> str:
    """Get database URL from environment."""
    return os.getenv("DATABASE_URL", "sqlite:///./test.db")


def get_backup_dir() -> str:
    """Get backup directory."""
    return os.getenv("BACKUP_DIR", "./backups")


def create_dummy_user():
    """Create a dummy user for admin operations."""
    class DummyUser:
        role = "super_admin"
        organization_id = None
        
        def has_permission(self, perm):
            return True
    
    return DummyUser()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def confirm_action(message: str) -> bool:
    """Confirm action with user."""
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ['y', 'yes']