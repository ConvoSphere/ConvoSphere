"""
Tests for RAG (Retrieval-Augmented Generation) service.

This module contains comprehensive tests for the RAG service including
configuration management, retrieval, and error handling.
"""

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from app.core.exceptions import AIError, ValidationError
from app.schemas.rag import (
    ContextRankingMethod,
    EmbeddingModel,
    RAGConfig,
    RAGMetrics,
    RAGRequest,
    RAGResponse,
    RAGResult,
    RAGStrategy,
)
from app.services.rag_service import RAGService


class TestRAGService:
    """Test cases for RAG service."""

    @pytest.fixture
    def rag_service(self):
        """Create RAG service instance for testing."""
        return RAGService()

    @pytest.fixture
    def sample_config(self):
        """Create sample RAG configuration."""
        return RAGConfig(
            name="Test Config",
            description="Test configuration",
            strategy=RAGStrategy.SEMANTIC,
            max_context_length=4000,
            max_results=5,
            similarity_threshold=0.7,
            embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL,
            ranking_method=ContextRankingMethod.RELEVANCE,
        )

    @pytest.fixture
    def sample_request(self):
        """Create sample RAG request."""
        return RAGRequest(
            query="test query",
            conversation_id="test-conversation",
            user_id="test-user",
            max_results=5,
            similarity_threshold=0.7,
        )

    @pytest.mark.asyncio
    async def test_initialize_success(self, rag_service):
        """Test successful service initialization."""
        with (
            patch.object(rag_service.weaviate_service, "health", return_value=True),
            patch.object(rag_service, "_cache_enabled", new=True),
        ):
            await rag_service.initialize()
            assert rag_service._initialized is True  # noqa: S101

    @pytest.mark.asyncio
    async def test_initialize_weaviate_unavailable(self, rag_service):
        """Test initialization when Weaviate is unavailable."""
        with patch.object(rag_service.weaviate_service, "health", return_value=False):
            await rag_service.initialize()
            # Should not raise exception, just log warning

    @pytest.mark.asyncio
    async def test_initialize_cache_failure(self, rag_service):
        """Test initialization when cache fails."""
        with (
            patch.object(rag_service.weaviate_service, "health", return_value=True),
            patch(
                "app.services.rag_service.cache_service.initialize",
                side_effect=Exception("Cache error"),
            ),
        ):
            await rag_service.initialize()
            assert rag_service._cache_enabled is False  # noqa: S101

    @pytest.mark.asyncio
    async def test_retrieve_success(self, rag_service, sample_request, sample_config):
        """Test successful RAG retrieval."""
        with (
            patch.object(rag_service, "_perform_retrieval", return_value=[]),
            patch.object(rag_service, "_process_results", return_value=[]),
        ):
            response = await rag_service.retrieve(sample_request, sample_config)

            assert isinstance(response, RAGResponse)  # noqa: S101
            assert response.query == sample_request.query  # noqa: S101
            assert response.config_used == sample_config  # noqa: S101
            assert response.total_results == 0  # noqa: S101
            assert response.retrieval_time >= 0  # noqa: S101
            assert response.processing_time >= 0  # noqa: S101

    @pytest.mark.asyncio
    async def test_retrieve_with_cache_hit(
        self,
        rag_service,
        sample_request,
        sample_config,
    ):
        """Test RAG retrieval with cache hit."""
        cached_response = RAGResponse(
            query=sample_request.query,
            results=[],
            config_used=sample_config,
            total_results=0,
            retrieval_time=0.1,
            processing_time=0.1,
            context_length=0,
            sources_queried=[],
            cached=True,
            cache_hit=True,
        )

        with patch.object(
            rag_service,
            "_get_cached_result",
            return_value=cached_response,
        ):
            response = await rag_service.retrieve(sample_request, sample_config)

            assert response.cached is True  # noqa: S101
            assert response.cache_hit is True  # noqa: S101

    @pytest.mark.asyncio
    async def test_retrieve_validation_error(self, rag_service, sample_config):
        """Test RAG retrieval with validation error."""
        invalid_request = RAGRequest(query="", conversation_id="test")

        with pytest.raises(ValidationError):
            await rag_service.retrieve(invalid_request, sample_config)

    @pytest.mark.asyncio
    async def test_retrieve_ai_error(self, rag_service, sample_request, sample_config):
        """Test RAG retrieval with AI error."""
        with (
            patch.object(
                rag_service,
                "_perform_retrieval",
                side_effect=AIError("AI service error"),
            ),
            pytest.raises(AIError),
        ):
            await rag_service.retrieve(sample_request, sample_config)

    @pytest.mark.asyncio
    async def test_semantic_retrieval(self, rag_service, sample_request, sample_config):
        """Test semantic retrieval strategy."""
        mock_knowledge_results = [
            {"content": "test content", "id": "1", "score": 0.8},
        ]

        with (
            patch.object(
                rag_service.weaviate_service,
                "semantic_search_knowledge",
                return_value=mock_knowledge_results,
            ),
            patch.object(
                rag_service.weaviate_service,
                "semantic_search_messages",
                return_value=[],
            ),
        ):
            results = await rag_service._semantic_retrieval(
                sample_request,
                sample_config,
                [],
            )

            assert len(results) == 1  # noqa: S101
            assert results[0]["content"] == "test content"  # noqa: S101
            assert results[0]["source"] == "knowledge_base"  # noqa: S101

    @pytest.mark.asyncio
    async def test_hybrid_retrieval(self, rag_service, sample_request, sample_config):
        """Test hybrid retrieval strategy."""
        with (
            patch.object(
                rag_service,
                "_semantic_retrieval",
                return_value=[{"content": "semantic"}],
            ),
            patch.object(
                rag_service,
                "_keyword_retrieval",
                return_value=[{"content": "keyword"}],
            ),
        ):
            results = await rag_service._hybrid_retrieval(
                sample_request,
                sample_config,
                [],
            )

            assert len(results) == 2  # noqa: S101
            assert any(r["content"] == "semantic" for r in results)  # noqa: S101
            assert any(r["content"] == "keyword" for r in results)  # noqa: S101

    @pytest.mark.asyncio
    async def test_keyword_retrieval(self, rag_service, sample_request, sample_config):
        """Test keyword retrieval strategy."""
        mock_results = [{"content": "keyword result", "id": "1", "score": 0.6}]

        with patch.object(
            rag_service.weaviate_service,
            "semantic_search_knowledge",
            return_value=mock_results,
        ):
            results = await rag_service._keyword_retrieval(
                sample_request,
                sample_config,
                [],
            )

            assert len(results) > 0  # noqa: S101
            assert all(r["source"] == "knowledge_base" for r in results)  # noqa: S101

    @pytest.mark.asyncio
    async def test_contextual_retrieval(
        self,
        rag_service,
        sample_request,
        sample_config,
    ):
        """Test contextual retrieval strategy."""
        conversation_history = [{"content": "previous message"}]
        mock_results = [{"content": "contextual result", "id": "1", "score": 0.7}]

        with patch.object(
            rag_service.weaviate_service,
            "semantic_search_knowledge",
            return_value=mock_results,
        ):
            results = await rag_service._contextual_retrieval(
                sample_request,
                sample_config,
                conversation_history,
            )

            assert len(results) == 1  # noqa: S101
            assert results[0]["content"] == "contextual result"  # noqa: S101

    @pytest.mark.asyncio
    async def test_adaptive_retrieval_technical(
        self,
        rag_service,
        sample_request,
        sample_config,
    ):
        """Test adaptive retrieval for technical queries."""
        sample_request.query = "API function method class"

        with patch.object(
            rag_service,
            "_semantic_retrieval",
            return_value=[{"content": "technical result"}],
        ):
            results = await rag_service._adaptive_retrieval(
                sample_request,
                sample_config,
                [],
            )

            assert len(results) == 1  # noqa: S101
            assert results[0]["content"] == "technical result"  # noqa: S101

    @pytest.mark.asyncio
    async def test_adaptive_retrieval_conversational(
        self,
        rag_service,
        sample_request,
        sample_config,
    ):
        """Test adaptive retrieval for conversational queries."""
        sample_request.query = "how can you help me please"

        with patch.object(
            rag_service,
            "_contextual_retrieval",
            return_value=[{"content": "conversational result"}],
        ):
            results = await rag_service._adaptive_retrieval(
                sample_request,
                sample_config,
                [],
            )

            assert len(results) == 1  # noqa: S101
            assert results[0]["content"] == "conversational result"  # noqa: S101

    @pytest.mark.asyncio
    async def test_process_results(self, rag_service, sample_request, sample_config):
        """Test result processing and ranking."""
        raw_results = [
            {
                "content": "test content 1",
                "source": "knowledge_base",
                "source_type": "document",
                "source_id": "1",
                "similarity_score": 0.8,
                "chunk_index": 0,
                "created_at": datetime.now(tz=UTC),
                "metadata": {},
            },
            {
                "content": "test content 2",
                "source": "knowledge_base",
                "source_type": "document",
                "source_id": "2",
                "similarity_score": 0.6,
                "chunk_index": 1,
                "created_at": datetime.now(tz=UTC),
                "metadata": {},
            },
        ]

        results = await rag_service._process_results(
            raw_results,
            sample_request,
            sample_config,
        )

        assert len(results) == 2  # noqa: S101
        assert all(isinstance(r, RAGResult) for r in results)  # noqa: S101
        assert results[0].ranking_score >= results[1].ranking_score  # noqa: S101

    @pytest.mark.asyncio
    async def test_rank_results(self, rag_service, sample_config):
        """Test result ranking."""
        results = [
            RAGResult(
                content="content 1",
                source="source1",
                source_type="document",
                source_id="1",
                similarity_score=0.8,
                relevance_score=0.7,
                ranking_score=0.0,
                token_count=10,
            ),
            RAGResult(
                content="content 2",
                source="source2",
                source_type="document",
                source_id="2",
                similarity_score=0.6,
                relevance_score=0.5,
                ranking_score=0.0,
                token_count=10,
            ),
        ]

        ranked_results = await rag_service._rank_results(results, sample_config)

        assert len(ranked_results) == 2  # noqa: S101
        assert (
            ranked_results[0].ranking_score >= ranked_results[1].ranking_score
        )  # noqa: S101

    def test_calculate_relevance_score(self, rag_service, sample_request):
        """Test relevance score calculation."""
        result = {"content": "test query content matches"}
        score = rag_service._calculate_relevance_score(result, sample_request)

        assert 0.0 <= score <= 1.0  # noqa: S101
        assert score > 0.0  # noqa: S101

    def test_calculate_freshness_score(self, rag_service):
        """Test freshness score calculation."""
        recent_time = datetime.now(tz=UTC)
        old_time = datetime(2020, 1, 1, tzinfo=UTC)

        recent_score = rag_service._calculate_freshness_score(recent_time)
        old_score = rag_service._calculate_freshness_score(old_time)

        assert recent_score > old_score  # noqa: S101
        assert 0.0 <= recent_score <= 1.0  # noqa: S101
        assert 0.0 <= old_score <= 1.0  # noqa: S101

    def test_calculate_authority_score(self, rag_service):
        """Test authority score calculation."""
        official_score = rag_service._calculate_authority_score(
            "official_documentation",
        )
        unknown_score = rag_service._calculate_authority_score("unknown_source")

        assert official_score > unknown_score  # noqa: S101
        assert official_score == 1.0  # noqa: S101
        assert unknown_score == 0.3  # noqa: S101

    def test_extract_keywords(self, rag_service):
        """Test keyword extraction."""
        query = "how to implement API authentication with JWT tokens"
        keywords = rag_service._extract_keywords(query)

        assert len(keywords) > 0  # noqa: S101
        assert "implement" in keywords  # noqa: S101
        assert "API" in keywords  # noqa: S101
        assert "authentication" in keywords  # noqa: S101
        assert "JWT" in keywords  # noqa: S101
        assert "tokens" in keywords  # noqa: S101

    def test_build_contextual_query(self, rag_service):
        """Test contextual query building."""
        query = "help with database"
        history = [
            {"content": "I need help with PostgreSQL"},
            {"content": "The connection is failing"},
            {"content": "Can you assist me?"},
        ]

        contextual_query = rag_service._build_contextual_query(query, history)

        assert "help with database" in contextual_query  # noqa: S101
        assert "PostgreSQL" in contextual_query  # noqa: S101
        assert "connection" in contextual_query  # noqa: S101

    def test_analyze_query(self, rag_service):
        """Test query analysis."""
        technical_query = "API function method class database"
        conversational_query = "how can you help me please"
        specific_query = "implement authentication with JWT tokens and OAuth2"

        technical_analysis = rag_service._analyze_query(technical_query)
        conversational_analysis = rag_service._analyze_query(conversational_query)
        specific_analysis = rag_service._analyze_query(specific_query)

        assert technical_analysis["is_technical"] is True  # noqa: S101
        assert conversational_analysis["is_conversational"] is True  # noqa: S101
        assert specific_analysis["has_specific_terms"] is True  # noqa: S101

    def test_combine_results(self, rag_service):
        """Test result combination and deduplication."""
        results1 = [{"content": "unique content 1", "source": "source1"}]
        results2 = [{"content": "unique content 2", "source": "source2"}]

        combined = rag_service._combine_results(results1, results2)

        assert len(combined) == 2  # noqa: S101
        assert any(r["content"] == "unique content 1" for r in combined)  # noqa: S101
        assert any(r["content"] == "unique content 2" for r in combined)  # noqa: S101

    @pytest.mark.asyncio
    async def test_create_config(self, rag_service, sample_config):
        """Test configuration creation."""
        config_id = await rag_service.create_config(sample_config)

        assert isinstance(config_id, str)  # noqa: S101
        assert len(config_id) > 0  # noqa: S101

        configs = await rag_service.list_configs()
        assert any(cid == config_id for cid, _ in configs)  # noqa: S101

    @pytest.mark.asyncio
    async def test_update_config(self, rag_service, sample_config):
        """Test configuration update."""
        config_id = await rag_service.create_config(sample_config)

        updated_config = RAGConfig(
            name="Updated Config",
            description="Updated description",
            strategy=RAGStrategy.HYBRID,
            max_context_length=6000,
            max_results=10,
            similarity_threshold=0.8,
            embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE,
            ranking_method=ContextRankingMethod.DIVERSITY,
        )

        success = await rag_service.update_config(config_id, updated_config)
        assert success is True  # noqa: S101

    @pytest.mark.asyncio
    async def test_delete_config(self, rag_service, sample_config):
        """Test configuration deletion."""
        config_id = await rag_service.create_config(sample_config)

        success = await rag_service.delete_config(config_id)
        assert success is True  # noqa: S101

        configs = await rag_service.list_configs()
        assert not any(cid == config_id for cid, _ in configs)  # noqa: S101

    @pytest.mark.asyncio
    async def test_get_metrics(self, rag_service):
        """Test metrics retrieval."""
        metrics = await rag_service.get_metrics()

        assert isinstance(metrics, RAGMetrics)  # noqa: S101
        assert metrics.total_requests >= 0  # noqa: S101
        assert metrics.successful_requests >= 0  # noqa: S101
        assert metrics.failed_requests >= 0  # noqa: S101
        assert metrics.avg_retrieval_time >= 0.0  # noqa: S101
        assert metrics.avg_processing_time >= 0.0  # noqa: S101
        assert metrics.avg_total_time >= 0.0  # noqa: S101

    def test_validate_request(self, rag_service, sample_config):
        """Test request validation."""
        # Valid request
        valid_request = RAGRequest(query="valid query", conversation_id="test")
        rag_service._validate_request(valid_request, sample_config)

        # Invalid request - empty query
        invalid_request = RAGRequest(query="", conversation_id="test")
        with pytest.raises(ValidationError):
            rag_service._validate_request(invalid_request, sample_config)

        # Invalid request - too short query
        short_request = RAGRequest(query="ab", conversation_id="test")
        with pytest.raises(ValidationError):
            rag_service._validate_request(short_request, sample_config)

    def test_create_cache_key(self, rag_service, sample_request, sample_config):
        """Test cache key creation."""
        cache_key = rag_service._create_cache_key(sample_request, sample_config)

        assert isinstance(cache_key, str)  # noqa: S101
        assert len(cache_key) == 32  # noqa: S101

    @pytest.mark.asyncio
    async def test_cache_operations(self, rag_service):
        """Test cache operations."""
        cache_key = "test_key"
        test_data = {"test": "data"}

        # Test cache set
        with (
            patch.object(rag_service, "_cache_enabled", new=True),
            patch("app.services.rag_service.cache_service.set", return_value=True),
        ):
            await rag_service._cache_result(cache_key, test_data)

        # Test cache get
        with (
            patch.object(rag_service, "_cache_enabled", new=True),
            patch("app.services.rag_service.cache_service.get", return_value=test_data),
        ):
            result = await rag_service._get_cached_result(cache_key)
            assert result == test_data  # noqa: S101

    def test_calculate_content_similarity(self, rag_service):
        """Test content similarity calculation."""
        content1 = "This is a test message about API authentication"
        content2 = "This is another test message about API authentication"
        content3 = "This is a completely different message about databases"

        similarity1 = rag_service._calculate_content_similarity(content1, content2)
        similarity2 = rag_service._calculate_content_similarity(content1, content3)

        assert similarity1 > similarity2  # noqa: S101
        assert 0.0 <= similarity1 <= 1.0  # noqa: S101
        assert 0.0 <= similarity2 <= 1.0  # noqa: S101

    def test_calculate_diversity_penalty(self, rag_service):
        """Test diversity penalty calculation."""
        result = RAGResult(
            content="test content",
            source="source1",
            source_type="document",
            source_id="1",
            similarity_score=0.8,
            relevance_score=0.7,
            ranking_score=0.0,
            token_count=10,
        )

        all_results = [
            result,
            RAGResult(
                content="very similar test content",
                source="source2",
                source_type="document",
                source_id="2",
                similarity_score=0.8,
                relevance_score=0.7,
                ranking_score=0.0,
                token_count=10,
            ),
        ]

        penalty = rag_service._calculate_diversity_penalty(result, all_results)

        assert 0.0 <= penalty <= 1.0  # noqa: S101

    def test_format_knowledge_results(self, rag_service):
        """Test knowledge results formatting."""
        raw_results = [
            {
                "content": "test content",
                "id": "1",
                "score": 0.8,
                "chunk_index": 0,
                "created_at": datetime.now(tz=UTC),
                "metadata": {"test": "data"},
            },
        ]

        formatted = rag_service._format_knowledge_results(raw_results)

        assert len(formatted) == 1  # noqa: S101
        assert formatted[0]["content"] == "test content"  # noqa: S101
        assert formatted[0]["source"] == "knowledge_base"  # noqa: S101
        assert formatted[0]["source_type"] == "document"  # noqa: S101
        assert formatted[0]["source_id"] == "1"  # noqa: S101
        assert formatted[0]["similarity_score"] == 0.8  # noqa: S101

    def test_format_conversation_results(self, rag_service):
        """Test conversation results formatting."""
        raw_results = [
            {
                "content": "conversation content",
                "message_id": "msg1",
                "score": 0.7,
                "created_at": datetime.now(tz=UTC),
                "metadata": {"user_id": "user1"},
            },
        ]

        formatted = rag_service._format_conversation_results(raw_results)

        assert len(formatted) == 1  # noqa: S101
        assert formatted[0]["content"] == "conversation content"  # noqa: S101
        assert formatted[0]["source"] == "conversation"  # noqa: S101
        assert formatted[0]["source_type"] == "message"  # noqa: S101
        assert formatted[0]["source_id"] == "msg1"  # noqa: S101
        assert formatted[0]["similarity_score"] == 0.7  # noqa: S101
