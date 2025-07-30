"""
Unit tests for Audit Service.

This module tests the audit service functionality including:
- Audit log creation and retrieval
- Audit log filtering and search
- Audit log export functionality
- Audit statistics and reporting
"""

import json
from datetime import UTC, datetime, timedelta

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
                created_at=datetime.now(UTC) - timedelta(hours=i),
            )
            db_session.add(log)
            logs.append(log)

        db_session.commit()
        return logs

    # =============================================================================
    # FAST TESTS - Basic audit operations
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_audit_log(self, audit_service, sample_audit_data):
        """Fast test for creating a new audit log entry."""
        audit_log = audit_service.create_audit_log(**sample_audit_data)

        assert audit_log is not None
        assert audit_log.user_id == sample_audit_data["user_id"]
        assert audit_log.action == sample_audit_data["action"]
        assert audit_log.resource_type == sample_audit_data["resource_type"]
        assert audit_log.resource_id == sample_audit_data["resource_id"]
        assert audit_log.status == sample_audit_data["status"]

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_log_by_id(self, audit_service, sample_audit_logs):
        """Fast test for retrieving an audit log by ID."""
        test_log = sample_audit_logs[0]

        retrieved_log = audit_service.get_audit_log_by_id(test_log.id)

        assert retrieved_log is not None
        assert retrieved_log.id == test_log.id
        assert retrieved_log.action == test_log.action

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_by_user(self, audit_service, sample_audit_logs, test_user):
        """Fast test for retrieving audit logs for a specific user."""
        user_logs = audit_service.get_audit_logs_by_user(test_user.id)

        assert len(user_logs) == 10
        assert all(log.user_id == test_user.id for log in user_logs)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_by_action(self, audit_service, sample_audit_logs):
        """Fast test for retrieving audit logs by action."""
        action_logs = audit_service.get_audit_logs_by_action("test_action_0")

        assert len(action_logs) == 1
        assert action_logs[0].action == "test_action_0"

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced audit operations and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_by_resource(self, audit_service, sample_audit_logs):
        """Comprehensive test for retrieving audit logs by resource."""
        resource_logs = audit_service.get_audit_logs_by_resource("test_resource", "0")

        assert len(resource_logs) == 1
        assert resource_logs[0].resource_type == "test_resource"
        assert resource_logs[0].resource_id == "0"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_by_date_range(self, audit_service, sample_audit_logs):
        """Comprehensive test for retrieving audit logs by date range."""
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(hours=5)

        date_logs = audit_service.get_audit_logs_by_date_range(start_date, end_date)

        assert len(date_logs) > 0
        assert all(start_date <= log.created_at <= end_date for log in date_logs)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_by_status(self, audit_service, sample_audit_logs):
        """Comprehensive test for retrieving audit logs by status."""
        success_logs = audit_service.get_audit_logs_by_status("success")
        failure_logs = audit_service.get_audit_logs_by_status("failure")

        assert len(success_logs) == 5
        assert len(failure_logs) == 5
        assert all(log.status == "success" for log in success_logs)
        assert all(log.status == "failure" for log in failure_logs)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_search_audit_logs(self, audit_service, sample_audit_logs):
        """Comprehensive test for searching audit logs."""
        search_results = audit_service.search_audit_logs("test_action")

        assert len(search_results) == 10
        assert all("test_action" in log.action for log in search_results)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_statistics(self, audit_service, sample_audit_logs):
        """Comprehensive test for getting audit statistics."""
        stats = audit_service.get_audit_statistics()

        assert stats is not None
        assert "total_logs" in stats
        assert "success_count" in stats
        assert "failure_count" in stats
        assert stats["total_logs"] == 10

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_statistics_by_user(self, audit_service, sample_audit_logs, test_user):
        """Comprehensive test for getting audit statistics by user."""
        user_stats = audit_service.get_audit_statistics_by_user(test_user.id)

        assert user_stats is not None
        assert user_stats["user_id"] == test_user.id
        assert user_stats["total_logs"] == 10

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_export_audit_logs_csv(self, audit_service, sample_audit_logs, tmp_path):
        """Comprehensive test for exporting audit logs to CSV."""
        csv_file = tmp_path / "audit_logs.csv"
        
        result = audit_service.export_audit_logs_csv(str(csv_file))

        assert result is True
        assert csv_file.exists()
        assert csv_file.stat().st_size > 0

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_export_audit_logs_json(self, audit_service, sample_audit_logs, tmp_path):
        """Comprehensive test for exporting audit logs to JSON."""
        json_file = tmp_path / "audit_logs.json"
        
        result = audit_service.export_audit_logs_json(str(json_file))

        assert result is True
        assert json_file.exists()
        
        with open(json_file, 'r') as f:
            data = json.load(f)
            assert len(data) == 10

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_cleanup_old_audit_logs(self, audit_service, sample_audit_logs):
        """Comprehensive test for cleaning up old audit logs."""
        cutoff_date = datetime.now(UTC) - timedelta(hours=5)
        
        deleted_count = audit_service.cleanup_old_audit_logs(cutoff_date)

        assert deleted_count >= 0
        remaining_logs = audit_service.get_audit_logs_by_date_range(
            cutoff_date, datetime.now(UTC)
        )
        assert len(remaining_logs) == 10 - deleted_count

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_paginated(self, audit_service, sample_audit_logs):
        """Comprehensive test for paginated audit log retrieval."""
        page1 = audit_service.get_audit_logs_paginated(page=1, page_size=5)
        page2 = audit_service.get_audit_logs_paginated(page=2, page_size=5)

        assert len(page1) == 5
        assert len(page2) == 5
        assert page1 != page2

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_by_ip_address(self, audit_service, sample_audit_logs):
        """Comprehensive test for retrieving audit logs by IP address."""
        ip_logs = audit_service.get_audit_logs_by_ip_address("192.168.1.0")

        assert len(ip_logs) == 1
        assert ip_logs[0].ip_address == "192.168.1.0"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_audit_logs_by_user_agent(self, audit_service, sample_audit_logs):
        """Comprehensive test for retrieving audit logs by user agent."""
        agent_logs = audit_service.get_audit_logs_by_user_agent("test-agent")

        assert len(agent_logs) == 10
        assert all(log.user_agent == "test-agent" for log in agent_logs)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_create_audit_log_async(self, audit_service, sample_audit_data):
        """Comprehensive test for async audit log creation."""
        audit_log = await audit_service.create_audit_log_async(**sample_audit_data)

        assert audit_log is not None
        assert audit_log.user_id == sample_audit_data["user_id"]
        assert audit_log.action == sample_audit_data["action"]

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_audit_log_validation(self, audit_service):
        """Comprehensive test for audit log validation."""
        invalid_data = {
            "user_id": None,  # Invalid user_id
            "action": "",     # Invalid action
            "resource_type": "user",
            "resource_id": "1",
        }

        with pytest.raises(ValueError):
            audit_service.create_audit_log(**invalid_data)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_audit_log_details_serialization(self, audit_service, sample_audit_data):
        """Comprehensive test for audit log details serialization."""
        complex_details = {
            "nested": {
                "array": [1, 2, 3],
                "object": {"key": "value"},
                "null": None,
                "boolean": True
            }
        }
        sample_audit_data["details"] = complex_details

        audit_log = audit_service.create_audit_log(**sample_audit_data)

        assert audit_log is not None
        assert audit_log.details == complex_details

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_audit_log_performance(self, audit_service, sample_audit_data):
        """Comprehensive test for audit log performance."""
        import time
        
        start_time = time.time()
        
        # Create multiple audit logs
        for i in range(100):
            sample_audit_data["action"] = f"performance_test_{i}"
            audit_service.create_audit_log(**sample_audit_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert execution_time < 5.0  # 5 seconds threshold

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_audit_log_concurrent_access(self, audit_service, sample_audit_data):
        """Comprehensive test for concurrent audit log access."""
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

        # Verify all logs were created successfully
        assert len(results) == 10
        assert len(errors) == 0