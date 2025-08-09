#!/usr/bin/env python3
"""
Simple script to run the backend application with correct Python path.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    from backend.app.core.config import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "run_backend:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )