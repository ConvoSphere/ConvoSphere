"""Output utilities for CLI commands."""

import sys


def print_success(message: str) -> None:
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"❌ {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print info message."""
    print(f"ℹ️  {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"⚠️  {message}")


def print_header(message: str) -> None:
    """Print header message."""
    print(f"\n{'=' * 50}")
    print(f"  {message}")
    print(f"{'=' * 50}\n")
