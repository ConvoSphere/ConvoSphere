"""
Agent Performance Service.

This module provides agent performance monitoring and metrics
extracted from the MultiAgentManager for better modularity.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger
from pydantic import BaseModel

from backend.app.schemas.agent import AgentPerformanceMetrics


class PerformanceSnapshot(BaseModel):
    """Performance snapshot for analysis."""

    agent_id: str
    conversation_id: str
    timestamp: datetime
    response_time: float
    success_rate: float
    user_satisfaction: float
    tool_usage_count: int
    tokens_used: int
    error_count: int
    context_size: int = 0
    complexity_score: float = 0.0

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class PerformanceTrend(BaseModel):
    """Performance trend analysis."""

    agent_id: str
    time_period: str
    start_time: datetime
    end_time: datetime
    avg_response_time: float
    avg_success_rate: float
    avg_user_satisfaction: float
    total_interactions: int
    total_errors: int
    performance_score: float
    trend_direction: str  # "improving", "declining", "stable"

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class AgentPerformanceService:
    """Service for managing agent performance metrics."""

    def __init__(self):
        """Initialize the performance service."""
        self.performance_history: list[AgentPerformanceMetrics] = []
        self.performance_snapshots: list[PerformanceSnapshot] = []
        self.retention_days = 90  # Keep metrics for 90 days

    def record_performance(
        self,
        metrics: AgentPerformanceMetrics,
    ) -> None:
        """
        Record performance metrics.

        Args:
            metrics: Performance metrics to record
        """
        self.performance_history.append(metrics)

        # Create snapshot for analysis
        snapshot = PerformanceSnapshot(
            agent_id=metrics.agent_id,
            conversation_id=metrics.conversation_id,
            timestamp=metrics.created_at,
            response_time=metrics.response_time,
            success_rate=metrics.success_rate,
            user_satisfaction=metrics.user_satisfaction,
            tool_usage_count=metrics.tool_usage_count,
            tokens_used=metrics.tokens_used,
            error_count=metrics.error_count,
        )

        self.performance_snapshots.append(snapshot)

        # Cleanup old data
        self._cleanup_old_data()

        logger.debug(f"Recorded performance metrics for agent {metrics.agent_id}")

    def get_agent_performance(
        self,
        agent_id: str,
        conversation_id: str | None = None,
        time_period_hours: int | None = None,
        limit: int = 100,
    ) -> list[AgentPerformanceMetrics]:
        """
        Get performance metrics for an agent.

        Args:
            agent_id: Agent ID
            conversation_id: Optional conversation ID filter
            time_period_hours: Optional time period filter
            limit: Maximum number of results

        Returns:
            List[AgentPerformanceMetrics]: Performance metrics
        """
        metrics = self.performance_history.copy()

        # Filter by agent
        metrics = [m for m in metrics if m.agent_id == agent_id]

        # Filter by conversation if specified
        if conversation_id:
            metrics = [m for m in metrics if m.conversation_id == conversation_id]

        # Filter by time period if specified
        if time_period_hours:
            cutoff_time = datetime.now(UTC) - timedelta(hours=time_period_hours)
            metrics = [m for m in metrics if m.created_at >= cutoff_time]

        # Sort by timestamp (most recent first)
        metrics.sort(key=lambda x: x.created_at, reverse=True)

        return metrics[:limit]

    def get_agent_performance_summary(
        self,
        agent_id: str,
        time_period_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Get performance summary for an agent.

        Args:
            agent_id: Agent ID
            time_period_hours: Time period for summary

        Returns:
            dict: Performance summary
        """
        metrics = self.get_agent_performance(
            agent_id, time_period_hours=time_period_hours
        )

        if not metrics:
            return {
                "agent_id": agent_id,
                "time_period_hours": time_period_hours,
                "total_interactions": 0,
                "avg_response_time": 0.0,
                "avg_success_rate": 0.0,
                "avg_user_satisfaction": 0.0,
                "total_tokens_used": 0,
                "total_errors": 0,
                "performance_score": 0.0,
            }

        total_interactions = len(metrics)
        avg_response_time = sum(m.response_time for m in metrics) / total_interactions
        avg_success_rate = sum(m.success_rate for m in metrics) / total_interactions
        avg_user_satisfaction = sum(m.user_satisfaction for m in metrics) / total_interactions
        total_tokens_used = sum(m.tokens_used for m in metrics)
        total_errors = sum(m.error_count for m in metrics)

        # Calculate performance score (weighted average)
        performance_score = (
            (avg_success_rate * 0.4) +
            (avg_user_satisfaction / 5.0 * 100 * 0.3) +
            (max(0, 100 - avg_response_time * 10) * 0.2) +
            (max(0, 100 - total_errors * 5) * 0.1)
        )

        return {
            "agent_id": agent_id,
            "time_period_hours": time_period_hours,
            "total_interactions": total_interactions,
            "avg_response_time": round(avg_response_time, 3),
            "avg_success_rate": round(avg_success_rate, 2),
            "avg_user_satisfaction": round(avg_user_satisfaction, 2),
            "total_tokens_used": total_tokens_used,
            "total_errors": total_errors,
            "performance_score": round(performance_score, 2),
        }

    def get_performance_trend(
        self,
        agent_id: str,
        time_period_hours: int = 168,  # 1 week
        interval_hours: int = 24,  # Daily intervals
    ) -> list[PerformanceTrend]:
        """
        Get performance trends for an agent.

        Args:
            agent_id: Agent ID
            time_period_hours: Total time period
            interval_hours: Interval size for trend analysis

        Returns:
            List[PerformanceTrend]: Performance trends
        """
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(hours=time_period_hours)

        trends = []
        current_start = start_time

        while current_start < end_time:
            current_end = min(current_start + timedelta(hours=interval_hours), end_time)

            # Get metrics for this interval
            interval_metrics = [
                m for m in self.performance_history
                if m.agent_id == agent_id
                and current_start <= m.created_at < current_end
            ]

            if interval_metrics:
                avg_response_time = sum(m.response_time for m in interval_metrics) / len(interval_metrics)
                avg_success_rate = sum(m.success_rate for m in interval_metrics) / len(interval_metrics)
                avg_user_satisfaction = sum(m.user_satisfaction for m in interval_metrics) / len(interval_metrics)
                total_interactions = len(interval_metrics)
                total_errors = sum(m.error_count for m in interval_metrics)

                # Calculate performance score
                performance_score = (
                    (avg_success_rate * 0.4) +
                    (avg_user_satisfaction / 5.0 * 100 * 0.3) +
                    (max(0, 100 - avg_response_time * 10) * 0.2) +
                    (max(0, 100 - total_errors * 5) * 0.1)
                )

                trend = PerformanceTrend(
                    agent_id=agent_id,
                    time_period=f"{interval_hours}h",
                    start_time=current_start,
                    end_time=current_end,
                    avg_response_time=round(avg_response_time, 3),
                    avg_success_rate=round(avg_success_rate, 2),
                    avg_user_satisfaction=round(avg_user_satisfaction, 2),
                    total_interactions=total_interactions,
                    total_errors=total_errors,
                    performance_score=round(performance_score, 2),
                    trend_direction="stable",  # Will be calculated later
                )

                trends.append(trend)

            current_start = current_end

        # Calculate trend direction
        if len(trends) >= 2:
            for i in range(1, len(trends)):
                prev_score = trends[i - 1].performance_score
                curr_score = trends[i].performance_score
                
                if curr_score > prev_score + 5:
                    trends[i].trend_direction = "improving"
                elif curr_score < prev_score - 5:
                    trends[i].trend_direction = "declining"
                else:
                    trends[i].trend_direction = "stable"

        return trends

    def get_conversation_performance(
        self,
        conversation_id: str,
    ) -> dict[str, Any]:
        """
        Get performance metrics for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            dict: Conversation performance summary
        """
        conversation_metrics = [
            m for m in self.performance_history
            if m.conversation_id == conversation_id
        ]

        if not conversation_metrics:
            return {
                "conversation_id": conversation_id,
                "total_interactions": 0,
                "agents_involved": [],
                "performance_summary": {},
            }

        # Get unique agents
        agents_involved = list(set(m.agent_id for m in conversation_metrics))

        # Calculate overall metrics
        total_interactions = len(conversation_metrics)
        avg_response_time = sum(m.response_time for m in conversation_metrics) / total_interactions
        avg_success_rate = sum(m.success_rate for m in conversation_metrics) / total_interactions
        total_tokens_used = sum(m.tokens_used for m in conversation_metrics)
        total_errors = sum(m.error_count for m in conversation_metrics)

        # Get agent-specific metrics
        agent_performance = {}
        for agent_id in agents_involved:
            agent_metrics = [m for m in conversation_metrics if m.agent_id == agent_id]
            agent_performance[agent_id] = {
                "interactions": len(agent_metrics),
                "avg_response_time": sum(m.response_time for m in agent_metrics) / len(agent_metrics),
                "avg_success_rate": sum(m.success_rate for m in agent_metrics) / len(agent_metrics),
                "total_tokens_used": sum(m.tokens_used for m in agent_metrics),
                "total_errors": sum(m.error_count for m in agent_metrics),
            }

        return {
            "conversation_id": conversation_id,
            "total_interactions": total_interactions,
            "agents_involved": agents_involved,
            "performance_summary": {
                "avg_response_time": round(avg_response_time, 3),
                "avg_success_rate": round(avg_success_rate, 2),
                "total_tokens_used": total_tokens_used,
                "total_errors": total_errors,
            },
            "agent_performance": agent_performance,
        }

    def get_top_performing_agents(
        self,
        time_period_hours: int = 24,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get top performing agents.

        Args:
            time_period_hours: Time period for analysis
            limit: Maximum number of agents

        Returns:
            List[dict]: Top performing agents
        """
        cutoff_time = datetime.now(UTC) - timedelta(hours=time_period_hours)

        # Get all agents with metrics in time period
        agent_ids = set(
            m.agent_id for m in self.performance_history
            if m.created_at >= cutoff_time
        )

        agent_performances = []
        for agent_id in agent_ids:
            summary = self.get_agent_performance_summary(agent_id, time_period_hours)
            if summary["total_interactions"] > 0:
                agent_performances.append(summary)

        # Sort by performance score (descending)
        agent_performances.sort(key=lambda x: x["performance_score"], reverse=True)

        return agent_performances[:limit]

    def get_performance_alerts(
        self,
        threshold_response_time: float = 5.0,
        threshold_error_rate: float = 10.0,
        time_period_hours: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Get performance alerts for agents below thresholds.

        Args:
            threshold_response_time: Response time threshold in seconds
            threshold_error_rate: Error rate threshold in percentage
            time_period_hours: Time period for analysis

        Returns:
            List[dict]: Performance alerts
        """
        cutoff_time = datetime.now(UTC) - timedelta(hours=time_period_hours)

        recent_metrics = [
            m for m in self.performance_history
            if m.created_at >= cutoff_time
        ]

        # Group by agent
        agent_metrics = {}
        for metric in recent_metrics:
            if metric.agent_id not in agent_metrics:
                agent_metrics[metric.agent_id] = []
            agent_metrics[metric.agent_id].append(metric)

        alerts = []
        for agent_id, metrics in agent_metrics.items():
            avg_response_time = sum(m.response_time for m in metrics) / len(metrics)
            total_errors = sum(m.error_count for m in metrics)
            total_interactions = len(metrics)
            error_rate = (total_errors / total_interactions) * 100 if total_interactions > 0 else 0

            if avg_response_time > threshold_response_time or error_rate > threshold_error_rate:
                alerts.append({
                    "agent_id": agent_id,
                    "avg_response_time": round(avg_response_time, 3),
                    "error_rate": round(error_rate, 2),
                    "total_interactions": total_interactions,
                    "threshold_response_time": threshold_response_time,
                    "threshold_error_rate": threshold_error_rate,
                    "alert_type": "performance_degradation",
                })

        return alerts

    def _cleanup_old_data(self) -> None:
        """Clean up old performance data."""
        cutoff_time = datetime.now(UTC) - timedelta(days=self.retention_days)

        # Clean up performance history
        self.performance_history = [
            m for m in self.performance_history
            if m.created_at >= cutoff_time
        ]

        # Clean up snapshots
        self.performance_snapshots = [
            s for s in self.performance_snapshots
            if s.timestamp >= cutoff_time
        ]

        logger.debug(f"Cleaned up performance data older than {self.retention_days} days")

    def get_stats(self) -> dict[str, Any]:
        """
        Get performance service statistics.

        Returns:
            dict: Service statistics
        """
        total_metrics = len(self.performance_history)
        total_snapshots = len(self.performance_snapshots)

        # Get unique agents and conversations
        unique_agents = set(m.agent_id for m in self.performance_history)
        unique_conversations = set(m.conversation_id for m in self.performance_history)

        # Calculate overall averages
        if total_metrics > 0:
            avg_response_time = sum(m.response_time for m in self.performance_history) / total_metrics
            avg_success_rate = sum(m.success_rate for m in self.performance_history) / total_metrics
            avg_user_satisfaction = sum(m.user_satisfaction for m in self.performance_history) / total_metrics
            total_tokens_used = sum(m.tokens_used for m in self.performance_history)
            total_errors = sum(m.error_count for m in self.performance_history)
        else:
            avg_response_time = 0.0
            avg_success_rate = 0.0
            avg_user_satisfaction = 0.0
            total_tokens_used = 0
            total_errors = 0

        return {
            "total_metrics_recorded": total_metrics,
            "total_snapshots": total_snapshots,
            "unique_agents": len(unique_agents),
            "unique_conversations": len(unique_conversations),
            "avg_response_time": round(avg_response_time, 3),
            "avg_success_rate": round(avg_success_rate, 2),
            "avg_user_satisfaction": round(avg_user_satisfaction, 2),
            "total_tokens_used": total_tokens_used,
            "total_errors": total_errors,
            "retention_days": self.retention_days,
        }


# Global agent performance service instance
agent_performance_service = AgentPerformanceService()