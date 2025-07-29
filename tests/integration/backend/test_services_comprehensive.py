import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.ai_service import AIService
from backend.app.services.assistant_service import AssistantService
from backend.app.services.conversation_service import ConversationService
from backend.app.services.document import DocumentService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.knowledge_service import KnowledgeService
from backend.app.services.performance_monitor import PerformanceMonitor
from backend.app.services.tool_service import ToolService
from backend.app.services.user_service import UserService


class TestUserServiceComprehensive:
    """Comprehensive tests for UserService."""

    @pytest.fixture
    def user_service(self):
        return UserService()

    @pytest.fixture
    def sample_user_data(self):
        return {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            # Mock query methods to return None (no existing users)
            mock_query = MagicMock()
            mock_query.filter.return_value.first.return_value = None
            mock_db.query.return_value = mock_query

            # Mock the get_user_by_email and get_user_by_username methods
            with (
                patch.object(user_service, "get_user_by_email", return_value=None),
                patch.object(user_service, "get_user_by_username", return_value=None),
            ):
                result = user_service.create_user(
                    email=sample_user_data["email"],
                    username=sample_user_data["username"],
                    password="TestPassword123!",
                    full_name=sample_user_data["full_name"],
                )

                assert result is not None
                assert result.email == sample_user_data["email"]

    def test_create_user_duplicate_email(self, user_service, sample_user_data):
        """Test user creation with duplicate email."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.add.side_effect = Exception("Duplicate email")

            with pytest.raises(Exception):
                user_service.create_user(
                    email=sample_user_data["email"],
                    username=sample_user_data["username"],
                    password="TestPassword123!",
                    full_name=sample_user_data["full_name"],
                )

    def test_get_user_by_id(self, user_service, sample_user_data):
        """Test getting user by ID."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )

            result = user_service.get_user_by_id(sample_user_data["id"])

            assert result == sample_user_data

    def test_get_user_by_email(self, user_service, sample_user_data):
        """Test getting user by email."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )

            result = user_service.get_user_by_email(sample_user_data["email"])

            assert result == sample_user_data

    def test_update_user(self, user_service, sample_user_data):
        """Test updating user."""
        update_data = {"full_name": "Updated Name"}

        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )
            mock_db.commit.return_value = None

            result = user_service.update_user(sample_user_data["id"], update_data)

            assert result is not None

    def test_delete_user(self, user_service, sample_user_data):
        """Test deleting user."""
        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_user_data
            )
            mock_db.delete.return_value = None
            mock_db.commit.return_value = None

            result = user_service.delete_user(sample_user_data["id"])

            assert result is True

    def test_get_users_paginated(self, user_service):
        """Test getting paginated users."""
        users = [
            {"id": "1", "email": "user1@test.com"},
            {"id": "2", "email": "user2@test.com"},
        ]

        with patch.object(user_service, "db") as mock_db:
            mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = users
            mock_db.query.return_value.count.return_value = 2

            result = user_service.get_users(skip=0, limit=10)

            assert len(result) == 2

    def test_authenticate_user(self, user_service, sample_user_data):
        """Test user authentication."""
        with patch.object(user_service, "get_user_by_email") as mock_get:
            mock_get.return_value = sample_user_data

            with patch("app.services.user_service.verify_password") as mock_verify:
                mock_verify.return_value = True

                result = user_service.authenticate_user(
                    email=sample_user_data["email"],
                    password="TestPassword123!",
                )

                assert result == sample_user_data

    def test_authenticate_user_invalid_password(self, user_service, sample_user_data):
        """Test user authentication with invalid password."""
        with patch.object(user_service, "get_user_by_email") as mock_get:
            mock_get.return_value = sample_user_data

            with patch("app.services.user_service.verify_password") as mock_verify:
                mock_verify.return_value = False

                result = user_service.authenticate_user(
                    email=sample_user_data["email"],
                    password="WrongPassword",
                )

                assert result is None


class TestAssistantServiceComprehensive:
    """Comprehensive tests for AssistantService."""

    @pytest.fixture
    def assistant_service(self):
        return AssistantService()

    @pytest.fixture
    def sample_assistant_data(self):
        return {
            "id": str(uuid.uuid4()),
            "name": "Test Assistant",
            "description": "A test assistant",
            "model": "gpt-4",
            "instructions": "You are a helpful assistant.",
            "user_id": str(uuid.uuid4()),
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    def test_create_assistant(self, assistant_service, sample_assistant_data):
        """Test creating an assistant."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            result = assistant_service.create_assistant(
                name=sample_assistant_data["name"],
                description=sample_assistant_data["description"],
                model=sample_assistant_data["model"],
                instructions=sample_assistant_data["instructions"],
                user_id=sample_assistant_data["user_id"],
            )

            assert result is not None
            assert result.name == sample_assistant_data["name"]

    def test_get_assistant_by_id(self, assistant_service, sample_assistant_data):
        """Test getting assistant by ID."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_assistant_data
            )

            result = assistant_service.get_assistant_by_id(sample_assistant_data["id"])

            assert result == sample_assistant_data

    def test_get_assistants_by_user(self, assistant_service):
        """Test getting assistants by user."""
        assistants = [
            {"id": "1", "name": "Assistant 1"},
            {"id": "2", "name": "Assistant 2"},
        ]

        with patch.object(assistant_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.all.return_value = assistants

            result = assistant_service.get_assistants_by_user("user123")

            assert len(result) == 2

    def test_update_assistant(self, assistant_service, sample_assistant_data):
        """Test updating assistant."""
        update_data = {"name": "Updated Assistant"}

        with patch.object(assistant_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_assistant_data
            )
            mock_db.commit.return_value = None

            result = assistant_service.update_assistant(
                sample_assistant_data["id"],
                update_data,
            )

            assert result is not None

    def test_delete_assistant(self, assistant_service, sample_assistant_data):
        """Test deleting assistant."""
        with patch.object(assistant_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_assistant_data
            )
            mock_db.delete.return_value = None
            mock_db.commit.return_value = None

            result = assistant_service.delete_assistant(sample_assistant_data["id"])

            assert result is True


class TestConversationServiceComprehensive:
    """Comprehensive tests for ConversationService."""

    @pytest.fixture
    def conversation_service(self):
        return ConversationService()

    @pytest.fixture
    def sample_conversation_data(self):
        return {
            "id": str(uuid.uuid4()),
            "title": "Test Conversation",
            "user_id": str(uuid.uuid4()),
            "assistant_id": str(uuid.uuid4()),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    def test_create_conversation(self, conversation_service, sample_conversation_data):
        """Test creating a conversation."""
        with patch.object(conversation_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            # Create ConversationCreate object
            from backend.app.schemas.conversation import ConversationCreate

            conversation_data = ConversationCreate(
                title=sample_conversation_data["title"],
                user_id=sample_conversation_data["user_id"],
                assistant_id=sample_conversation_data["assistant_id"],
            )

            result = conversation_service.create_conversation(conversation_data)

            assert result is not None
            assert result["title"] == sample_conversation_data["title"]

    def test_get_conversation_by_id(
        self,
        conversation_service,
        sample_conversation_data,
    ):
        """Test getting conversation by ID."""
        with patch.object(conversation_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_conversation_data
            )

            result = conversation_service.get_conversation_by_id(
                sample_conversation_data["id"],
            )

            assert result == sample_conversation_data

    def test_get_conversations_by_user(self, conversation_service):
        """Test getting conversations by user."""
        conversations = [
            {"id": "1", "title": "Conversation 1"},
            {"id": "2", "title": "Conversation 2"},
        ]

        with patch.object(conversation_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.all.return_value = (
                conversations
            )

            result = conversation_service.get_conversations_by_user("user123")

            assert len(result) == 2

    def test_add_message_to_conversation(self, conversation_service):
        """Test adding message to conversation."""
        message_data = {
            "content": "Hello, how are you?",
            "role": "user",
            "conversation_id": "conv123",
        }

        with patch.object(conversation_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            result = conversation_service.add_message(
                conversation_id=message_data["conversation_id"],
                content=message_data["content"],
                role=message_data["role"],
            )

            assert result is not None
            assert result.content == message_data["content"]

    def test_get_messages_by_conversation(self, conversation_service):
        """Test getting messages by conversation."""
        messages = [
            {"id": "1", "content": "Hello", "role": "user"},
            {"id": "2", "content": "Hi there!", "role": "assistant"},
        ]

        with patch.object(conversation_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.all.return_value = messages

            result = conversation_service.get_messages_by_conversation("conv123")

            assert len(result) == 2


class TestToolServiceComprehensive:
    """Comprehensive tests for ToolService."""

    @pytest.fixture
    def tool_service(self):
        return ToolService()

    @pytest.fixture
    def sample_tool_data(self):
        return {
            "id": str(uuid.uuid4()),
            "name": "Test Tool",
            "description": "A test tool",
            "type": "function",
            "config": {"function_name": "test_function"},
            "user_id": str(uuid.uuid4()),
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    def test_create_tool(self, tool_service, sample_tool_data):
        """Test creating a tool."""
        with patch.object(tool_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            result = tool_service.create_tool(
                name=sample_tool_data["name"],
                description=sample_tool_data["description"],
                type=sample_tool_data["type"],
                config=sample_tool_data["config"],
                user_id=sample_tool_data["user_id"],
            )

            assert result is not None
            assert result.name == sample_tool_data["name"]

    def test_get_tool_by_id(self, tool_service, sample_tool_data):
        """Test getting tool by ID."""
        with patch.object(tool_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_tool_data
            )

            result = tool_service.get_tool_by_id(sample_tool_data["id"])

            assert result == sample_tool_data

    def test_get_tools_by_user(self, tool_service):
        """Test getting tools by user."""
        tools = [
            {"id": "1", "name": "Tool 1"},
            {"id": "2", "name": "Tool 2"},
        ]

        with patch.object(tool_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.all.return_value = tools

            result = tool_service.get_tools_by_user("user123")

            assert len(result) == 2

    def test_execute_tool(self, tool_service, sample_tool_data):
        """Test executing a tool."""
        parameters = {"param1": "value1"}

        with patch.object(tool_service, "get_tool_by_id") as mock_get:
            mock_get.return_value = sample_tool_data

            with patch(
                "app.services.tool_service.enhanced_tool_executor.execute",
            ) as mock_execute:
                mock_execute.return_value = {"result": "success"}

                result = tool_service.execute_tool(sample_tool_data["id"], parameters)

                assert result == {"result": "success"}


class TestKnowledgeServiceComprehensive:
    """Comprehensive tests for KnowledgeService."""

    @pytest.fixture
    def knowledge_service(self):
        return KnowledgeService()

    @pytest.fixture
    def sample_document_data(self):
        return {
            "id": str(uuid.uuid4()),
            "filename": "test.pdf",
            "file_path": "/path/to/test.pdf",
            "file_size": 1024,
            "file_type": "application/pdf",
            "user_id": str(uuid.uuid4()),
            "status": "processed",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    def test_process_document(self, knowledge_service, sample_document_data):
        """Test processing a document."""
        with patch.object(knowledge_service, "db") as mock_db:
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            with patch(
                "app.services.knowledge_service.document_processor.process",
            ) as mock_process:
                mock_process.return_value = {"chunks": ["chunk1", "chunk2"]}

                result = knowledge_service.process_document(
                    filename=sample_document_data["filename"],
                    file_path=sample_document_data["file_path"],
                    file_size=sample_document_data["file_size"],
                    file_type=sample_document_data["file_type"],
                    user_id=sample_document_data["user_id"],
                )

                assert result is not None
                assert result.filename == sample_document_data["filename"]

    def test_search_documents(self, knowledge_service):
        """Test searching documents."""
        search_results = [
            {"id": "1", "content": "test result 1", "score": 0.9},
            {"id": "2", "content": "test result 2", "score": 0.8},
        ]

        with patch(
            "app.services.knowledge_service.embedding_service.search",
        ) as mock_search:
            mock_search.return_value = search_results

            result = knowledge_service.search("test query", user_id="user123")

            assert len(result) == 2
            assert result[0]["score"] == 0.9

    def test_get_documents_by_user(self, knowledge_service):
        """Test getting documents by user."""
        documents = [
            {"id": "1", "filename": "doc1.pdf"},
            {"id": "2", "filename": "doc2.pdf"},
        ]

        with patch.object(knowledge_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.all.return_value = documents

            result = knowledge_service.get_documents_by_user("user123")

            assert len(result) == 2

    def test_delete_document(self, knowledge_service, sample_document_data):
        """Test deleting a document."""
        with patch.object(knowledge_service, "db") as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = (
                sample_document_data
            )
            mock_db.delete.return_value = None
            mock_db.commit.return_value = None

            result = knowledge_service.delete_document(sample_document_data["id"])

            assert result is True


class TestAIServiceComprehensive:
    """Comprehensive tests for AIService."""

    @pytest.fixture
    def ai_service(self):
        return AIService()

    def test_generate_response(self, ai_service):
        """Test generating AI response."""
        messages = [
            {"role": "user", "content": "Hello, how are you?"},
        ]

        with patch("app.services.ai_service.litellm.completion") as mock_completion:
            mock_completion.return_value = {
                "choices": [{"message": {"content": "I'm doing well, thank you!"}}],
            }

            result = ai_service.generate_response(messages, model="gpt-4")

            assert result is not None
            assert "I'm doing well" in result

    def test_generate_response_with_tools(self, ai_service):
        """Test generating AI response with tools."""
        messages = [
            {"role": "user", "content": "What's the weather like?"},
        ]
        tools = [
            {"name": "get_weather", "description": "Get weather information"},
        ]

        with patch("app.services.ai_service.litellm.completion") as mock_completion:
            mock_completion.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "Let me check the weather for you.",
                            "tool_calls": [{"name": "get_weather"}],
                        },
                    },
                ],
            }

            result = ai_service.generate_response_with_tools(
                messages,
                tools,
                model="gpt-4",
            )

            assert result is not None
            assert "tool_calls" in str(result)

    def test_embed_text(self, ai_service):
        """Test embedding text."""
        text = "This is a test text for embedding."

        with patch("app.services.ai_service.litellm.embedding") as mock_embedding:
            mock_embedding.return_value = {
                "data": [{"embedding": [0.1, 0.2, 0.3]}],
            }

            result = ai_service.embed_text(text, model="text-embedding-ada-002")

            assert result is not None
            assert len(result) == 3

    def test_chat_completion(self, ai_service):
        """Test chat completion."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

        with patch("app.services.ai_service.litellm.completion") as mock_completion:
            mock_completion.return_value = {
                "choices": [{"message": {"content": "I'm doing great!"}}],
            }

            result = ai_service.chat_completion(messages, model="gpt-4")

            assert result is not None
            assert "I'm doing great" in result


class TestEmbeddingServiceComprehensive:
    """Comprehensive tests for EmbeddingService."""

    @pytest.fixture
    def embedding_service(self):
        return EmbeddingService()

    def test_create_embedding(self, embedding_service):
        """Test creating embedding."""
        text = "Test text for embedding"

        with patch.object(embedding_service, "ai_service") as mock_ai:
            mock_ai.embed_text.return_value = [0.1, 0.2, 0.3]

            result = embedding_service.create_embedding(text)

            assert result is not None
            assert len(result) == 3

    def test_search_similar(self, embedding_service):
        """Test searching similar embeddings."""
        query = "test query"
        embeddings = [
            {"id": "1", "embedding": [0.1, 0.2, 0.3], "content": "result 1"},
            {"id": "2", "embedding": [0.4, 0.5, 0.6], "content": "result 2"},
        ]

        with patch.object(embedding_service, "create_embedding") as mock_create:
            mock_create.return_value = [0.1, 0.2, 0.3]

            with patch.object(embedding_service, "weaviate_client") as mock_weaviate:
                mock_weaviate.search.return_value = embeddings

                result = embedding_service.search_similar(query, limit=5)

                assert len(result) == 2

    def test_store_embedding(self, embedding_service):
        """Test storing embedding."""
        embedding_data = {
            "content": "test content",
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"source": "test"},
        }

        with patch.object(embedding_service, "weaviate_client") as mock_weaviate:
            mock_weaviate.store.return_value = "embedding_id"

            result = embedding_service.store_embedding(
                embedding_data["content"],
                embedding_data["embedding"],
                embedding_data["metadata"],
            )

            assert result == "embedding_id"


class TestDocumentProcessorComprehensive:
    """Comprehensive tests for DocumentService."""

    @pytest.fixture
    def document_processor(self):
        return DocumentService()

    def test_process_pdf(self, document_processor):
        """Test processing PDF document."""
        file_path = "/path/to/test.pdf"

        with patch("app.services.document_processor.PyPDF2.PdfReader") as mock_pdf:
            mock_pdf.return_value.pages = [
                MagicMock(extract_text=lambda: "PDF content"),
            ]

            result = document_processor.process_pdf(file_path)

            assert result is not None
            assert "PDF content" in result

    def test_process_docx(self, document_processor):
        """Test processing DOCX document."""
        file_path = "/path/to/test.docx"

        with patch("app.services.document_processor.Document") as mock_docx:
            mock_docx.return_value.paragraphs = [MagicMock(text="DOCX content")]

            result = document_processor.process_docx(file_path)

            assert result is not None
            assert "DOCX content" in result

    def test_process_txt(self, document_processor):
        """Test processing TXT document."""
        file_path = "/path/to/test.txt"

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                "TXT content"
            )

            result = document_processor.process_txt(file_path)

            assert result is not None
            assert "TXT content" in result

    def test_chunk_text(self, document_processor):
        """Test chunking text."""
        text = "This is a long text that needs to be chunked into smaller pieces for processing."

        result = document_processor.chunk_text(text, chunk_size=20, overlap=5)

        assert len(result) > 1
        assert all(len(chunk) <= 20 for chunk in result)


class TestPerformanceMonitorComprehensive:
    """Comprehensive tests for PerformanceMonitor."""

    @pytest.fixture
    def performance_monitor(self):
        return PerformanceMonitor()

    def test_get_stats(self, performance_monitor):
        """Test getting performance stats."""
        result = performance_monitor.get_stats()

        assert result is not None
        assert "current_metrics" in result
        assert "current_alerts" in result
        assert "active_alerts" in result

    def test_record_metric(self, performance_monitor):
        """Test recording a performance metric."""
        from backend.app.services.performance_monitor import PerformanceMetric

        metric = PerformanceMetric(
            metric_name="test_metric",
            metric_type="counter",
            value=42,
        )

        performance_monitor.record_metric(metric)

        # Check that metric was recorded
        stats = performance_monitor.get_stats()
        assert stats["current_metrics"] > 0

    def test_record_api_request(self, performance_monitor):
        """Test recording an API request metric."""
        from backend.app.services.performance_monitor import APIMetric

        api_metric = APIMetric(
            endpoint="/api/test",
            method="GET",
            status_code=200,
            response_time=0.1,
        )

        performance_monitor.record_api_request(api_metric)

        # Check that metric was recorded (API metrics are stored separately)
        assert len(performance_monitor.api_metrics) > 0

    def test_record_cache_operation(self, performance_monitor):
        """Test recording a cache operation metric."""
        from backend.app.services.performance_monitor import CacheMetric

        cache_metric = CacheMetric(
            operation="get",
            namespace="test",
            key="test_key",
            operation_time=0.01,
            cache_hit=True,
        )

        performance_monitor.record_cache_operation(cache_metric)

        # Check that metric was recorded (cache metrics are stored separately)
        assert len(performance_monitor.cache_metrics) > 0

    def test_start_monitoring(self, performance_monitor):
        """Test starting performance monitoring."""
        with patch("threading.Thread") as mock_thread:
            mock_thread.return_value.start.return_value = None

            performance_monitor.start_monitoring()

            assert performance_monitor.monitoring_enabled is True

    def test_stop_monitoring(self, performance_monitor):
        """Test stopping performance monitoring."""
        performance_monitor.monitoring_enabled = True

        performance_monitor.stop_monitoring()

        assert performance_monitor.monitoring_enabled is False
