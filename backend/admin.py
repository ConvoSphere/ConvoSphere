#!/usr/bin/env python3
"""
ChatAssistant Admin CLI

A comprehensive command-line interface for managing the ChatAssistant platform.
This tool provides database management, user administration, backup/restore,
monitoring, and development utilities.

Usage:
    python admin.py [COMMAND] [OPTIONS]

Examples:
    python admin.py db migrate
    python admin.py user create-admin
    python admin.py backup create
    python admin.py monitoring health
    python admin.py config show
"""

# Import and run the new CLI
from cli.main import main

if __name__ == "__main__":
    main()
