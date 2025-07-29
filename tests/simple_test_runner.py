#!/usr/bin/env python3
"""
Simple test runner that mocks external dependencies to run basic tests.
"""

import sys
import os
from unittest.mock import MagicMock, patch

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock external dependencies before any imports
mock_magic = MagicMock()
mock_magic.Magic = MagicMock()
mock_magic.from_file = MagicMock(return_value='application/pdf')
mock_magic.from_buffer = MagicMock(return_value='application/pdf')
sys.modules['magic'] = mock_magic

# Mock OpenTelemetry
mock_opentelemetry = MagicMock()
sys.modules['opentelemetry'] = mock_opentelemetry
sys.modules['opentelemetry.instrumentation.redis'] = MagicMock()
sys.modules['opentelemetry.instrumentation.httpx'] = MagicMock()

# Mock Weaviate
mock_weaviate = MagicMock()
sys.modules['weaviate'] = mock_weaviate

# Mock Redis
mock_redis = MagicMock()
sys.modules['redis'] = mock_redis

# Mock other external services
with patch('backend.app.services.weaviate_service.weaviate'), \
     patch('backend.app.core.weaviate_client.weaviate'), \
     patch('backend.app.core.redis_client.redis'), \
     patch('backend.app.core.opentelemetry_config.opentelemetry'):
    
    # Now we can import and run tests
    if __name__ == "__main__":
        import pytest
        
        # Run only simple tests that don't require external services
        test_args = [
            "unit/backend/test_health.py",
            "unit/backend/test_config.py", 
            "unit/backend/test_models.py",
            "unit/backend/test_utils.py",
            "-v",
            "--tb=short"
        ]
        
        exit_code = pytest.main(test_args)
        sys.exit(exit_code)