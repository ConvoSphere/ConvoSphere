"""
Tests for knowledge base services.

This module contains unit tests for the enhanced knowledge base services
including KnowledgeService, TagService, MetadataExtractor, and BackgroundJobService.
"""

import pytest
import uuid
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from sqlalchemy.orm import Session

# Mock external dependencies before importing services
import sys
from unittest.mock import Mock, MagicMock

# Mock external services
sys.modules['app.services.document_processor'] = Mock()
sys.modules['app.services.weaviate_service'] = Mock()
sys.modules['app.services.embedding_service'] = Mock()
sys.modules['app.services.ai_service'] = Mock()

# Now import the services
from app.services.knowledge_service import KnowledgeService, TagService, MetadataExtractor
from app.services.background_job_service import BackgroundJobService
from app.models.knowledge import Document, Tag, DocumentProcessingJob, DocumentStatus, DocumentType
from app.models.user import User


class TestTagService:
    """Test cases for TagService."""

    def test_normalize_tag_name(self, db_session: Session):
        """Test tag name normalization."""
        tag_service = TagService(db_session)
        
        assert tag_service.normalize_tag_name("  Test Tag  ") == "test tag"
        assert tag_service.normalize_tag_name("UPPERCASE") == "uppercase"
        assert tag_service.normalize_tag_name("Mixed-Case") == "mixed-case"
        assert tag_service.normalize_tag_name("   ") == ""

    def test_get_or_create_tag_new(self, db_session: Session):
        """Test creating a new tag."""
        tag_service = TagService(db_session)
        
        tag = tag_service.get_or_create_tag("new-tag")
        
        assert tag.name == "new-tag"
        assert tag.id is not None
        assert tag.usage_count == 0

    def test_get_or_create_tag_existing(self, db_session: Session):
        """Test getting an existing tag."""
        tag_service = TagService(db_session)
        
        # Create tag first
        tag1 = tag_service.get_or_create_tag("existing-tag")
        db_session.commit()
        
        # Get the same tag
        tag2 = tag_service.get_or_create_tag("existing-tag")
        
        assert tag1.id == tag2.id
        assert tag1.name == tag2.name

    def test_get_tags(self, db_session: Session, test_user: User):
        """Test getting tags for a user's documents."""
        tag_service = TagService(db_session)
        
        # Create tags
        tag1 = Tag(name="important")
        tag2 = Tag(name="project")
        tag3 = Tag(name="unused")
        db_session.add_all([tag1, tag2, tag3])
        
        # Create document with tags
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024
        )
        document.tags.append(tag1)
        document.tags.append(tag2)
        tag1.usage_count = 2
        tag2.usage_count = 1
        
        db_session.add(document)
        db_session.commit()
        
        # Get tags for user
        tags = tag_service.get_tags(str(test_user.id), limit=10)
        
        assert len(tags) == 2
        assert tags[0].name == "important"  # Higher usage count first
        assert tags[1].name == "project"

    def test_search_tags(self, db_session: Session, test_user: User):
        """Test searching tags by name."""
        tag_service = TagService(db_session)
        
        # Create tags
        tag1 = Tag(name="project-a")
        tag2 = Tag(name="project-b")
        tag3 = Tag(name="other")
        db_session.add_all([tag1, tag2, tag3])
        
        # Create document with project tags
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024
        )
        document.tags.append(tag1)
        document.tags.append(tag2)
        tag1.usage_count = 1
        tag2.usage_count = 1
        
        db_session.add(document)
        db_session.commit()
        
        # Search for project tags
        tags = tag_service.search_tags("project", str(test_user.id), limit=10)
        
        assert len(tags) == 2
        assert all("project" in tag.name for tag in tags)

    def test_delete_unused_tags(self, db_session: Session):
        """Test deleting unused tags."""
        tag_service = TagService(db_session)
        
        # Create used and unused tags
        used_tag = Tag(name="used", usage_count=1)
        unused_tag1 = Tag(name="unused1", usage_count=0)
        unused_tag2 = Tag(name="unused2", usage_count=0)
        
        db_session.add_all([used_tag, unused_tag1, unused_tag2])
        db_session.commit()
        
        # Delete unused tags
        deleted_count = tag_service.delete_unused_tags()
        
        assert deleted_count == 2
        
        # Check that used tag still exists
        remaining_tag = db_session.query(Tag).filter(Tag.name == "used").first()
        assert remaining_tag is not None
        
        # Check that unused tags are deleted
        deleted_tag = db_session.query(Tag).filter(Tag.name == "unused1").first()
        assert deleted_tag is None


class TestMetadataExtractor:
    """Test cases for MetadataExtractor."""

    def test_extract_pdf_metadata_success(self):
        """Test successful PDF metadata extraction."""
        with patch('app.services.knowledge_service.PyPDF2') as mock_pypdf2:
            # Mock PDF reader
            mock_reader = Mock()
            mock_reader.metadata = {
                '/Author': 'Test Author',
                '/Title': 'Test Title',
                '/Subject': 'Test Subject',
                '/CreationDate': 'D:20240101120000'
            }
            mock_reader.pages = [Mock(), Mock()]  # 2 pages
            
            mock_pypdf2.PdfReader.return_value = mock_reader
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"fake pdf content")
                temp_file_path = temp_file.name
            
            try:
                metadata = MetadataExtractor.extract_pdf_metadata(temp_file_path)
                
                assert metadata['author'] == 'Test Author'
                assert metadata['title'] == 'Test Title'
                assert metadata['subject'] == 'Test Subject'
                assert metadata['year'] == 2024
                assert metadata['page_count'] == 2
            finally:
                os.unlink(temp_file_path)

    def test_extract_pdf_metadata_no_metadata(self):
        """Test PDF metadata extraction with no metadata."""
        with patch('app.services.knowledge_service.PyPDF2') as mock_pypdf2:
            mock_reader = Mock()
            mock_reader.metadata = None
            mock_reader.pages = [Mock()]
            
            mock_pypdf2.PdfReader.return_value = mock_reader
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"fake pdf content")
                temp_file_path = temp_file.name
            
            try:
                metadata = MetadataExtractor.extract_pdf_metadata(temp_file_path)
                assert metadata == {}
            finally:
                os.unlink(temp_file_path)

    def test_extract_pdf_metadata_exception(self):
        """Test PDF metadata extraction with exception."""
        with patch('app.services.knowledge_service.PyPDF2', side_effect=ImportError):
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"fake pdf content")
                temp_file_path = temp_file.name
            
            try:
                metadata = MetadataExtractor.extract_pdf_metadata(temp_file_path)
                assert metadata == {}
            finally:
                os.unlink(temp_file_path)

    def test_extract_word_metadata_success(self):
        """Test successful Word document metadata extraction."""
        with patch('app.services.knowledge_service.Document') as mock_docx:
            # Mock document
            mock_doc = Mock()
            mock_doc.core_properties.author = 'Test Author'
            mock_doc.core_properties.title = 'Test Title'
            mock_doc.core_properties.subject = 'Test Subject'
            mock_doc.core_properties.created = datetime(2024, 1, 1)
            mock_doc.paragraphs = [Mock(text='Test paragraph')]
            
            mock_docx.return_value = mock_doc
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(b"fake docx content")
                temp_file_path = temp_file.name
            
            try:
                metadata = MetadataExtractor.extract_word_metadata(temp_file_path)
                
                assert metadata['author'] == 'Test Author'
                assert metadata['title'] == 'Test Title'
                assert metadata['subject'] == 'Test Subject'
                assert metadata['year'] == 2024
                assert metadata['word_count'] == 2  # "Test paragraph" = 2 words
            finally:
                os.unlink(temp_file_path)

    def test_detect_language_success(self):
        """Test successful language detection."""
        with patch('app.services.knowledge_service.detect') as mock_detect:
            mock_detect.return_value = 'en'
            
            language = MetadataExtractor.detect_language("This is English text")
            assert language == 'en'

    def test_detect_language_exception(self):
        """Test language detection with exception."""
        with patch('app.services.knowledge_service.detect', side_effect=Exception):
            language = MetadataExtractor.detect_language("Some text")
            assert language is None


class TestKnowledgeService:
    """Test cases for enhanced KnowledgeService."""

    def test_create_document_with_metadata(self, db_session: Session, test_user: User):
        """Test creating a document with enhanced metadata."""
        knowledge_service = KnowledgeService(db_session)
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                file_content = f.read()
            
            document = knowledge_service.create_document(
                user_id=str(test_user.id),
                title="Test Document",
                file_name="test.txt",
                file_content=file_content,
                description="A test document",
                tags=["important", "test"],
                metadata={"custom_field": "value"}
            )
            
            assert document.id is not None
            assert document.title == "Test Document"
            assert document.description == "A test document"
            assert document.file_type == "txt"
            assert document.document_type == DocumentType.TEXT
            assert len(document.tags) == 2
            assert document.tag_names == ["important", "test"]
            
        finally:
            os.unlink(temp_file_path)

    def test_determine_document_type(self, db_session: Session):
        """Test document type determination."""
        knowledge_service = KnowledgeService(db_session)
        
        # Test various file types
        assert knowledge_service._determine_document_type("pdf", "application/pdf") == DocumentType.PDF
        assert knowledge_service._determine_document_type("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document") == DocumentType.DOCUMENT
        assert knowledge_service._determine_document_type("txt", "text/plain") == DocumentType.TEXT
        assert knowledge_service._determine_document_type("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") == DocumentType.SPREADSHEET
        assert knowledge_service._determine_document_type("unknown", "application/octet-stream") == DocumentType.OTHER

    @patch('app.services.knowledge_service.MetadataExtractor')
    def test_extract_document_metadata(self, mock_metadata_extractor, db_session: Session):
        """Test document metadata extraction."""
        knowledge_service = KnowledgeService(db_session)
        
        # Mock metadata extraction
        mock_metadata_extractor.extract_pdf_metadata.return_value = {
            'author': 'Test Author',
            'year': 2024,
            'page_count': 10
        }
        mock_metadata_extractor.detect_language.return_value = 'en'
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"fake pdf content")
            temp_file_path = temp_file.name
        
        try:
            metadata = knowledge_service._extract_document_metadata(temp_file_path, "pdf")
            
            assert metadata['author'] == 'Test Author'
            assert metadata['year'] == 2024
            assert metadata['page_count'] == 10
            assert metadata['language'] == 'en'
        finally:
            os.unlink(temp_file_path)

    def test_get_documents_with_filters(self, db_session: Session, test_user: User):
        """Test getting documents with advanced filtering."""
        knowledge_service = KnowledgeService(db_session)
        
        # Create documents with different metadata
        doc1 = Document(
            user_id=test_user.id,
            title="PDF Document",
            file_name="doc1.pdf",
            file_path="/path/to/doc1.pdf",
            file_type="pdf",
            file_size=1024,
            document_type=DocumentType.PDF,
            author="Author 1",
            year=2024,
            language="en"
        )
        
        doc2 = Document(
            user_id=test_user.id,
            title="Word Document",
            file_name="doc2.docx",
            file_path="/path/to/doc2.docx",
            file_type="docx",
            file_size=2048,
            document_type=DocumentType.DOCUMENT,
            author="Author 2",
            year=2023,
            language="de"
        )
        
        db_session.add_all([doc1, doc2])
        db_session.commit()
        
        # Test filtering by document type
        documents, total = knowledge_service.get_documents(
            user_id=str(test_user.id),
            document_type="pdf"
        )
        assert len(documents) == 1
        assert documents[0].document_type == DocumentType.PDF
        
        # Test filtering by author
        documents, total = knowledge_service.get_documents(
            user_id=str(test_user.id),
            author="Author 1"
        )
        assert len(documents) == 1
        assert documents[0].author == "Author 1"
        
        # Test filtering by year
        documents, total = knowledge_service.get_documents(
            user_id=str(test_user.id),
            year=2024
        )
        assert len(documents) == 1
        assert documents[0].year == 2024
        
        # Test filtering by language
        documents, total = knowledge_service.get_documents(
            user_id=str(test_user.id),
            language="de"
        )
        assert len(documents) == 1
        assert documents[0].language == "de"

    def test_update_document_metadata(self, db_session: Session, test_user: User):
        """Test updating document metadata."""
        knowledge_service = KnowledgeService(db_session)
        
        # Create document
        document = Document(
            user_id=test_user.id,
            title="Original Title",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024
        )
        db_session.add(document)
        db_session.commit()
        
        # Update metadata
        updated_document = knowledge_service.update_document_metadata(
            document_id=str(document.id),
            user_id=str(test_user.id),
            title="Updated Title",
            author="New Author",
            year=2024,
            language="en",
            tags=["important", "updated"]
        )
        
        assert updated_document.title == "Updated Title"
        assert updated_document.author == "New Author"
        assert updated_document.year == 2024
        assert updated_document.language == "en"
        assert updated_document.tag_names == ["important", "updated"]

    def test_create_processing_job(self, db_session: Session, test_user: User):
        """Test creating a processing job."""
        knowledge_service = KnowledgeService(db_session)
        
        # Create document
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024
        )
        db_session.add(document)
        db_session.commit()
        
        # Create job
        job = knowledge_service.create_processing_job(
            document_id=str(document.id),
            user_id=str(test_user.id),
            job_type="process",
            priority=5,
            processing_options={"chunk_size": 500}
        )
        
        assert job.id is not None
        assert job.document_id == document.id
        assert job.user_id == test_user.id
        assert job.job_type == "process"
        assert job.priority == 5
        assert job.processing_options["chunk_size"] == 500
        assert job.status == "pending"

    def test_get_processing_jobs(self, db_session: Session, test_user: User):
        """Test getting processing jobs."""
        knowledge_service = KnowledgeService(db_session)
        
        # Create document
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024
        )
        db_session.add(document)
        db_session.commit()
        
        # Create jobs
        job1 = DocumentProcessingJob(
            document_id=document.id,
            user_id=test_user.id,
            job_type="process",
            status="pending"
        )
        job2 = DocumentProcessingJob(
            document_id=document.id,
            user_id=test_user.id,
            job_type="reprocess",
            status="completed"
        )
        db_session.add_all([job1, job2])
        db_session.commit()
        
        # Get all jobs
        jobs = knowledge_service.get_processing_jobs(str(test_user.id))
        assert len(jobs) == 2
        
        # Get jobs by status
        pending_jobs = knowledge_service.get_processing_jobs(str(test_user.id), status="pending")
        assert len(pending_jobs) == 1
        assert pending_jobs[0].status == "pending"

    @patch('app.services.knowledge_service.embedding_service')
    @patch('app.services.knowledge_service.WeaviateService')
    async def test_search_documents_with_filters(self, mock_weaviate, mock_embedding, db_session: Session, test_user: User):
        """Test searching documents with enhanced filtering."""
        knowledge_service = KnowledgeService(db_session)
        
        # Mock embedding service
        mock_embedding.generate_single_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        
        # Mock Weaviate service
        mock_weaviate_instance = Mock()
        mock_weaviate_instance.search_documents.return_value = [
            {"id": "1", "content": "Test result", "score": 0.8}
        ]
        mock_weaviate.return_value = mock_weaviate_instance
        
        # Test search with filters
        results = await knowledge_service.search_documents(
            query="test query",
            user_id=str(test_user.id),
            filters={
                "document_type": "pdf",
                "author": "Test Author",
                "language": "en",
                "year": 2024
            }
        )
        
        assert len(results) == 1
        assert results[0]["content"] == "Test result"
        
        # Verify Weaviate was called with correct filters
        mock_weaviate_instance.search_documents.assert_called_once()
        call_args = mock_weaviate_instance.search_documents.call_args
        assert call_args[1]["filters"]["document_type"] == "pdf"
        assert call_args[1]["filters"]["author"] == "Test Author"
        assert call_args[1]["filters"]["language"] == "en"
        assert call_args[1]["filters"]["year"] == 2024

    def test_get_search_history(self, db_session: Session, test_user: User):
        """Test getting search history."""
        knowledge_service = KnowledgeService(db_session)
        
        # Create search queries
        from app.models.knowledge import SearchQuery
        
        query1 = SearchQuery(
            user_id=test_user.id,
            query="test query 1",
            query_type="knowledge",
            result_count=5
        )
        query2 = SearchQuery(
            user_id=test_user.id,
            query="test query 2",
            query_type="conversation",
            result_count=3
        )
        db_session.add_all([query1, query2])
        db_session.commit()
        
        # Get search history
        history = knowledge_service.get_search_history(str(test_user.id))
        
        assert len(history) == 2
        assert history[0].query == "test query 2"  # Most recent first
        assert history[1].query == "test query 1"


class TestBackgroundJobService:
    """Test cases for BackgroundJobService."""

    def test_job_service_initialization(self):
        """Test background job service initialization."""
        service = BackgroundJobService()
        
        assert service.max_workers == 3
        assert service.running is False
        assert len(service.running_jobs) == 0

    def test_schedule_job(self):
        """Test scheduling a job."""
        service = BackgroundJobService()
        
        success = service.schedule_job("test-job-id", priority=5)
        assert success is True
        
        # Check that job is in queue
        assert not service.job_queue.empty()

    def test_get_job_status(self, db_session: Session, test_user: User):
        """Test getting job status."""
        service = BackgroundJobService()
        
        # Create job
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024
        )
        db_session.add(document)
        db_session.commit()
        
        job = DocumentProcessingJob(
            document_id=document.id,
            user_id=test_user.id,
            job_type="process",
            status="running",
            progress=0.5,
            current_step="Processing"
        )
        db_session.add(job)
        db_session.commit()
        
        # Get job status
        status = service.get_job_status(str(job.id))
        
        assert status is not None
        assert status["id"] == str(job.id)
        assert status["status"] == "running"
        assert status["progress"] == 0.5
        assert status["current_step"] == "Processing"

    def test_get_running_jobs(self):
        """Test getting running jobs."""
        service = BackgroundJobService()
        
        # Simulate running jobs
        service.running_jobs["job1"] = Mock()
        service.running_jobs["job2"] = Mock()
        
        running_jobs = service.get_running_jobs()
        assert len(running_jobs) == 2
        assert "job1" in running_jobs
        assert "job2" in running_jobs

    def test_cancel_job(self):
        """Test canceling a job."""
        service = BackgroundJobService()
        
        # Simulate running job
        service.running_jobs["job1"] = Mock()
        
        # Cancel job
        success = service.cancel_job("job1")
        assert success is True
        assert "job1" not in service.running_jobs
        
        # Cancel non-existent job
        success = service.cancel_job("non-existent")
        assert success is False


# Fixtures
@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user