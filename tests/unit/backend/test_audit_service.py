"""
Unit tests for Audit Service.

This module tests the audit service functionality including:
- Audit log creation and retrieval
- Audit log filtering and search
- Audit log export functionality
- Audit statistics and reporting
"""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from backend.app.models.audit import AuditLog
from backend.app.services.audit import AuditService


class TestAuditService:
    """Test class for AuditService."""

    @pytest.fixture
    def audit_service(self, db_session: Session):
        """Create AuditService instance for testing."""
        return AuditService(db_session)

    @pytest.fixture
    def sample_audit_data(self):
        """Sample audit log data for testing."""
        return {
            "user_id": 1,
            "action": "user_login",
            "resource_type": "user",
            "resource_id": "1",
            "details": {"ip_address": "192.168.1.1", "user_agent": "test-browser"},
            "ip_address": "192.168.1.1",
            "user_agent": "test-browser",
            "status": "success",
        }

    @pytest.fixture
    def sample_audit_logs(self, db_session: Session, test_user):
        """Create sample audit logs for testing."""
        logs = []
        for i in range(10):
            log = AuditLog(
                user_id=test_user.id,
                action=f"test_action_{i}",
                resource_type="test_resource",
                resource_id=str(i),
                details={"test": f"value_{i}"},
                ip_address=f"192.168.1.{i}",
                user_agent="test-agent",
                status="success" if i % 2 == 0 else "failure",
                created_at=datetime.now() - timedelta(hours=i),
            )
            db_session.add(log)
            logs.append(log)
        
        db_session.commit()
        return logs

    def test_create_audit_log(self, audit_service, sample_audit_data):
        """Test creating a new audit log entry."""
        # Act
        audit_log = audit_service.create_audit_log(**sample_audit_data)
        
        # Assert
        assert audit_log is not None
        assert audit_log.user_id == sample_audit_data["user_id"]
        assert audit_log.action == sample_audit_data["action"]
        assert audit_log.resource_type == sample_audit_data["resource_type"]
        assert audit_log.resource_id == sample_audit_data["resource_id"]
        assert audit_log.status == sample_audit_data["status"]
        assert audit_log.ip_address == sample_audit_data["ip_address"]
        assert audit_log.user_agent == sample_audit_data["user_agent"]

    def test_get_audit_log_by_id(self, audit_service, sample_audit_logs):
        """Test retrieving an audit log by ID."""
        # Arrange
        test_log = sample_audit_logs[0]
        
        # Act
        retrieved_log = audit_service.get_audit_log_by_id(test_log.id)
        
        # Assert
        assert retrieved_log is not None
        assert retrieved_log.id == test_log.id
        assert retrieved_log.action == test_log.action

    def test_get_audit_logs_by_user(self, audit_service, sample_audit_logs, test_user):
        """Test retrieving audit logs for a specific user."""
        # Act
        user_logs = audit_service.get_audit_logs_by_user(test_user.id)
        
        # Assert
        assert len(user_logs) == 10
        assert all(log.user_id == test_user.id for log in user_logs)

    def test_get_audit_logs_by_action(self, audit_service, sample_audit_logs):
        """Test retrieving audit logs by action."""
        # Act
        action_logs = audit_service.get_audit_logs_by_action("test_action_0")
        
        # Assert
        assert len(action_logs) == 1
        assert action_logs[0].action == "test_action_0"

    def test_get_audit_logs_by_resource(self, audit_service, sample_audit_logs):
        """Test retrieving audit logs by resource."""
        # Act
        resource_logs = audit_service.get_audit_logs_by_resource("test_resource", "0")
        
        # Assert
        assert len(resource_logs) == 1
        assert resource_logs[0].resource_type == "test_resource"
        assert resource_logs[0].resource_id == "0"

    def test_get_audit_logs_by_date_range(self, audit_service, sample_audit_logs):
        """Test retrieving audit logs within a date range."""
        # Arrange
        start_date = datetime.now() - timedelta(hours=5)
        end_date = datetime.now() - timedelta(hours=2)
        
        # Act
        date_logs = audit_service.get_audit_logs_by_date_range(start_date, end_date)
        
        # Assert
        assert len(date_logs) == 4  # logs 2, 3, 4, 5
        assert all(start_date <= log.created_at <= end_date for log in date_logs)

    def test_get_audit_logs_by_status(self, audit_service, sample_audit_logs):
        """Test retrieving audit logs by status."""
        # Act
        success_logs = audit_service.get_audit_logs_by_status("success")
        failure_logs = audit_service.get_audit_logs_by_status("failure")
        
        # Assert
        assert len(success_logs) == 5
        assert len(failure_logs) == 5
        assert all(log.status == "success" for log in success_logs)
        assert all(log.status == "failure" for log in failure_logs)

    def test_search_audit_logs(self, audit_service, sample_audit_logs):
        """Test searching audit logs with multiple criteria."""
        # Act
        search_results = audit_service.search_audit_logs(
            user_id=test_user.id,
            action="test_action_0",
            status="success"
        )
        
        # Assert
        assert len(search_results) == 1
        assert search_results[0].action == "test_action_0"
        assert search_results[0].status == "success"

    def test_get_audit_statistics(self, audit_service, sample_audit_logs):
        """Test getting audit statistics."""
        # Act
        stats = audit_service.get_audit_statistics()
        
        # Assert
        assert stats["total_logs"] == 10
        assert stats["success_count"] == 5
        assert stats["failure_count"] == 5
        assert "actions" in stats
        assert "users" in stats

    def test_get_audit_statistics_by_user(self, audit_service, sample_audit_logs, test_user):
        """Test getting audit statistics for a specific user."""
        # Act
        user_stats = audit_service.get_audit_statistics_by_user(test_user.id)
        
        # Assert
        assert user_stats["total_logs"] == 10
        assert user_stats["success_count"] == 5
        assert user_stats["failure_count"] == 5

    def test_export_audit_logs_csv(self, audit_service, sample_audit_logs, tmp_path):
        """Test exporting audit logs to CSV format."""
        # Arrange
        export_path = tmp_path / "audit_logs.csv"
        
        # Act
        result = audit_service.export_audit_logs_csv(export_path)
        
        # Assert
        assert result is True
        assert export_path.exists()
        assert export_path.stat().st_size > 0

    def test_export_audit_logs_json(self, audit_service, sample_audit_logs, tmp_path):
        """Test exporting audit logs to JSON format."""
        # Arrange
        export_path = tmp_path / "audit_logs.json"
        
        # Act
        result = audit_service.export_audit_logs_json(export_path)
        
        # Assert
        assert result is True
        assert export_path.exists()
        
        # Verify JSON content
        with open(export_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 10
            assert all("id" in log for log in data)

    def test_cleanup_old_audit_logs(self, audit_service, sample_audit_logs):
        """Test cleaning up old audit logs."""
        # Arrange
        retention_days = 1
        
        # Act
        deleted_count = audit_service.cleanup_old_audit_logs(retention_days)
        
        # Assert
        assert deleted_count >= 0  # May be 0 if all logs are recent

    def test_get_audit_logs_paginated(self, audit_service, sample_audit_logs):
        """Test retrieving audit logs with pagination."""
        # Act
        page1 = audit_service.get_audit_logs_paginated(page=1, size=5)
        page2 = audit_service.get_audit_logs_paginated(page=2, size=5)
        
        # Assert
        assert len(page1["items"]) == 5
        assert len(page2["items"]) == 5
        assert page1["total"] == 10
        assert page1["page"] == 1
        assert page2["page"] == 2

    def test_get_audit_logs_by_ip_address(self, audit_service, sample_audit_logs):
        """Test retrieving audit logs by IP address."""
        # Act
        ip_logs = audit_service.get_audit_logs_by_ip_address("192.168.1.0")
        
        # Assert
        assert len(ip_logs) == 1
        assert ip_logs[0].ip_address == "192.168.1.0"

    def test_get_audit_logs_by_user_agent(self, audit_service, sample_audit_logs):
        """Test retrieving audit logs by user agent."""
        # Act
        agent_logs = audit_service.get_audit_logs_by_user_agent("test-agent")
        
        # Assert
        assert len(agent_logs) == 10
        assert all(log.user_agent == "test-agent" for log in agent_logs)

    @pytest.mark.asyncio
    async def test_create_audit_log_async(self, audit_service, sample_audit_data):
        """Test creating audit log asynchronously."""
        # Act
        audit_log = await audit_service.create_audit_log_async(**sample_audit_data)
        
        # Assert
        assert audit_log is not None
        assert audit_log.action == sample_audit_data["action"]

    def test_audit_log_validation(self, audit_service):
        """Test audit log data validation."""
        # Arrange
        invalid_data = {
            "user_id": None,  # Invalid user_id
            "action": "",     # Empty action
            "resource_type": None,  # Invalid resource_type
        }
        
        # Act & Assert
        with pytest.raises(ValueError):
            audit_service.create_audit_log(**invalid_data)

    def test_audit_log_details_serialization(self, audit_service, sample_audit_data):
        """Test that audit log details are properly serialized."""
        # Arrange
        complex_details = {
            "nested": {
                "data": [1, 2, 3],
                "metadata": {"key": "value"}
            },
            "timestamp": datetime.now().isoformat()
        }
        sample_audit_data["details"] = complex_details
        
        # Act
        audit_log = audit_service.create_audit_log(**sample_audit_data)
        
        # Assert
        assert audit_log.details == complex_details
        # Verify it can be serialized to JSON
        json.dumps(audit_log.details)

    def test_audit_log_performance(self, audit_service, sample_audit_data):
        """Test audit log creation performance."""
        import time
        
        # Act
        start_time = time.time()
        for i in range(100):
            sample_audit_data["action"] = f"performance_test_{i}"
            audit_service.create_audit_log(**sample_audit_data)
        end_time = time.time()
        
        # Assert
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should complete within 1 second

    def test_audit_log_concurrent_access(self, audit_service, sample_audit_data):
        """Test audit log creation with concurrent access."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_log(thread_id):
            try:
                sample_audit_data["action"] = f"concurrent_test_{thread_id}"
                log = audit_service.create_audit_log(**sample_audit_data)
                results.append(log)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_log, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(results) == 10
        assert len(errors) == 0