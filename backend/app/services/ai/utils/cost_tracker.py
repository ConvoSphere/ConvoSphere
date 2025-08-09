"""Cost tracking utility for AI services."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.models.cost_tracking import CostTracking
from sqlalchemy.orm import Session


class CostTracker:
    """Track and manage AI service costs."""

    def __init__(self, db: Session):
        self.db = db

    async def track_cost(
        self,
        user_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        conversation_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> CostTracking:
        """Track a cost entry."""
        try:
            cost_entry = CostTracking(
                user_id=user_id,
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                conversation_id=conversation_id,
                request_id=request_id,
                timestamp=datetime.utcnow(),
            )

            self.db.add(cost_entry)
            self.db.commit()
            self.db.refresh(cost_entry)

            return cost_entry

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to track cost: {str(e)}")

    def get_user_costs(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
    ) -> List[CostTracking]:
        """Get cost entries for a user."""
        query = self.db.query(CostTracking).filter(CostTracking.user_id == user_id)

        if start_date:
            query = query.filter(CostTracking.timestamp >= start_date)

        if end_date:
            query = query.filter(CostTracking.timestamp <= end_date)

        if provider:
            query = query.filter(CostTracking.provider == provider)

        return query.order_by(CostTracking.timestamp.desc()).all()

    def get_total_cost(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
    ) -> float:
        """Get total cost for a user."""
        query = self.db.query(CostTracking).filter(CostTracking.user_id == user_id)

        if start_date:
            query = query.filter(CostTracking.timestamp >= start_date)

        if end_date:
            query = query.filter(CostTracking.timestamp <= end_date)

        if provider:
            query = query.filter(CostTracking.provider == provider)

        result = query.with_entities(CostTracking.cost).all()

        return sum(row[0] for row in result) if result else 0.0

    def get_cost_summary(self, user_id: str, days: int = 30) -> Dict[str, float]:
        """Get cost summary for a user."""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get costs by provider
        costs_by_provider = {}
        entries = self.get_user_costs(user_id, start_date=start_date)

        for entry in entries:
            if entry.provider not in costs_by_provider:
                costs_by_provider[entry.provider] = 0.0
            costs_by_provider[entry.provider] += entry.cost

        return costs_by_provider

    def get_daily_costs(self, user_id: str, days: int = 7) -> List[Dict[str, any]]:
        """Get daily cost breakdown."""
        start_date = datetime.utcnow() - timedelta(days=days)
        entries = self.get_user_costs(user_id, start_date=start_date)

        daily_costs = {}
        for entry in entries:
            date_key = entry.timestamp.date().isoformat()
            if date_key not in daily_costs:
                daily_costs[date_key] = {
                    "date": date_key,
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "requests": 0,
                }

            daily_costs[date_key]["total_cost"] += entry.cost
            daily_costs[date_key]["total_tokens"] += (
                entry.input_tokens + entry.output_tokens
            )
            daily_costs[date_key]["requests"] += 1

        return list(daily_costs.values())

    def get_model_usage_stats(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Dict[str, any]]:
        """Get model usage statistics."""
        start_date = datetime.utcnow() - timedelta(days=days)
        entries = self.get_user_costs(user_id, start_date=start_date)

        model_stats = {}
        for entry in entries:
            if entry.model not in model_stats:
                model_stats[entry.model] = {
                    "total_cost": 0.0,
                    "total_requests": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "avg_cost_per_request": 0.0,
                }

            stats = model_stats[entry.model]
            stats["total_cost"] += entry.cost
            stats["total_requests"] += 1
            stats["total_input_tokens"] += entry.input_tokens
            stats["total_output_tokens"] += entry.output_tokens

        # Calculate averages
        for model, stats in model_stats.items():
            if stats["total_requests"] > 0:
                stats["avg_cost_per_request"] = (
                    stats["total_cost"] / stats["total_requests"]
                )

        return model_stats
