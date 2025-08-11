"""Compatibility module to expose FastAPI app under backend.app.main for tests.

This re-exports the application instance from the root-level backend/main.py.
"""
from ..main import app  # type: ignore