"""
RAG (Retrieval-Augmented Generation) Pydantic schemas.

This module defines the Pydantic models for RAG configuration and
advanced retrieval features, integrating with existing knowledge base
and semantic search functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RAGStrategy(Enum):
    """RAG retrieval strategies."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"
    CONTEXTUAL = "contextual"
    ADAPTIVE = "adaptive"


class ContextRankingMethod(Enum):
    """Context ranking methods."""
    RELEVANCE = "relevance"
    DIVERSITY = "diversity"
    FRESHNESS = "freshness"
    AUTHORITY = "authority"
    HYBRID = "hybrid"


class EmbeddingModel(Enum):
    """Supported embedding models."""
    OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    OPENAI_TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    COHERE_EMBED_ENGLISH_V3 = "embed-english-v3.0"
    COHERE_EMBED_MULTILINGUAL_V3 = "embed-multilingual-v3.0"


class RAGConfig(BaseModel):
    """RAG configuration with comprehensive validation."""
    
    # Basic Configuration
    name: str = Field(..., min_length=1, max_length=100, description="RAG configuration name")
    description: str = Field(..., max_length=500, description="RAG configuration description")
    enabled: bool = Field(default=True, description="Whether RAG is enabled")
    
    # Retrieval Configuration
    strategy: RAGStrategy = Field(default=RAGStrategy.SEMANTIC, description="Retrieval strategy")
    max_context_length: int = Field(default=4000, ge=1000, le=32000, description="Maximum context length in tokens")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results to retrieve")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum similarity threshold")
    
    # Context Ranking
    ranking_method: ContextRankingMethod = Field(default=ContextRankingMethod.RELEVANCE, description="Context ranking method")
    diversity_penalty: float = Field(default=0.1, ge=0.0, le=1.0, description="Diversity penalty for ranking")
    freshness_weight: float = Field(default=0.2, ge=0.0, le=1.0, description="Weight for content freshness")
    authority_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight for source authority")
    
    # Embedding Configuration
    embedding_model: EmbeddingModel = Field(default=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL, description="Embedding model")
    embedding_dimensions: int = Field(default=1536, ge=384, le=3072, description="Embedding dimensions")
    chunk_size: int = Field(default=1000, ge=100, le=4000, description="Text chunk size for embedding")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Chunk overlap in characters")
    
    # Knowledge Base Integration
    knowledge_sources: List[str] = Field(default_factory=list, description="Knowledge base sources to search")
    include_conversation_history: bool = Field(default=True, description="Include conversation history in search")
    conversation_history_limit: int = Field(default=10, ge=0, le=50, description="Number of recent messages to include")
    
    # Advanced Features
    dynamic_context_selection: bool = Field(default=True, description="Enable dynamic context selection")
    context_compression: bool = Field(default=False, description="Enable context compression")
    reranking_enabled: bool = Field(default=True, description="Enable result reranking")
    cache_results: bool = Field(default=True, description="Cache retrieval results")
    
    # Performance Configuration
    timeout_seconds: float = Field(default=30.0, ge=5.0, le=300.0, description="Retrieval timeout in seconds")
    max_concurrent_searches: int = Field(default=5, ge=1, le=20, description="Maximum concurrent searches")
    batch_size: int = Field(default=10, ge=1, le=100, description="Batch size for processing")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Configuration creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Configuration update timestamp")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate configuration name."""
        if not v.strip():
            raise ValueError('Configuration name cannot be empty')
        if any(char in v for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            raise ValueError('Configuration name contains invalid characters')
        return v.strip()
    
    @field_validator('max_context_length')
    @classmethod
    def validate_context_length(cls, v: int, info) -> int:
        """Validate context length based on strategy."""
        strategy = info.data.get('strategy', RAGStrategy.SEMANTIC)
        if strategy == RAGStrategy.ADAPTIVE and v < 2000:
            raise ValueError('Adaptive strategy requires at least 2000 tokens context length')
        return v
    
    @field_validator('similarity_threshold')
    @classmethod
    def validate_similarity_threshold(cls, v: float) -> float:
        """Validate similarity threshold."""
        if v < 0.1:
            raise ValueError('Similarity threshold too low, may return irrelevant results')
        return round(v, 2)
    
    @field_validator('chunk_overlap')
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Validate chunk overlap relative to chunk size."""
        chunk_size = info.data.get('chunk_size', 1000)
        if v >= chunk_size:
            raise ValueError('Chunk overlap must be less than chunk size')
        return v
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Default RAG Config",
                    "description": "Standard semantic search configuration",
                    "strategy": "semantic",
                    "max_context_length": 4000,
                    "max_results": 5,
                    "similarity_threshold": 0.7,
                    "embedding_model": "text-embedding-3-small"
                }
            ]
        }
    }


class RAGRequest(BaseModel):
    """RAG retrieval request."""
    
    query: str = Field(..., min_length=1, max_length=10000, description="Search query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    config_id: Optional[str] = Field(None, description="RAG configuration ID")
    
    # Override configuration
    max_results: Optional[int] = Field(None, ge=1, le=20, description="Override max results")
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Override similarity threshold")
    knowledge_sources: Optional[List[str]] = Field(None, description="Override knowledge sources")
    
    # Context options
    include_conversation_history: Optional[bool] = Field(None, description="Override conversation history inclusion")
    conversation_history_limit: Optional[int] = Field(None, ge=0, le=50, description="Override history limit")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean query."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError('Query cannot be empty')
        if len(cleaned) < 3:
            raise ValueError('Query too short, minimum 3 characters')
        return cleaned
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGResult(BaseModel):
    """Individual RAG retrieval result."""
    
    content: str = Field(..., description="Retrieved content")
    source: str = Field(..., description="Content source")
    source_type: str = Field(..., description="Source type (document, conversation, etc.)")
    source_id: str = Field(..., description="Source ID")
    
    # Relevance metrics
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    ranking_score: float = Field(..., ge=0.0, le=1.0, description="Final ranking score")
    
    # Content metadata
    chunk_index: Optional[int] = Field(None, description="Chunk index in source")
    token_count: int = Field(..., ge=1, description="Number of tokens")
    created_at: Optional[datetime] = Field(None, description="Content creation timestamp")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGResponse(BaseModel):
    """RAG retrieval response."""
    
    query: str = Field(..., description="Original query")
    results: List[RAGResult] = Field(..., description="Retrieved results")
    config_used: RAGConfig = Field(..., description="Configuration used")
    
    # Performance metrics
    total_results: int = Field(..., ge=0, description="Total results found")
    retrieval_time: float = Field(..., ge=0.0, description="Retrieval time in seconds")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    
    # Context information
    context_length: int = Field(..., ge=0, description="Total context length in tokens")
    sources_queried: List[str] = Field(..., description="Sources that were queried")
    
    # Cache information
    cached: bool = Field(default=False, description="Whether results were cached")
    cache_hit: bool = Field(default=False, description="Whether cache was hit")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGContext(BaseModel):
    """RAG context for AI generation."""
    
    query: str = Field(..., description="Original query")
    retrieved_results: List[RAGResult] = Field(..., description="Retrieved results")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")
    
    # Context composition
    context_text: str = Field(..., description="Composed context text")
    context_tokens: int = Field(..., ge=0, description="Number of tokens in context")
    max_tokens: int = Field(..., ge=0, description="Maximum allowed tokens")
    
    # Context metadata
    sources_used: List[str] = Field(..., description="Sources used in context")
    relevance_summary: Dict[str, float] = Field(default_factory=dict, description="Relevance summary by source")
    
    # Generation hints
    generation_hints: Dict[str, Any] = Field(default_factory=dict, description="Hints for AI generation")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGMetrics(BaseModel):
    """RAG performance and quality metrics."""
    
    # Performance metrics
    total_requests: int = Field(..., ge=0, description="Total RAG requests")
    successful_requests: int = Field(..., ge=0, description="Successful requests")
    failed_requests: int = Field(..., ge=0, description="Failed requests")
    
    # Timing metrics
    avg_retrieval_time: float = Field(..., ge=0.0, description="Average retrieval time")
    avg_processing_time: float = Field(..., ge=0.0, description="Average processing time")
    avg_total_time: float = Field(..., ge=0.0, description="Average total time")
    
    # Quality metrics
    avg_similarity_score: float = Field(..., ge=0.0, le=1.0, description="Average similarity score")
    avg_relevance_score: float = Field(..., ge=0.0, le=1.0, description="Average relevance score")
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0, description="Cache hit rate")
    
    # Source metrics
    source_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by source")
    strategy_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by strategy")
    
    # Error metrics
    error_counts: Dict[str, int] = Field(default_factory=dict, description="Error counts by type")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGConfigCreate(BaseModel):
    """RAG configuration creation request."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Configuration name")
    description: str = Field(..., max_length=500, description="Configuration description")
    config: RAGConfig = Field(..., description="RAG configuration")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGConfigUpdate(BaseModel):
    """RAG configuration update request."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Configuration name")
    description: Optional[str] = Field(None, max_length=500, description="Configuration description")
    config: Optional[RAGConfig] = Field(None, description="RAG configuration")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGConfigResponse(BaseModel):
    """RAG configuration response."""
    
    id: str = Field(..., description="Configuration ID")
    name: str = Field(..., description="Configuration name")
    description: str = Field(..., description="Configuration description")
    config: RAGConfig = Field(..., description="RAG configuration")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class RAGConfigList(BaseModel):
    """RAG configuration list response."""
    
    configs: List[RAGConfigResponse] = Field(..., description="List of configurations")
    total: int = Field(..., ge=0, description="Total number of configurations")
    skip: int = Field(..., ge=0, description="Number of configurations skipped")
    limit: int = Field(..., ge=1, description="Maximum number of configurations returned")
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }