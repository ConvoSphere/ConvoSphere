"""
Database monitoring functionality.

This module provides database performance monitoring including query
tracking, connection monitoring, and slow query detection.
"""

import time
from collections import defaultdict
from typing import Any

from loguru import logger
from sqlalchemy import event
from sqlalchemy.orm import Session


class DatabaseMonitor:
    """Monitors database performance and queries."""

    def __init__(self, db: Session):
        """Initialize database monitor."""
        self.db = db
        self.query_times: list[dict[str, Any]] = []
        self.slow_queries: list[dict[str, Any]] = []
        self.connection_metrics = {
            "total_queries": 0,
            "slow_queries": 0,
            "avg_query_time": 0.0,
            "max_query_time": 0.0,
            "min_query_time": float("inf"),
            "query_count_by_type": defaultdict(int),
        }
        self._setup_query_monitoring()

    def _setup_query_monitoring(self):
        """Setup SQLAlchemy event listeners for query monitoring."""
        try:

            @event.listens_for(self.db, "before_cursor_execute")
            def before_cursor_execute(
                conn, cursor, statement, parameters, context, executemany
            ):
                context._query_start_time = time.time()

            @event.listens_for(self.db, "after_cursor_execute")
            def after_cursor_execute(
                conn, cursor, statement, parameters, context, executemany
            ):
                query_time = time.time() - getattr(
                    context, "_query_start_time", time.time()
                )

                # Record query metrics
                query_info = {
                    "statement": statement,
                    "parameters": str(parameters)[:200] if parameters else None,
                    "execution_time": query_time,
                    "timestamp": time.time(),
                    "executemany": executemany,
                }

                self.query_times.append(query_info)

                # Update connection metrics
                self.connection_metrics["total_queries"] += 1
                self.connection_metrics["avg_query_time"] = (
                    self.connection_metrics["avg_query_time"]
                    * (self.connection_metrics["total_queries"] - 1)
                    + query_time
                ) / self.connection_metrics["total_queries"]
                self.connection_metrics["max_query_time"] = max(
                    self.connection_metrics["max_query_time"], query_time
                )
                self.connection_metrics["min_query_time"] = min(
                    self.connection_metrics["min_query_time"], query_time
                )

                # Detect slow queries (over 1 second)
                if query_time > 1.0:
                    self.connection_metrics["slow_queries"] += 1
                    self.slow_queries.append(query_info)

                    # Keep only last 100 slow queries
                    if len(self.slow_queries) > 100:
                        self.slow_queries.pop(0)

                # Categorize query type
                query_type = self._categorize_query(statement)
                self.connection_metrics["query_count_by_type"][query_type] += 1

                # Keep only last 1000 queries
                if len(self.query_times) > 1000:
                    self.query_times.pop(0)

        except Exception as e:
            logger.error(f"Failed to setup query monitoring: {e}")

    def get_database_metrics(self) -> dict[str, Any]:
        """Get current database metrics."""
        try:
            # Get current connection info
            connection_info = {
                "engine_name": str(self.db.bind.engine.name),
                "pool_size": self.db.bind.engine.pool.size(),
                "checked_in": self.db.bind.engine.pool.checkedin(),
                "checked_out": self.db.bind.engine.pool.checkedout(),
                "overflow": self.db.bind.engine.pool.overflow(),
                "invalid": self.db.bind.engine.pool.invalid(),
            }

            # Calculate additional metrics
            recent_queries = self.query_times[-100:] if self.query_times else []
            recent_avg_time = (
                sum(q["execution_time"] for q in recent_queries) / len(recent_queries)
                if recent_queries
                else 0.0
            )

            return {
                "connection": connection_info,
                "queries": {
                    "total_queries": self.connection_metrics["total_queries"],
                    "slow_queries": self.connection_metrics["slow_queries"],
                    "avg_query_time": self.connection_metrics["avg_query_time"],
                    "max_query_time": self.connection_metrics["max_query_time"],
                    "min_query_time": self.connection_metrics["min_query_time"],
                    "recent_avg_time": recent_avg_time,
                    "query_count_by_type": dict(
                        self.connection_metrics["query_count_by_type"]
                    ),
                },
                "performance": {
                    "slow_query_percentage": (
                        (
                            self.connection_metrics["slow_queries"]
                            / self.connection_metrics["total_queries"]
                            * 100
                        )
                        if self.connection_metrics["total_queries"] > 0
                        else 0.0
                    ),
                    "queries_per_minute": self._calculate_queries_per_minute(),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get database metrics: {e}")
            return {}

    def get_slow_queries(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent slow queries."""
        try:
            # Sort by execution time (slowest first) and return top N
            sorted_queries = sorted(
                self.slow_queries, key=lambda x: x["execution_time"], reverse=True
            )
            return sorted_queries[:limit]

        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return []

    def reset_metrics(self) -> None:
        """Reset all database metrics."""
        try:
            self.query_times.clear()
            self.slow_queries.clear()
            self.connection_metrics = {
                "total_queries": 0,
                "slow_queries": 0,
                "avg_query_time": 0.0,
                "max_query_time": 0.0,
                "min_query_time": float("inf"),
                "query_count_by_type": defaultdict(int),
            }
            logger.info("Database metrics reset")

        except Exception as e:
            logger.error(f"Failed to reset database metrics: {e}")

    def _categorize_query(self, statement: str) -> str:
        """Categorize SQL query by type."""
        try:
            statement_upper = statement.strip().upper()

            if statement_upper.startswith("SELECT"):
                return "SELECT"
            if statement_upper.startswith("INSERT"):
                return "INSERT"
            if statement_upper.startswith("UPDATE"):
                return "UPDATE"
            if statement_upper.startswith("DELETE"):
                return "DELETE"
            if statement_upper.startswith("CREATE"):
                return "CREATE"
            if statement_upper.startswith("ALTER"):
                return "ALTER"
            if statement_upper.startswith("DROP"):
                return "DROP"
            return "OTHER"

        except Exception:
            return "UNKNOWN"

    def _calculate_queries_per_minute(self) -> float:
        """Calculate queries per minute based on recent activity."""
        try:
            if not self.query_times:
                return 0.0

            # Get queries from last minute
            one_minute_ago = time.time() - 60
            recent_queries = [
                q for q in self.query_times if q["timestamp"] >= one_minute_ago
            ]

            return len(recent_queries)

        except Exception as e:
            logger.error(f"Failed to calculate queries per minute: {e}")
            return 0.0

    def get_query_statistics(self, time_window_minutes: int = 60) -> dict[str, Any]:
        """Get query statistics for a time window."""
        try:
            if not self.query_times:
                return {}

            # Calculate time window
            window_start = time.time() - (time_window_minutes * 60)

            # Filter queries in time window
            window_queries = [
                q for q in self.query_times if q["timestamp"] >= window_start
            ]

            if not window_queries:
                return {}

            # Calculate statistics
            execution_times = [q["execution_time"] for q in window_queries]

            return {
                "total_queries": len(window_queries),
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "slow_queries": len([t for t in execution_times if t > 1.0]),
                "queries_per_minute": len(window_queries) / time_window_minutes,
                "query_types": self._get_query_type_distribution(window_queries),
            }

        except Exception as e:
            logger.error(f"Failed to get query statistics: {e}")
            return {}

    def _get_query_type_distribution(
        self, queries: list[dict[str, Any]]
    ) -> dict[str, int]:
        """Get distribution of query types."""
        try:
            distribution = defaultdict(int)
            for query in queries:
                query_type = self._categorize_query(query["statement"])
                distribution[query_type] += 1
            return dict(distribution)

        except Exception as e:
            logger.error(f"Failed to get query type distribution: {e}")
            return {}
