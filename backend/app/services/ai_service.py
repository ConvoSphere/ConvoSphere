"""
Main AI service with modular architecture.

This file serves as the main entry point for the AI service, using the new modular architecture.
The refactored implementation is imported from the ai submodule to maintain backward compatibility.
"""

from backend.app.services.ai.ai_service_refactored import AIService

# Create a singleton instance for backward compatibility
ai_service = None


def get_ai_service(db=None):
    """Get or create the AI service instance."""
    global ai_service
    if ai_service is None:
        if db is None:
            raise ValueError(
                "Database session is required for AI service initialization"
            )
        ai_service = AIService(db)
    return ai_service


# Re-export the AIService class for direct imports
__all__ = ["AIService", "ai_service", "get_ai_service"]
