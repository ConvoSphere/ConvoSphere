"""
Integration tests for knowledge base API endpoints.

This module contains integration tests for the enhanced knowledge base API
including document management, tag management, search, and processing jobs.
"""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
from app.core.security import create_access_token
from app.main import app
from app.models.knowledge import (
    Document,
    DocumentProcessingJob,
    DocumentStatus,
    DocumentType,
    Tag,
)
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

client = TestClient(app)


class TestKnowledgeAPI:
    """Test cases for knowledge base API endpoints."""

    def test_upload_document_with_tags(self, db_session: Session, test_user: User):
        """Test uploading a document with tags and metadata."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"Test document content")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                data = {
                    "title": "Test Document",
                    "description": "A test document with tags",
                    "tags": "important,test,2024",
                    "processing_options": '{"chunk_size": 500}',
                }

                response = client.post(
                    "/api/v1/knowledge/documents",
                    headers=headers,
                    files=files,
                    data=data,
                )

            assert response.status_code == 200
            result = response.json()

            assert result["title"] == "Test Document"
            assert result["description"] == "A test document with tags"
            assert result["file_name"] == "test.txt"
            assert result["file_type"] == "txt"
            assert result["status"] == "uploaded"
            assert result["document_type"] == "text"

        finally:
            os.unlink(temp_file_path)

    def test_get_documents_with_filters(self, db_session: Session, test_user: User):
        """Test getting documents with advanced filtering."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test documents
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
            language="en",
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
            language="de",
        )

        db_session.add_all([doc1, doc2])
        db_session.commit()

        # Test filtering by document type
        response = client.get(
            "/api/v1/knowledge/documents?document_type=pdf", headers=headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 1
        assert result["documents"][0]["document_type"] == "pdf"

        # Test filtering by author
        response = client.get(
            "/api/v1/knowledge/documents?author=Author%201", headers=headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 1
        assert result["documents"][0]["author"] == "Author 1"

        # Test filtering by year
        response = client.get("/api/v1/knowledge/documents?year=2024", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 1
        assert result["documents"][0]["year"] == 2024

    def test_update_document_metadata(self, db_session: Session, test_user: User):
        """Test updating document metadata."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test document
        document = Document(
            user_id=test_user.id,
            title="Original Title",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024,
        )
        db_session.add(document)
        db_session.commit()

        # Update document metadata
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "author": "New Author",
            "source": "New Source",
            "year": 2024,
            "language": "en",
            "keywords": ["updated", "test"],
            "tags": ["important", "updated"],
        }

        response = client.put(
            f"/api/v1/knowledge/documents/{document.id}",
            headers=headers,
            json=update_data,
        )

        assert response.status_code == 200
        result = response.json()

        assert result["title"] == "Updated Title"
        assert result["description"] == "Updated description"
        assert result["author"] == "New Author"
        assert result["source"] == "New Source"
        assert result["year"] == 2024
        assert result["language"] == "en"
        assert result["keywords"] == ["updated", "test"]
        assert result["tag_names"] == ["important", "updated"]

    def test_get_tags(self, db_session: Session, test_user: User):
        """Test getting tags for user's documents."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create tags
        tag1 = Tag(name="important", usage_count=3)
        tag2 = Tag(name="project", usage_count=2)
        tag3 = Tag(name="test", usage_count=1)
        db_session.add_all([tag1, tag2, tag3])

        # Create document with tags
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024,
        )
        document.tags.append(tag1)
        document.tags.append(tag2)
        db_session.add(document)
        db_session.commit()

        # Get tags
        response = client.get("/api/v1/knowledge/tags", headers=headers)

        assert response.status_code == 200
        result = response.json()

        assert result["total"] == 2
        assert len(result["tags"]) == 2
        # Tags should be ordered by usage count
        assert result["tags"][0]["name"] == "important"
        assert result["tags"][1]["name"] == "project"

    def test_search_tags(self, db_session: Session, test_user: User):
        """Test searching tags by name."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create tags
        tag1 = Tag(name="project-a", usage_count=2)
        tag2 = Tag(name="project-b", usage_count=1)
        tag3 = Tag(name="other", usage_count=1)
        db_session.add_all([tag1, tag2, tag3])

        # Create document with project tags
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024,
        )
        document.tags.append(tag1)
        document.tags.append(tag2)
        db_session.add(document)
        db_session.commit()

        # Search for project tags
        response = client.get(
            "/api/v1/knowledge/tags/search?query=project", headers=headers,
        )

        assert response.status_code == 200
        result = response.json()

        assert result["total"] == 2
        assert len(result["tags"]) == 2
        assert all("project" in tag["name"] for tag in result["tags"])

    @patch("app.services.knowledge_service.embedding_service")
    @patch("app.services.knowledge_service.WeaviateService")
    def test_advanced_search(
        self, mock_weaviate, mock_embedding, db_session: Session, test_user: User,
    ):
        """Test advanced search with filters."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Mock services
        mock_embedding.generate_single_embedding = AsyncMock(
            return_value=[0.1, 0.2, 0.3],
        )
        mock_weaviate_instance = Mock()
        mock_weaviate_instance.search_documents.return_value = [
            {
                "id": "1",
                "content": "Test search result",
                "score": 0.8,
                "document_id": "doc-1",
                "document_title": "Test Document",
                "author": "Test Author",
            },
        ]
        mock_weaviate.return_value = mock_weaviate_instance

        # Test advanced search
        search_data = {
            "query": "test query",
            "filters": {
                "document_type": "pdf",
                "author": "Test Author",
                "year": 2024,
                "language": "en",
            },
            "limit": 10,
            "offset": 0,
            "sort_by": "relevance",
            "sort_order": "desc",
        }

        response = client.post(
            "/api/v1/knowledge/search/advanced", headers=headers, json=search_data,
        )

        assert response.status_code == 200
        result = response.json()

        assert result["query"] == "test query"
        assert len(result["results"]) == 1
        assert result["results"][0]["content"] == "Test search result"
        assert result["filters_applied"]["document_type"] == "pdf"

    def test_create_processing_job(self, db_session: Session, test_user: User):
        """Test creating a processing job."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test document
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024,
        )
        db_session.add(document)
        db_session.commit()

        # Create processing job
        job_data = {
            "document_id": str(document.id),
            "job_type": "process",
            "priority": 5,
            "processing_options": '{"chunk_size": 500}',
        }

        response = client.post(
            "/api/v1/knowledge/processing/jobs", headers=headers, data=job_data,
        )

        assert response.status_code == 200
        result = response.json()

        assert result["document_id"] == str(document.id)
        assert result["user_id"] == str(test_user.id)
        assert result["job_type"] == "process"
        assert result["priority"] == 5
        assert result["status"] == "pending"

    def test_get_processing_jobs(self, db_session: Session, test_user: User):
        """Test getting processing jobs."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test document
        document = Document(
            user_id=test_user.id,
            title="Test Document",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            file_size=1024,
        )
        db_session.add(document)
        db_session.commit()

        # Create processing jobs
        job1 = DocumentProcessingJob(
            document_id=document.id,
            user_id=test_user.id,
            job_type="process",
            status="pending",
        )
        job2 = DocumentProcessingJob(
            document_id=document.id,
            user_id=test_user.id,
            job_type="reprocess",
            status="completed",
        )
        db_session.add_all([job1, job2])
        db_session.commit()

        # Get all jobs
        response = client.get("/api/v1/knowledge/processing/jobs", headers=headers)

        assert response.status_code == 200
        result = response.json()

        assert result["total"] == 2
        assert len(result["jobs"]) == 2

        # Get jobs by status
        response = client.get(
            "/api/v1/knowledge/processing/jobs?status=pending", headers=headers,
        )

        assert response.status_code == 200
        result = response.json()

        assert result["total"] == 1
        assert result["jobs"][0]["status"] == "pending"

    def test_bulk_import(self, db_session: Session, test_user: User):
        """Test bulk import functionality."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Test bulk import request
        bulk_import_data = {
            "files": [
                {
                    "name": "doc1.pdf",
                    "title": "Document 1",
                    "description": "First document",
                    "tags": ["important"],
                },
                {
                    "name": "doc2.txt",
                    "title": "Document 2",
                    "description": "Second document",
                    "tags": ["test"],
                },
            ],
            "processing_options": {
                "engine": "traditional",
                "options": {"chunk_size": 500},
            },
            "tags": ["bulk-import", "2024"],
        }

        response = client.post(
            "/api/v1/knowledge/bulk-import", headers=headers, json=bulk_import_data,
        )

        assert response.status_code == 200
        result = response.json()

        assert result["total_files"] == 2
        assert result["message"] == "Bulk import job created successfully"
        assert "job_id" in result

    def test_get_knowledge_base_stats(self, db_session: Session, test_user: User):
        """Test getting knowledge base statistics."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test documents with different statuses
        doc1 = Document(
            user_id=test_user.id,
            title="Processed Document",
            file_name="doc1.pdf",
            file_path="/path/to/doc1.pdf",
            file_type="pdf",
            file_size=1024,
            status=DocumentStatus.PROCESSED,
            document_type=DocumentType.PDF,
        )

        doc2 = Document(
            user_id=test_user.id,
            title="Processing Document",
            file_name="doc2.docx",
            file_path="/path/to/doc2.docx",
            file_type="docx",
            file_size=2048,
            status=DocumentStatus.PROCESSING,
            document_type=DocumentType.DOCUMENT,
        )

        doc3 = Document(
            user_id=test_user.id,
            title="Error Document",
            file_name="doc3.txt",
            file_path="/path/to/doc3.txt",
            file_type="txt",
            file_size=512,
            status=DocumentStatus.ERROR,
            document_type=DocumentType.TEXT,
        )

        db_session.add_all([doc1, doc2, doc3])
        db_session.commit()

        # Get statistics
        response = client.get("/api/v1/knowledge/stats", headers=headers)

        assert response.status_code == 200
        result = response.json()

        assert result["total_documents"] == 3
        assert result["documents_by_status"]["processed"] == 1
        assert result["documents_by_status"]["processing"] == 1
        assert result["documents_by_status"]["error"] == 1
        assert result["documents_by_type"]["pdf"] == 1
        assert result["documents_by_type"]["document"] == 1
        assert result["documents_by_type"]["text"] == 1
        assert result["storage_used"] == 3584  # 1024 + 2048 + 512

    def test_search_history(self, db_session: Session, test_user: User):
        """Test getting search history."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create search queries
        from app.models.knowledge import SearchQuery

        query1 = SearchQuery(
            user_id=test_user.id,
            query="test query 1",
            query_type="knowledge",
            result_count=5,
        )
        query2 = SearchQuery(
            user_id=test_user.id,
            query="test query 2",
            query_type="conversation",
            result_count=3,
        )
        db_session.add_all([query1, query2])
        db_session.commit()

        # Get search history
        response = client.get("/api/v1/knowledge/search/history", headers=headers)

        assert response.status_code == 200
        result = response.json()

        assert result["total"] == 2
        assert len(result["searches"]) == 2
        assert result["searches"][0]["query"] == "test query 2"  # Most recent first

    def test_unauthorized_access(self, db_session: Session):
        """Test unauthorized access to protected endpoints."""
        # Test without authentication
        response = client.get("/api/v1/knowledge/documents")
        assert response.status_code == 401

        response = client.get("/api/v1/knowledge/tags")
        assert response.status_code == 401

        response = client.post("/api/v1/knowledge/search/advanced", json={})
        assert response.status_code == 401

    def test_invalid_document_id(self, db_session: Session, test_user: User):
        """Test accessing non-existent document."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Try to get non-existent document
        response = client.get("/api/v1/knowledge/documents/invalid-id", headers=headers)
        assert response.status_code == 404

        # Try to update non-existent document
        response = client.put(
            "/api/v1/knowledge/documents/invalid-id",
            headers=headers,
            json={"title": "Updated"},
        )
        assert response.status_code == 404

    def test_invalid_file_type(self, db_session: Session, test_user: User):
        """Test uploading invalid file type."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test file with invalid extension
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test.exe", f, "application/octet-stream")}
                data = {"title": "Test Document"}

                response = client.post(
                    "/api/v1/knowledge/documents",
                    headers=headers,
                    files=files,
                    data=data,
                )

            assert response.status_code == 400
            assert "not supported" in response.json()["detail"]

        finally:
            os.unlink(temp_file_path)

    def test_invalid_processing_options(self, db_session: Session, test_user: User):
        """Test uploading with invalid processing options."""
        # Create access token
        access_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create test file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                data = {"title": "Test Document", "processing_options": "invalid json"}

                response = client.post(
                    "/api/v1/knowledge/documents",
                    headers=headers,
                    files=files,
                    data=data,
                )

            assert response.status_code == 400
            assert "Invalid processing options JSON" in response.json()["detail"]

        finally:
            os.unlink(temp_file_path)


# Fixtures
@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com", username="testuser", hashed_password="hashed_password",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
