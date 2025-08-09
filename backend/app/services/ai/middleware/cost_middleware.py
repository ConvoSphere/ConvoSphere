"""Cost Middleware for AI Service."""

import time
from typing import Any, Dict, List, Optional

from ..types.ai_types import CostInfo


class CostMiddleware:
    """Cost tracking and usage monitoring middleware."""

    def __init__(self, cost_tracker=None):
        self.cost_tracker = cost_tracker

    async def track_cost(
        self,
        user_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        request_id: str,
    ) -> None:
        """Track cost for a request."""
        if not self.cost_tracker:
            return

        try:
            await self.cost_tracker.track_cost(
                user_id=user_id,
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                request_id=request_id,
            )
        except Exception as e:
            print(f"Failed to track cost: {str(e)}")

    async def track_streaming_cost(
        self,
        user_id: str,
        provider: str,
        model: str,
        estimated_tokens: int,
        cost: float,
        request_id: str,
    ) -> None:
        """Track cost for streaming requests."""
        if not self.cost_tracker:
            return

        try:
            await self.cost_tracker.track_cost(
                user_id=user_id,
                provider=provider,
                model=model,
                input_tokens=estimated_tokens,
                output_tokens=estimated_tokens,
                cost=cost,
                request_id=request_id,
            )
        except Exception as e:
            print(f"Failed to track streaming cost: {str(e)}")

    def estimate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for a request."""
        # Default cost estimates (per 1K tokens)
        cost_estimates = {
            "openai": {
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03},
                "text-embedding-ada-002": {"input": 0.0001, "output": 0.0},
            },
            "anthropic": {
                "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
                "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
                "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            },
        }

        provider_costs = cost_estimates.get(provider, {})
        model_costs = provider_costs.get(model, {"input": 0.001, "output": 0.002})

        input_cost = (input_tokens / 1000) * model_costs["input"]
        output_cost = (output_tokens / 1000) * model_costs["output"]

        return input_cost + output_cost

    def estimate_streaming_cost(
        self,
        provider: str,
        model: str,
        content_length: int,
    ) -> float:
        """Estimate cost for streaming requests."""
        # Rough estimation: 1 token ≈ 4 characters
        estimated_tokens = int(content_length / 4)
        return self.estimate_cost(provider, model, estimated_tokens, estimated_tokens)

    def get_cost_summary(self, user_id: str, days: int = 30) -> Dict[str, float]:
        """Get cost summary for a user."""
        if not self.cost_tracker:
            return {"total_cost": 0.0, "daily_average": 0.0}

        try:
            return self.cost_tracker.get_cost_summary(user_id, days)
        except Exception as e:
            print(f"Failed to get cost summary: {str(e)}")
            return {"total_cost": 0.0, "daily_average": 0.0}

    def get_daily_costs(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily cost breakdown."""
        if not self.cost_tracker:
            return []

        try:
            return self.cost_tracker.get_daily_costs(user_id, days)
        except Exception as e:
            print(f"Failed to get daily costs: {str(e)}")
            return []

    def get_model_usage_stats(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """Get model usage statistics."""
        if not self.cost_tracker:
            return {}

        try:
            return self.cost_tracker.get_model_usage_stats(user_id, days)
        except Exception as e:
            print(f"Failed to get model usage stats: {str(e)}")
            return {}

    def create_cost_info(
        self,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        model: str,
        provider: str,
    ) -> CostInfo:
        """Create a cost info object."""
        return CostInfo(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            model=model,
            provider=provider,
        )

    def calculate_token_count(self, text: str) -> int:
        """Calculate approximate token count for text."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4

    def get_provider_cost_limits(self, provider: str) -> Dict[str, Any]:
        """Get cost limits for a provider."""
        limits = {
            "openai": {
                "daily_limit": 100.0,  # $100 per day
                "monthly_limit": 2000.0,  # $2000 per month
                "rate_limit": 3000,  # requests per minute
            },
            "anthropic": {
                "daily_limit": 50.0,  # $50 per day
                "monthly_limit": 1000.0,  # $1000 per month
                "rate_limit": 1000,  # requests per minute
            },
        }
        return limits.get(provider, {})

    def check_cost_limits(
        self, user_id: str, provider: str, estimated_cost: float
    ) -> Dict[str, Any]:
        """Check if request would exceed cost limits."""
        limits = self.get_provider_cost_limits(provider)
        
        # Get current daily cost
        daily_costs = self.get_daily_costs(user_id, 1)
        current_daily_cost = sum(cost.get("cost", 0) for cost in daily_costs)
        
        # Check daily limit
        daily_limit = limits.get("daily_limit", float("inf"))
        would_exceed_daily = (current_daily_cost + estimated_cost) > daily_limit
        
        return {
            "within_limits": not would_exceed_daily,
            "current_daily_cost": current_daily_cost,
            "daily_limit": daily_limit,
            "estimated_cost": estimated_cost,
            "would_exceed_daily": would_exceed_daily,
        }

    def log_cost_metrics(
        self,
        cost_info: CostInfo,
        processing_time: float,
        request_id: str,
    ) -> None:
        """Log cost metrics for monitoring."""
        metrics = {
            "request_id": request_id,
            "provider": cost_info.provider,
            "model": cost_info.model,
            "input_tokens": cost_info.input_tokens,
            "output_tokens": cost_info.output_tokens,
            "cost": cost_info.cost,
            "processing_time": processing_time,
            "cost_per_token": cost_info.cost / (cost_info.input_tokens + cost_info.output_tokens) if (cost_info.input_tokens + cost_info.output_tokens) > 0 else 0,
        }
        
        # TODO: Integrate with your logging/monitoring system
        print(f"Cost metrics: {metrics}")  # Placeholder