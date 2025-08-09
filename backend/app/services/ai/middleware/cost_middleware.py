"""Cost Middleware for AI Service."""

from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional

from ..utils.cost_tracker import CostTracker
from ..types.ai_types import CostInfo


class CostMiddleware:
    """Cost tracking middleware for AI service."""

    def __init__(self, cost_tracker=None):
        """Initialize cost middleware with optional cost tracker."""
        self.cost_tracker = cost_tracker or CostTracker()

    def track_cost(
        self,
        user_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        conversation_id: Optional[str] = None,
    ) -> None:
        """Track cost for a request."""
        try:
            cost_info = CostInfo(
                model=model,
                tokens_used=input_tokens + output_tokens,
                cost_usd=cost_usd,
                timestamp=datetime.now(UTC),
                user_id=user_id,
                conversation_id=conversation_id,
            )
            
            self.cost_tracker.add_cost(cost_info)
            
        except Exception as e:
            print(f"Failed to track cost: {str(e)}")

    def track_streaming_cost(
        self,
        user_id: str,
        provider: str,
        model: str,
        total_tokens: int,
        cost_usd: float,
        conversation_id: Optional[str] = None,
    ) -> None:
        """Track cost for streaming requests."""
        try:
            cost_info = CostInfo(
                model=model,
                tokens_used=total_tokens,
                cost_usd=cost_usd,
                timestamp=datetime.now(UTC),
                user_id=user_id,
                conversation_id=conversation_id,
            )
            
            self.cost_tracker.add_cost(cost_info)
            
        except Exception as e:
            print(f"Failed to track streaming cost: {str(e)}")

    def estimate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for token usage."""
        try:
            # Get cost rates from provider manager (if available)
            # For now, use default rates
            cost_per_1k_input = self._get_cost_rate(model, "input")
            cost_per_1k_output = self._get_cost_rate(model, "output")
            
            input_cost = (input_tokens / 1000) * cost_per_1k_input
            output_cost = (output_tokens / 1000) * cost_per_1k_output
            
            return input_cost + output_cost
            
        except Exception as e:
            print(f"Failed to estimate cost: {str(e)}")
            return 0.0

    def _get_cost_rate(self, model: str, token_type: str) -> float:
        """Get cost rate for model and token type."""
        # Default cost rates (can be enhanced with provider-specific rates)
        if model.startswith("gpt-4"):
            return 0.03 if token_type == "input" else 0.06
        elif model.startswith("gpt-3.5"):
            return 0.0015 if token_type == "input" else 0.002
        elif model.startswith("claude-3-opus"):
            return 0.015 if token_type == "input" else 0.075
        elif model.startswith("claude-3-sonnet"):
            return 0.003 if token_type == "input" else 0.015
        elif model.startswith("claude-3-haiku"):
            return 0.00025 if token_type == "input" else 0.00125
        elif model.startswith("text-embedding"):
            return 0.0001 if token_type == "input" else 0.0
        else:
            # Default rates
            return 0.001 if token_type == "input" else 0.002

    def get_cost_summary(self, user_id: str, days: int = 30) -> Dict[str, float]:
        """Get cost summary for a user."""
        try:
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=days)
            
            # Get costs from cost tracker
            costs = self.cost_tracker.get_costs_by_user(user_id)
            
            # Filter by date range
            filtered_costs = [
                cost for cost in costs
                if start_date <= cost.timestamp <= end_date
            ]
            
            # Calculate summary
            total_cost = sum(cost.cost_usd for cost in filtered_costs)
            total_tokens = sum(cost.tokens_used for cost in filtered_costs)
            
            # Calculate daily average
            daily_cost = total_cost / days if days > 0 else 0.0
            
            return {
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "daily_cost": daily_cost,
                "monthly_cost": total_cost,
                "requests_count": len(filtered_costs),
            }
            
        except Exception as e:
            print(f"Failed to get cost summary: {str(e)}")
            return {
                "total_cost": 0.0,
                "total_tokens": 0,
                "daily_cost": 0.0,
                "monthly_cost": 0.0,
                "requests_count": 0,
            }

    def get_daily_costs(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily cost breakdown."""
        try:
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=days)
            
            # Get costs from cost tracker
            costs = self.cost_tracker.get_costs_by_user(user_id)
            
            # Filter by date range
            filtered_costs = [
                cost for cost in costs
                if start_date <= cost.timestamp <= end_date
            ]
            
            # Group by date
            daily_costs = {}
            for cost in filtered_costs:
                date_key = cost.timestamp.date().isoformat()
                if date_key not in daily_costs:
                    daily_costs[date_key] = {
                        "date": date_key,
                        "cost": 0.0,
                        "tokens": 0,
                        "requests": 0,
                    }
                
                daily_costs[date_key]["cost"] += cost.cost_usd
                daily_costs[date_key]["tokens"] += cost.tokens_used
                daily_costs[date_key]["requests"] += 1
            
            # Convert to list and sort by date
            result = list(daily_costs.values())
            result.sort(key=lambda x: x["date"])
            
            return result
            
        except Exception as e:
            print(f"Failed to get daily costs: {str(e)}")
            return []

    def get_model_usage_stats(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """Get model usage statistics."""
        try:
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=days)
            
            # Get costs from cost tracker
            costs = self.cost_tracker.get_costs_by_user(user_id)
            
            # Filter by date range
            filtered_costs = [
                cost for cost in costs
                if start_date <= cost.timestamp <= end_date
            ]
            
            # Group by model
            model_stats = {}
            for cost in filtered_costs:
                model = cost.model
                if model not in model_stats:
                    model_stats[model] = {
                        "total_requests": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "avg_tokens_per_request": 0.0,
                        "avg_cost_per_request": 0.0,
                    }
                
                model_stats[model]["total_requests"] += 1
                model_stats[model]["total_tokens"] += cost.tokens_used
                model_stats[model]["total_cost"] += cost.cost_usd
            
            # Calculate averages
            for model, stats in model_stats.items():
                if stats["total_requests"] > 0:
                    stats["avg_tokens_per_request"] = stats["total_tokens"] / stats["total_requests"]
                    stats["avg_cost_per_request"] = stats["total_cost"] / stats["total_requests"]
            
            return model_stats
            
        except Exception as e:
            print(f"Failed to get model usage stats: {str(e)}")
            return {}

    def check_cost_limit(self, user_id: str, cost_limit: float) -> bool:
        """Check if user has exceeded cost limit."""
        try:
            # Get current month's cost
            cost_summary = self.get_cost_summary(user_id, days=30)
            current_cost = cost_summary.get("total_cost", 0.0)
            
            return current_cost < cost_limit
            
        except Exception as e:
            print(f"Failed to check cost limit: {str(e)}")
            return True  # Allow if check fails

    def get_cost_alerts(self, user_id: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Get cost alerts for user."""
        try:
            # Get current month's cost
            cost_summary = self.get_cost_summary(user_id, days=30)
            current_cost = cost_summary.get("total_cost", 0.0)
            
            alerts = []
            
            # Check if approaching limit (assuming limit is 1.0 for now)
            if current_cost > threshold:
                alerts.append({
                    "type": "cost_warning",
                    "message": f"Cost is approaching limit: ${current_cost:.2f}",
                    "severity": "warning",
                    "cost": current_cost,
                })
            
            # Check for unusual spending patterns
            daily_costs = self.get_daily_costs(user_id, days=7)
            if daily_costs:
                avg_daily_cost = sum(day["cost"] for day in daily_costs) / len(daily_costs)
                if avg_daily_cost > 0.1:  # More than $0.10 per day
                    alerts.append({
                        "type": "high_usage",
                        "message": f"High daily usage detected: ${avg_daily_cost:.2f}/day",
                        "severity": "info",
                        "avg_daily_cost": avg_daily_cost,
                    })
            
            return alerts
            
        except Exception as e:
            print(f"Failed to get cost alerts: {str(e)}")
            return []