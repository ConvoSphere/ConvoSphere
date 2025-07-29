#!/usr/bin/env python3
"""
Test runner that patches the magic module to avoid libmagic dependency issues.
"""

import sys
import os
from unittest.mock import MagicMock

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the magic module before any imports
mock_magic = MagicMock()
mock_magic.Magic = MagicMock()
mock_magic.from_file = MagicMock(return_value='application/pdf')
mock_magic.from_buffer = MagicMock(return_value='application/pdf')

sys.modules['magic'] = mock_magic

# Now we can import and run tests
if __name__ == "__main__":
    import pytest
    
    # Run the tests
    test_args = [
        "unit/backend/",
        "-v",
        "--tb=short"
    ]
    
    exit_code = pytest.main(test_args)
    sys.exit(exit_code)