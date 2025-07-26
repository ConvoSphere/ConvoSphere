"""
Test configuration and fixtures.

This module provides common test fixtures and configuration for all tests.
"""

import os
import tempfile
from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Create a minimal test app
app = FastAPI(title="Test API", version="1.0.0")
from app.core.config import get_settings
from app.core.database import get_db
from app.models.base import Base
from app.models.knowledge import Document, DocumentProcessingJob, Tag
from app.models.user import User

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    # Clean up
    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session: Session) -> User:
    """Create a test admin user."""
    from app.models.user import UserRole

    admin_user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password="hashed_password",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    return admin_user


@pytest.fixture
def test_document(db_session: Session, test_user: User) -> Document:
    """Create a test document."""
    document = Document(
        user_id=test_user.id,
        title="Test Document",
        description="A test document",
        file_name="test.pdf",
        file_path="/path/to/test.pdf",
        file_type="pdf",
        file_size=1024,
        mime_type="application/pdf",
        author="Test Author",
        source="Test Source",
        language="en",
        year=2024,
        keywords=["test", "document"],
        document_type="pdf",
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


@pytest.fixture
def test_documents(db_session: Session, test_user: User) -> list[Document]:
    """Create multiple test documents."""
    documents = []

    # PDF document
    doc1 = Document(
        user_id=test_user.id,
        title="PDF Document",
        description="A PDF document",
        file_name="doc1.pdf",
        file_path="/path/to/doc1.pdf",
        file_type="pdf",
        file_size=1024,
        mime_type="application/pdf",
        author="Author 1",
        year=2024,
        language="en",
        document_type="pdf",
    )

    # Word document
    doc2 = Document(
        user_id=test_user.id,
        title="Word Document",
        description="A Word document",
        file_name="doc2.docx",
        file_path="/path/to/doc2.docx",
        file_type="docx",
        file_size=2048,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        author="Author 2",
        year=2023,
        language="de",
        document_type="document",
    )

    # Text document
    doc3 = Document(
        user_id=test_user.id,
        title="Text Document",
        description="A text document",
        file_name="doc3.txt",
        file_path="/path/to/doc3.txt",
        file_type="txt",
        file_size=512,
        mime_type="text/plain",
        author="Author 3",
        year=2024,
        language="en",
        document_type="text",
    )

    documents = [doc1, doc2, doc3]
    db_session.add_all(documents)
    db_session.commit()

    for doc in documents:
        db_session.refresh(doc)

    return documents


@pytest.fixture
def test_tags(db_session: Session) -> list[Tag]:
    """Create test tags."""
    tags = []

    tag1 = Tag(
        name="important",
        description="Important documents",
        color="#FF0000",
        usage_count=5,
    )

    tag2 = Tag(
        name="project",
        description="Project documents",
        color="#00FF00",
        usage_count=3,
    )

    tag3 = Tag(
        name="test",
        description="Test documents",
        color="#0000FF",
        usage_count=2,
    )

    tag4 = Tag(
        name="archive",
        description="Archived documents",
        color="#FFFF00",
        usage_count=1,
        is_system=True,
    )

    tags = [tag1, tag2, tag3, tag4]
    db_session.add_all(tags)
    db_session.commit()

    for tag in tags:
        db_session.refresh(tag)

    return tags


@pytest.fixture
def test_document_with_tags(
    db_session: Session,
    test_user: User,
    test_tags: list[Tag],
) -> Document:
    """Create a test document with tags."""
    document = Document(
        user_id=test_user.id,
        title="Tagged Document",
        description="A document with tags",
        file_name="tagged.pdf",
        file_path="/path/to/tagged.pdf",
        file_type="pdf",
        file_size=1024,
        mime_type="application/pdf",
        author="Test Author",
        year=2024,
        language="en",
        document_type="pdf",
    )

    # Add tags to document
    document.tags.append(test_tags[0])  # important
    document.tags.append(test_tags[1])  # project

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    return document


@pytest.fixture
def test_processing_job(
    db_session: Session,
    test_user: User,
    test_document: Document,
) -> DocumentProcessingJob:
    """Create a test processing job."""
    job = DocumentProcessingJob(
        document_id=test_document.id,
        user_id=test_user.id,
        job_type="process",
        priority=5,
        processing_engine="traditional",
        processing_options={"chunk_size": 500},
        total_steps=3,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def test_processing_jobs(
    db_session: Session,
    test_user: User,
    test_document: Document,
) -> list[DocumentProcessingJob]:
    """Create multiple test processing jobs."""
    jobs = []

    # Pending job
    job1 = DocumentProcessingJob(
        document_id=test_document.id,
        user_id=test_user.id,
        job_type="process",
        status="pending",
        priority=5,
    )

    # Running job
    job2 = DocumentProcessingJob(
        document_id=test_document.id,
        user_id=test_user.id,
        job_type="reprocess",
        status="running",
        priority=3,
        progress=0.5,
        current_step="Processing document",
    )

    # Completed job
    job3 = DocumentProcessingJob(
        document_id=test_document.id,
        user_id=test_user.id,
        job_type="process",
        status="completed",
        priority=1,
        progress=1.0,
        current_step="Completed",
    )

    # Failed job
    job4 = DocumentProcessingJob(
        document_id=test_document.id,
        user_id=test_user.id,
        job_type="process",
        status="failed",
        priority=2,
        error_message="Processing failed",
        retry_count=3,
    )

    jobs = [job1, job2, job3, job4]
    db_session.add_all(jobs)
    db_session.commit()

    for job in jobs:
        db_session.refresh(job)

    return jobs


@pytest.fixture
def temp_upload_dir():
    """Create a temporary upload directory."""
    temp_dir = tempfile.mkdtemp()

    # Override upload directory setting
    original_upload_dir = get_settings().UPLOAD_DIR
    get_settings().UPLOAD_DIR = temp_dir

    yield temp_dir

    # Clean up
    import shutil

    shutil.rmtree(temp_dir)
    get_settings().UPLOAD_DIR = original_upload_dir


@pytest.fixture
def mock_weaviate_service():
    """Mock Weaviate service."""
    with pytest.MonkeyPatch().context() as m:
        mock_service = Mock()
        mock_service.search_documents.return_value = [
            {
                "id": "test-chunk-1",
                "content": "Test search result content",
                "score": 0.85,
                "document_id": "test-doc-1",
                "document_title": "Test Document",
                "author": "Test Author",
                "language": "en",
                "year": 2024,
            },
        ]
        mock_service.search_conversations.return_value = [
            {
                "id": "test-conv-1",
                "content": "Test conversation content",
                "score": 0.75,
                "conversation_id": "conv-1",
            },
        ]
        mock_service.add_document_chunk.return_value = True
        mock_service.delete_document_chunks.return_value = True

        m.setattr(
            "app.services.knowledge_service.WeaviateService",
            lambda: mock_service,
        )
        yield mock_service


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service."""
    with pytest.MonkeyPatch().context() as m:
        mock_service = Mock()
        mock_service.generate_single_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_service.generate_embeddings.return_value = [
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.6, 0.7, 0.8, 0.9, 1.0],
        ]

        m.setattr("app.services.knowledge_service.embedding_service", mock_service)
        yield mock_service


@pytest.fixture
def mock_document_processor():
    """Mock document processor."""
    with pytest.MonkeyPatch().context() as m:
        mock_processor = Mock()
        mock_processor.process_document.return_value = {
            "success": True,
            "text": "Processed document text",
            "chunks": [
                {
                    "content": "First chunk content",
                    "token_count": 5,
                    "chunk_type": "text",
                    "page_number": 1,
                    "start_word": 0,
                    "end_word": 5,
                },
                {
                    "content": "Second chunk content",
                    "token_count": 4,
                    "chunk_type": "text",
                    "page_number": 1,
                    "start_word": 5,
                    "end_word": 9,
                },
            ],
            "metadata": {
                "processing_engine": "traditional",
                "page_count": 1,
                "word_count": 9,
                "character_count": 45,
            },
        }

        m.setattr("app.services.knowledge_service.document_processor", mock_processor)
        yield mock_processor


@pytest.fixture
def mock_ai_service():
    """Mock AI service."""
    with pytest.MonkeyPatch().context() as m:
        mock_service = Mock()
        mock_service.generate_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]

        m.setattr("app.services.knowledge_service.AIService", lambda: mock_service)
        yield mock_service


@pytest.fixture
def mock_background_job_service():
    """Mock background job service."""
    with pytest.MonkeyPatch().context() as m:
        mock_service = Mock()
        mock_service.schedule_job.return_value = True
        mock_service.get_job_status.return_value = {
            "id": "test-job-1",
            "status": "pending",
            "progress": 0.0,
            "current_step": "Waiting in queue",
        }
        mock_service.get_running_jobs.return_value = ["test-job-1"]
        mock_service.cancel_job.return_value = True

        m.setattr(
            "app.services.background_job_service.background_job_service",
            mock_service,
        )
        yield mock_service


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        # Create a minimal PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF\n"
        temp_file.write(pdf_content)
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    os.unlink(temp_file_path)


@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        text_content = b"This is a sample text file for testing purposes.\nIt contains multiple lines of text.\nThis will be used to test document processing."
        temp_file.write(text_content)
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    os.unlink(temp_file_path)


@pytest.fixture
def sample_word_file():
    """Create a sample Word document file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
        # Create a minimal DOCX file (ZIP format with Office Open XML structure)
        import zipfile

        with zipfile.ZipFile(temp_file, "w") as zip_file:
            # Add minimal required files for a DOCX
            zip_file.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
            )
            zip_file.writestr(
                "word/document.xml",
                '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Test Word Document Content</w:t></w:r></w:p></w:body></w:document>',
            )
            zip_file.writestr(
                "_rels/.rels",
                '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
            )

        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    os.unlink(temp_file_path)


# Test data fixtures
@pytest.fixture
def sample_search_queries(db_session: Session, test_user: User):
    """Create sample search queries for testing."""
    from app.models.knowledge import SearchQuery

    queries = []

    query1 = SearchQuery(
        user_id=test_user.id,
        query="machine learning",
        query_type="knowledge",
        result_count=15,
        execution_time=0.5,
    )

    query2 = SearchQuery(
        user_id=test_user.id,
        query="artificial intelligence",
        query_type="knowledge",
        result_count=8,
        execution_time=0.3,
    )

    query3 = SearchQuery(
        user_id=test_user.id,
        query="How does AI work?",
        query_type="conversation",
        result_count=5,
        execution_time=0.2,
    )

    queries = [query1, query2, query3]
    db_session.add_all(queries)
    db_session.commit()

    for query in queries:
        db_session.refresh(query)

    return queries


@pytest.fixture
def sample_document_chunks(db_session: Session, test_document: Document):
    """Create sample document chunks for testing."""
    from app.models.knowledge import DocumentChunk

    chunks = []

    chunk1 = DocumentChunk(
        document_id=test_document.id,
        content="This is the first chunk of the document.",
        chunk_index=0,
        chunk_size=35,
        token_count=8,
        chunk_type="text",
        page_number=1,
        section_title="Introduction",
    )

    chunk2 = DocumentChunk(
        document_id=test_document.id,
        content="This is the second chunk with different content.",
        chunk_index=1,
        chunk_size=42,
        token_count=9,
        chunk_type="text",
        page_number=1,
        section_title="Introduction",
    )

    chunk3 = DocumentChunk(
        document_id=test_document.id,
        content="This chunk contains a table with data.",
        chunk_index=2,
        chunk_size=32,
        token_count=7,
        chunk_type="table",
        page_number=2,
        table_id="table_1",
    )

    chunks = [chunk1, chunk2, chunk3]
    db_session.add_all(chunks)
    db_session.commit()

    for chunk in chunks:
        db_session.refresh(chunk)

    return chunks
