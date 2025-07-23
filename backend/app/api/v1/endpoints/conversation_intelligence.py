"""
Conversation Intelligence API endpoints.

This module provides API endpoints for conversation intelligence features
including summarization, topic detection, sentiment analysis, and analytics.
"""


from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.core.exceptions import AIError, ValidationError
from app.schemas.conversation_intelligence import (
    ConversationAnalytics,
    ConversationIntelligenceRequest,
    ConversationIntelligenceResponse,
    ConversationSummary,
    IntelligenceMetrics,
    SentimentAnalysis,
    SentimentAnalysisRequest,
    SummaryRequest,
    TopicDetectionRequest,
    TopicInfo,
)
from app.services.conversation_intelligence_service import (
    conversation_intelligence_service,
)

router = APIRouter()


@router.post("/analyze", response_model=ConversationIntelligenceResponse)
async def analyze_conversation(
    request: ConversationIntelligenceRequest,
) -> ConversationIntelligenceResponse:
    """
    Perform comprehensive conversation analysis.

    Args:
        request: Intelligence analysis request

    Returns:
        Intelligence analysis response
    """
    try:
        response = await conversation_intelligence_service.analyze_conversation(request)
        logger.info(f"Conversation intelligence analysis completed for conversation: {request.conversation_id}")
        return response
    except (ValidationError, AIError) as e:
        logger.error(f"Conversation intelligence analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in conversation intelligence analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/summarize", response_model=ConversationSummary)
async def generate_summary(
    request: SummaryRequest,
) -> ConversationSummary:
    """
    Generate conversation summary.

    Args:
        request: Summary generation request

    Returns:
        Generated conversation summary
    """
    try:
        summary = await conversation_intelligence_service.generate_summary(request)
        logger.info(f"Summary generated for conversation: {request.conversation_id}")
        return summary
    except (ValidationError, AIError) as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in summary generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/topics", response_model=list[TopicInfo])
async def detect_topics(
    request: TopicDetectionRequest,
) -> list[TopicInfo]:
    """
    Detect conversation topics.

    Args:
        request: Topic detection request

    Returns:
        List of detected topics
    """
    try:
        topics = await conversation_intelligence_service.detect_topics(request)
        logger.info(f"Topics detected for conversation: {request.conversation_id}")
        return topics
    except (ValidationError, AIError) as e:
        logger.error(f"Topic detection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in topic detection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sentiment", response_model=SentimentAnalysis)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
) -> SentimentAnalysis:
    """
    Analyze sentiment.

    Args:
        request: Sentiment analysis request

    Returns:
        Sentiment analysis results
    """
    try:
        sentiment = await conversation_intelligence_service.analyze_sentiment(request)
        logger.info("Sentiment analysis completed")
        return sentiment
    except (ValidationError, AIError) as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/{conversation_id}", response_model=ConversationAnalytics)
async def get_conversation_analytics(
    conversation_id: str,
    include_temporal_analysis: bool = Query(True, description="Include temporal analysis"),
) -> ConversationAnalytics:
    """
    Get conversation analytics.

    Args:
        conversation_id: Conversation ID
        include_temporal_analysis: Whether to include temporal analysis

    Returns:
        Conversation analytics
    """
    try:
        request = ConversationIntelligenceRequest(
            conversation_id=conversation_id,
            generate_analytics=True,
            include_temporal_analysis=include_temporal_analysis,
        )

        response = await conversation_intelligence_service.analyze_conversation(request)

        if not response.analytics:
            raise HTTPException(status_code=404, detail="Analytics not available for this conversation")

        logger.info(f"Analytics retrieved for conversation: {conversation_id}")
        return response.analytics
    except HTTPException:
        raise
    except (ValidationError, AIError) as e:
        logger.error(f"Analytics retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analytics retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary/{conversation_id}", response_model=ConversationSummary)
async def get_conversation_summary(
    conversation_id: str,
    summary_type: str = Query("executive", description="Type of summary to generate"),
    max_length: int = Query(500, ge=50, le=2000, description="Maximum summary length"),
) -> ConversationSummary:
    """
    Get conversation summary.

    Args:
        conversation_id: Conversation ID
        summary_type: Type of summary to generate
        max_length: Maximum summary length

    Returns:
        Conversation summary
    """
    try:
        from app.schemas.conversation_intelligence import SummaryType

        # Convert string to SummaryType enum
        try:
            summary_type_enum = SummaryType(summary_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid summary type: {summary_type}")

        request = SummaryRequest(
            conversation_id=conversation_id,
            summary_type=summary_type_enum,
            max_length=max_length,
        )

        summary = await conversation_intelligence_service.generate_summary(request)
        logger.info(f"Summary retrieved for conversation: {conversation_id}")
        return summary
    except HTTPException:
        raise
    except (ValidationError, AIError) as e:
        logger.error(f"Summary retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in summary retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/topics/{conversation_id}", response_model=list[TopicInfo])
async def get_conversation_topics(
    conversation_id: str,
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    max_topics: int = Query(10, ge=1, le=50, description="Maximum number of topics"),
) -> list[TopicInfo]:
    """
    Get conversation topics.

    Args:
        conversation_id: Conversation ID
        min_confidence: Minimum confidence threshold
        max_topics: Maximum number of topics

    Returns:
        List of conversation topics
    """
    try:
        request = TopicDetectionRequest(
            conversation_id=conversation_id,
            min_confidence=min_confidence,
            max_topics=max_topics,
        )

        topics = await conversation_intelligence_service.detect_topics(request)
        logger.info(f"Topics retrieved for conversation: {conversation_id}")
        return topics
    except (ValidationError, AIError) as e:
        logger.error(f"Topic retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in topic retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sentiment/{conversation_id}", response_model=SentimentAnalysis)
async def get_conversation_sentiment(
    conversation_id: str,
    include_emotions: bool = Query(True, description="Include emotion analysis"),
    include_trends: bool = Query(True, description="Include sentiment trends"),
) -> SentimentAnalysis:
    """
    Get conversation sentiment.

    Args:
        conversation_id: Conversation ID
        include_emotions: Whether to include emotion analysis
        include_trends: Whether to include sentiment trends

    Returns:
        Sentiment analysis results
    """
    try:
        request = SentimentAnalysisRequest(
            conversation_id=conversation_id,
            include_emotions=include_emotions,
            include_trends=include_trends,
        )

        sentiment = await conversation_intelligence_service.analyze_sentiment(request)
        logger.info(f"Sentiment retrieved for conversation: {conversation_id}")
        return sentiment
    except (ValidationError, AIError) as e:
        logger.error(f"Sentiment retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in sentiment retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sentiment/text", response_model=SentimentAnalysis)
async def analyze_text_sentiment(
    text: str = Query(..., min_length=1, description="Text to analyze"),
    include_emotions: bool = Query(True, description="Include emotion analysis"),
    include_trends: bool = Query(False, description="Include sentiment trends"),
    granular_analysis: bool = Query(False, description="Perform granular analysis"),
) -> SentimentAnalysis:
    """
    Analyze sentiment of provided text.

    Args:
        text: Text to analyze
        include_emotions: Whether to include emotion analysis
        include_trends: Whether to include sentiment trends
        granular_analysis: Whether to perform granular analysis

    Returns:
        Sentiment analysis results
    """
    try:
        request = SentimentAnalysisRequest(
            text=text,
            include_emotions=include_emotions,
            include_trends=include_trends,
            granular_analysis=granular_analysis,
        )

        sentiment = await conversation_intelligence_service.analyze_sentiment(request)
        logger.info("Text sentiment analysis completed")
        return sentiment
    except (ValidationError, AIError) as e:
        logger.error(f"Text sentiment analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in text sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics", response_model=IntelligenceMetrics)
async def get_intelligence_metrics() -> IntelligenceMetrics:
    """
    Get conversation intelligence metrics.

    Returns:
        Intelligence metrics
    """
    try:
        return await conversation_intelligence_service.get_metrics()
    except Exception as e:
        logger.error(f"Failed to get intelligence metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get intelligence metrics")


@router.post("/health")
async def intelligence_health_check() -> dict:
    """
    Check conversation intelligence service health.

    Returns:
        Health status
    """
    try:
        # Check if intelligence service is initialized
        metrics = await conversation_intelligence_service.get_metrics()

        return {
            "status": "healthy",
            "service": "conversation_intelligence",
            "total_requests": metrics.total_requests,
            "success_rate": metrics.successful_requests / max(metrics.total_requests, 1),
            "avg_processing_time": metrics.avg_processing_time,
        }
    except Exception as e:
        logger.error(f"Intelligence health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "conversation_intelligence",
            "error": str(e),
        }


@router.get("/supported-features")
async def get_supported_features() -> dict:
    """
    Get supported conversation intelligence features.

    Returns:
        List of supported features
    """
    return {
        "features": [
            {
                "name": "summarization",
                "description": "Generate conversation summaries",
                "types": ["executive", "detailed", "action_items", "key_points", "timeline"],
                "supported": True,
            },
            {
                "name": "topic_detection",
                "description": "Detect conversation topics",
                "categories": ["technical", "business", "personal", "support", "general", "custom"],
                "supported": True,
            },
            {
                "name": "sentiment_analysis",
                "description": "Analyze conversation sentiment",
                "features": ["overall_sentiment", "emotion_analysis", "sentiment_trends"],
                "supported": True,
            },
            {
                "name": "analytics",
                "description": "Comprehensive conversation analytics",
                "metrics": ["engagement", "quality", "clarity", "temporal_analysis"],
                "supported": True,
            },
        ],
        "ai_models": {
            "summarization": "gpt-4",
            "topic_detection": "gpt-4",
            "sentiment_analysis": "gpt-4",
            "analytics": "gpt-4",
        },
    }
