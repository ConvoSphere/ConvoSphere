"""
Conversation Intelligence Pydantic schemas.

This module defines the Pydantic models for conversation intelligence
features including summarization, topic detection, sentiment analysis,
and conversation analytics.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SentimentType(Enum):
    """Sentiment classification types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class TopicCategory(Enum):
    """Topic categories for classification."""
    TECHNICAL = "technical"
    BUSINESS = "business"
    PERSONAL = "personal"
    SUPPORT = "support"
    GENERAL = "general"
    CUSTOM = "custom"


class SummaryType(Enum):
    """Summary generation types."""
    EXECUTIVE = "executive"
    DETAILED = "detailed"
    ACTION_ITEMS = "action_items"
    KEY_POINTS = "key_points"
    TIMELINE = "timeline"


class ConversationSummary(BaseModel):
    """Conversation summary with comprehensive analysis."""
    
    # Basic information
    conversation_id: str = Field(..., description="Conversation ID")
    summary_type: SummaryType = Field(..., description="Type of summary")
    summary_text: str = Field(..., min_length=10, max_length=10000, description="Summary text")
    
    # Summary metadata
    word_count: int = Field(..., ge=0, description="Number of words in summary")
    token_count: int = Field(..., ge=0, description="Number of tokens in summary")
    compression_ratio: float = Field(..., ge=0.0, le=1.0, description="Compression ratio vs original")
    
    # Key elements
    key_points: List[str] = Field(default_factory=list, description="Key points extracted")
    action_items: List[str] = Field(default_factory=list, description="Action items identified")
    decisions_made: List[str] = Field(default_factory=list, description="Decisions made")
    questions_asked: List[str] = Field(default_factory=list, description="Questions asked")
    
    # Context information
    participants: List[str] = Field(default_factory=list, description="Conversation participants")
    duration_minutes: Optional[float] = Field(None, ge=0.0, description="Conversation duration")
    message_count: int = Field(..., ge=0, description="Number of messages in conversation")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Summary creation timestamp")
    model_used: str = Field(..., description="AI model used for summarization")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in summary quality")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional summary metadata")
    
    @field_validator('summary_text')
    @classmethod
    def validate_summary_text(cls, v: str) -> str:
        """Validate summary text."""
        if not v.strip():
            raise ValueError('Summary text cannot be empty')
        return v.strip()
    
    @field_validator('compression_ratio')
    @classmethod
    def validate_compression_ratio(cls, v: float) -> float:
        """Validate compression ratio."""
        if v <= 0.0:
            raise ValueError('Compression ratio must be positive')
        if v > 1.0:
            raise ValueError('Compression ratio cannot exceed 1.0')
        return round(v, 3)
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class TopicInfo(BaseModel):
    """Topic information with confidence and metadata."""
    
    topic: str = Field(..., min_length=1, max_length=200, description="Topic name")
    category: TopicCategory = Field(..., description="Topic category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in topic detection")
    
    # Topic metadata
    keywords: List[str] = Field(default_factory=list, description="Keywords associated with topic")
    related_topics: List[str] = Field(default_factory=list, description="Related topics")
    frequency: int = Field(..., ge=0, description="Topic frequency in conversation")
    
    # Temporal information
    first_mentioned: Optional[datetime] = Field(None, description="First mention timestamp")
    last_mentioned: Optional[datetime] = Field(None, description="Last mention timestamp")
    
    # Context
    message_indices: List[int] = Field(default_factory=list, description="Message indices where topic appears")
    context_snippets: List[str] = Field(default_factory=list, description="Context snippets for topic")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class SentimentAnalysis(BaseModel):
    """Sentiment analysis for conversation or message."""
    
    # Sentiment classification
    overall_sentiment: SentimentType = Field(..., description="Overall sentiment")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score (-1 to 1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in sentiment analysis")
    
    # Detailed sentiment breakdown
    positive_score: float = Field(..., ge=0.0, le=1.0, description="Positive sentiment score")
    negative_score: float = Field(..., ge=0.0, le=1.0, description="Negative sentiment score")
    neutral_score: float = Field(..., ge=0.0, le=1.0, description="Neutral sentiment score")
    
    # Emotion analysis
    emotions: Dict[str, float] = Field(default_factory=dict, description="Emotion scores")
    dominant_emotion: Optional[str] = Field(None, description="Dominant emotion")
    
    # Sentiment trends
    sentiment_trend: str = Field(default="stable", description="Sentiment trend (improving, declining, stable)")
    sentiment_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Sentiment change points")
    
    # Context
    analyzed_text: str = Field(..., description="Text that was analyzed")
    message_id: Optional[str] = Field(None, description="Message ID if analyzing single message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID if analyzing conversation")
    
    # Metadata
    model_used: str = Field(..., description="AI model used for sentiment analysis")
    created_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class ConversationAnalytics(BaseModel):
    """Comprehensive conversation analytics."""
    
    # Basic metrics
    conversation_id: str = Field(..., description="Conversation ID")
    total_messages: int = Field(..., ge=0, description="Total number of messages")
    total_participants: int = Field(..., ge=1, description="Number of participants")
    duration_minutes: float = Field(..., ge=0.0, description="Conversation duration in minutes")
    
    # Message analysis
    avg_message_length: float = Field(..., ge=0.0, description="Average message length")
    message_frequency: float = Field(..., ge=0.0, description="Messages per minute")
    response_times: List[float] = Field(default_factory=list, description="Response times in seconds")
    avg_response_time: float = Field(..., ge=0.0, description="Average response time")
    
    # Participant analysis
    participant_activity: Dict[str, int] = Field(default_factory=dict, description="Messages per participant")
    participant_sentiment: Dict[str, SentimentType] = Field(default_factory=dict, description="Sentiment per participant")
    participant_engagement: Dict[str, float] = Field(default_factory=dict, description="Engagement scores")
    
    # Content analysis
    topics_detected: List[TopicInfo] = Field(default_factory=list, description="Detected topics")
    sentiment_overview: SentimentAnalysis = Field(..., description="Overall sentiment analysis")
    key_phrases: List[str] = Field(default_factory=list, description="Key phrases extracted")
    
    # Quality metrics
    conversation_quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall conversation quality")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="Engagement level")
    clarity_score: float = Field(..., ge=0.0, le=1.0, description="Conversation clarity")
    
    # Temporal analysis
    conversation_phases: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation phases")
    peak_activity_time: Optional[datetime] = Field(None, description="Peak activity timestamp")
    lull_periods: List[Dict[str, Any]] = Field(default_factory=list, description="Periods of low activity")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Analytics creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    analysis_version: str = Field(default="1.0", description="Analysis algorithm version")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class ConversationIntelligenceRequest(BaseModel):
    """Request for conversation intelligence analysis."""
    
    conversation_id: str = Field(..., description="Conversation ID to analyze")
    analysis_types: List[str] = Field(default_factory=list, description="Types of analysis to perform")
    
    # Summary options
    generate_summary: bool = Field(default=True, description="Generate conversation summary")
    summary_type: SummaryType = Field(default=SummaryType.EXECUTIVE, description="Type of summary to generate")
    
    # Topic detection options
    detect_topics: bool = Field(default=True, description="Detect conversation topics")
    topic_categories: List[TopicCategory] = Field(default_factory=list, description="Topic categories to focus on")
    
    # Sentiment analysis options
    analyze_sentiment: bool = Field(default=True, description="Analyze conversation sentiment")
    include_emotion_analysis: bool = Field(default=True, description="Include emotion analysis")
    
    # Analytics options
    generate_analytics: bool = Field(default=True, description="Generate comprehensive analytics")
    include_temporal_analysis: bool = Field(default=True, description="Include temporal analysis")
    
    # Configuration
    max_summary_length: int = Field(default=500, ge=50, le=2000, description="Maximum summary length")
    min_topic_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum topic confidence")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")
    
    @field_validator('analysis_types')
    @classmethod
    def validate_analysis_types(cls, v: List[str]) -> List[str]:
        """Validate analysis types."""
        valid_types = ['summary', 'topics', 'sentiment', 'analytics', 'engagement', 'quality']
        for analysis_type in v:
            if analysis_type not in valid_types:
                raise ValueError(f'Invalid analysis type: {analysis_type}')
        return v
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class ConversationIntelligenceResponse(BaseModel):
    """Response for conversation intelligence analysis."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    request_id: str = Field(..., description="Analysis request ID")
    
    # Analysis results
    summary: Optional[ConversationSummary] = Field(None, description="Generated summary")
    topics: List[TopicInfo] = Field(default_factory=list, description="Detected topics")
    sentiment: Optional[SentimentAnalysis] = Field(None, description="Sentiment analysis")
    analytics: Optional[ConversationAnalytics] = Field(None, description="Comprehensive analytics")
    
    # Processing information
    processing_time: float = Field(..., ge=0.0, description="Total processing time in seconds")
    models_used: List[str] = Field(default_factory=list, description="AI models used")
    analysis_completed: List[str] = Field(default_factory=list, description="Completed analysis types")
    
    # Quality indicators
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Confidence scores by analysis type")
    warnings: List[str] = Field(default_factory=list, description="Analysis warnings")
    errors: List[str] = Field(default_factory=list, description="Analysis errors")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Response creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Response expiration timestamp")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class IntelligenceMetrics(BaseModel):
    """Metrics for conversation intelligence system."""
    
    # Processing metrics
    total_requests: int = Field(..., ge=0, description="Total intelligence requests")
    successful_requests: int = Field(..., ge=0, description="Successful requests")
    failed_requests: int = Field(..., ge=0, description="Failed requests")
    
    # Performance metrics
    avg_processing_time: float = Field(..., ge=0.0, description="Average processing time")
    avg_summary_length: float = Field(..., ge=0.0, description="Average summary length")
    avg_topic_count: float = Field(..., ge=0.0, description="Average topics detected")
    
    # Quality metrics
    avg_confidence_score: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")
    avg_quality_score: float = Field(..., ge=0.0, le=1.0, description="Average quality score")
    user_satisfaction_score: float = Field(..., ge=0.0, le=1.0, description="User satisfaction score")
    
    # Usage metrics
    analysis_type_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by analysis type")
    model_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by AI model")
    error_counts: Dict[str, int] = Field(default_factory=dict, description="Error counts by type")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class SummaryRequest(BaseModel):
    """Request for conversation summarization."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    summary_type: SummaryType = Field(default=SummaryType.EXECUTIVE, description="Type of summary")
    max_length: int = Field(default=500, ge=50, le=2000, description="Maximum summary length")
    include_action_items: bool = Field(default=True, description="Include action items")
    include_key_points: bool = Field(default=True, description="Include key points")
    
    # Customization
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus on")
    exclude_topics: List[str] = Field(default_factory=list, description="Topics to exclude")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class TopicDetectionRequest(BaseModel):
    """Request for topic detection."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    categories: List[TopicCategory] = Field(default_factory=list, description="Topic categories to detect")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    max_topics: int = Field(default=10, ge=1, le=50, description="Maximum number of topics")
    
    # Advanced options
    include_keywords: bool = Field(default=True, description="Include keywords for each topic")
    include_context: bool = Field(default=True, description="Include context snippets")
    temporal_analysis: bool = Field(default=False, description="Include temporal analysis")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class SentimentAnalysisRequest(BaseModel):
    """Request for sentiment analysis."""
    
    conversation_id: Optional[str] = Field(None, description="Conversation ID for conversation analysis")
    message_id: Optional[str] = Field(None, description="Message ID for single message analysis")
    text: Optional[str] = Field(None, description="Raw text for analysis")
    
    # Analysis options
    include_emotions: bool = Field(default=True, description="Include emotion analysis")
    include_trends: bool = Field(default=True, description="Include sentiment trends")
    granular_analysis: bool = Field(default=False, description="Perform granular analysis")
    
    # Customization
    custom_emotions: List[str] = Field(default_factory=list, description="Custom emotions to detect")
    
    @field_validator('conversation_id', 'message_id', 'text')
    @classmethod
    def validate_analysis_target(cls, v, info):
        """Ensure at least one analysis target is provided."""
        values = info.data
        if not any([values.get('conversation_id'), values.get('message_id'), values.get('text')]):
            raise ValueError('Must provide conversation_id, message_id, or text for analysis')
        return v
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }