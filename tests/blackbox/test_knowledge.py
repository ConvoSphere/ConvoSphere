"""
Blackbox tests for knowledge base endpoints.

This module tests all knowledge base API endpoints including
document management, search, tags, and processing.
"""

import pytest
from backend.appconftest import TEST_DOCUMENT_DATA


class TestDocumentManagement:
    """Test document management endpoints."""
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_upload_document_success(self, api_client, assertion_helper, authenticated_user, test_data_manager):
        """Test successful document upload."""
        token, user_data = authenticated_user
        
        # Create temporary file
        file_content = "This is a test document for blackbox testing of knowledge base."
        file_path = test_data_manager.create_temp_file(file_content, ".txt")
        
        # Upload document
        with open(file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {
                "title": TEST_DOCUMENT_DATA["title"],
                "description": TEST_DOCUMENT_DATA["description"],
                "tags": "test,blackbox,document"
            }
            
            response = api_client.post("/knowledge/documents", data=data, files=files, user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 201)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "title", "description", "file_name", "file_size", "file_type", 
            "uploaded_at", "status", "tags"
        ])
        
        # Verify document data
        document = response.json()
        assert document["title"] == TEST_DOCUMENT_DATA["title"]
        assert document["description"] == TEST_DOCUMENT_DATA["description"]
        assert document["file_name"] == "test_document.txt"
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_upload_document_invalid_file(self, api_client, assertion_helper, authenticated_user):
        """Test document upload with invalid file."""
        token, user_data = authenticated_user
        
        # Try to upload without file
        data = {
            "title": "Test Document",
            "description": "Test description"
        }
        
        response = api_client.post("/knowledge/documents", data=data, user_type="regular_user")
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_upload_document_unauthorized(self, api_client, assertion_helper, test_data_manager):
        """Test document upload without authentication."""
        # Create temporary file
        file_content = "Test document content"
        file_path = test_data_manager.create_temp_file(file_content, ".txt")
        
        # Upload document without authentication
        with open(file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {
                "title": "Test Document",
                "description": "Test description"
            }
            
            response = api_client.post("/knowledge/documents", data=data, files=files)
        
        assertion_helper.assert_unauthorized(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_documents_list(self, api_client, assertion_helper, authenticated_user):
        """Test getting list of documents."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/documents", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "documents", "total", "page", "size"
        ])
        assertion_helper.assert_list_response(response.json()["documents"])
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_documents_list_with_filters(self, api_client, assertion_helper, authenticated_user):
        """Test getting documents list with filters."""
        token, user_data = authenticated_user
        
        # Test with pagination
        response = api_client.get("/knowledge/documents", params={"page": 1, "size": 10}, user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
        
        # Test with search
        response = api_client.get("/knowledge/documents", params={"search": "test"}, user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
        
        # Test with tags filter
        response = api_client.get("/knowledge/documents", params={"tags": "test"}, user_type="regular_user")
        assertion_helper.assert_success_response(response, 200)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_document_by_id(self, api_client, assertion_helper, test_document):
        """Test getting document by ID."""
        document_id = test_document["id"]
        
        response = api_client.get(f"/knowledge/documents/{document_id}")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "title", "description", "file_name", "file_size", "file_type", 
            "uploaded_at", "status", "tags"
        ])
        assert response.json()["id"] == document_id
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_document_by_id_not_found(self, api_client, assertion_helper, authenticated_user):
        """Test getting non-existent document by ID."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/documents/999999", user_type="regular_user")
        assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_update_document(self, api_client, assertion_helper, test_document):
        """Test updating document."""
        document_id = test_document["id"]
        
        update_data = {
            "title": "Updated Document Title",
            "description": "Updated description",
            "tags": "updated,test,document"
        }
        
        response = api_client.put(f"/knowledge/documents/{document_id}", data=update_data)
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "title", "description", "file_name", "file_size", "file_type", 
            "uploaded_at", "status", "tags"
        ])
        
        # Verify updates
        updated_document = response.json()
        assert updated_document["title"] == update_data["title"]
        assert updated_document["description"] == update_data["description"]
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_delete_document(self, api_client, assertion_helper, authenticated_user, test_data_manager):
        """Test deleting document."""
        token, user_data = authenticated_user
        
        # First upload a document to delete
        file_content = "Document to delete"
        file_path = test_data_manager.create_temp_file(file_content, ".txt")
        
        with open(file_path, "rb") as f:
            files = {"file": ("delete_document.txt", f, "text/plain")}
            data = {
                "title": "Document to Delete",
                "description": "This document will be deleted"
            }
            
            create_response = api_client.post("/knowledge/documents", data=data, files=files, user_type="regular_user")
            document_id = create_response.json()["id"]
        
        # Delete the document
        response = api_client.delete(f"/knowledge/documents/{document_id}", user_type="regular_user")
        assertion_helper.assert_success_response(response, 204)
        
        # Verify document is deleted
        get_response = api_client.get(f"/knowledge/documents/{document_id}", user_type="regular_user")
        assertion_helper.assert_not_found(get_response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_download_document(self, api_client, assertion_helper, test_document):
        """Test downloading document."""
        document_id = test_document["id"]
        
        response = api_client.get(f"/knowledge/documents/{document_id}/download")
        
        assertion_helper.assert_success_response(response, 200)
        assert response.headers.get("content-type") in ["text/plain", "application/octet-stream"]
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_download_document_not_found(self, api_client, assertion_helper, authenticated_user):
        """Test downloading non-existent document."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/documents/999999/download", user_type="regular_user")
        assertion_helper.assert_not_found(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_process_document(self, api_client, assertion_helper, test_document):
        """Test processing document."""
        document_id = test_document["id"]
        
        response = api_client.post(f"/knowledge/documents/{document_id}/process")
        
        # This endpoint might return different status codes depending on implementation
        assert response.status_code in [200, 202, 400], \
            f"Unexpected status code: {response.status_code}"
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_reprocess_document(self, api_client, assertion_helper, test_document):
        """Test reprocessing document."""
        document_id = test_document["id"]
        
        response = api_client.post(f"/knowledge/documents/{document_id}/reprocess")
        
        # This endpoint might return different status codes depending on implementation
        assert response.status_code in [200, 202, 400], \
            f"Unexpected status code: {response.status_code}"
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_upload_advanced_document(self, api_client, assertion_helper, authenticated_user, test_data_manager):
        """Test advanced document upload."""
        token, user_data = authenticated_user
        
        # Create temporary file
        file_content = "Advanced test document content"
        file_path = test_data_manager.create_temp_file(file_content, ".txt")
        
        # Upload with advanced options
        with open(file_path, "rb") as f:
            files = {"file": ("advanced_document.txt", f, "text/plain")}
            data = {
                "title": "Advanced Test Document",
                "description": "Advanced test description",
                "tags": "advanced,test,document",
                "processing_options": "extract_text,generate_summary"
            }
            
            response = api_client.post("/knowledge/documents/upload-advanced", data=data, files=files, user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 201)
        assertion_helper.assert_response_structure(response.json(), [
            "id", "title", "description", "file_name", "file_size", "file_type", 
            "uploaded_at", "status", "tags"
        ])


class TestDocumentSearch:
    """Test document search functionality."""
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_search_documents(self, api_client, assertion_helper, authenticated_user):
        """Test basic document search."""
        token, user_data = authenticated_user
        
        search_data = {
            "query": "test document",
            "limit": 10
        }
        
        response = api_client.post("/knowledge/search", data=search_data, user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "results", "total", "query"
        ])
        assertion_helper.assert_list_response(response.json()["results"])
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_advanced_search_documents(self, api_client, assertion_helper, authenticated_user):
        """Test advanced document search."""
        token, user_data = authenticated_user
        
        search_data = {
            "query": "test",
            "filters": {
                "tags": ["test"],
                "file_type": ["txt"],
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                }
            },
            "sort_by": "relevance",
            "limit": 10
        }
        
        response = api_client.post("/knowledge/search/advanced", data=search_data, user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "results", "total", "query", "filters"
        ])
        assertion_helper.assert_list_response(response.json()["results"])
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_search_history(self, api_client, assertion_helper, authenticated_user):
        """Test getting search history."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/search/history", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_search_unauthorized(self, api_client, assertion_helper):
        """Test search without authentication."""
        search_data = {
            "query": "test document",
            "limit": 10
        }
        
        response = api_client.post("/knowledge/search", data=search_data)
        assertion_helper.assert_unauthorized(response)


class TestTagManagement:
    """Test tag management functionality."""
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_tags(self, api_client, assertion_helper, authenticated_user):
        """Test getting all tags."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/tags", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_search_tags(self, api_client, assertion_helper, authenticated_user):
        """Test searching tags."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/tags/search", params={"query": "test"}, user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_tags_unauthorized(self, api_client, assertion_helper):
        """Test getting tags without authentication."""
        response = api_client.get("/knowledge/tags")
        assertion_helper.assert_unauthorized(response)


class TestProcessingManagement:
    """Test document processing management."""
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_processing_jobs(self, api_client, assertion_helper, authenticated_user):
        """Test getting processing jobs."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/processing/jobs", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "jobs", "total", "page", "size"
        ])
        assertion_helper.assert_list_response(response.json()["jobs"])
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_processing_jobs_with_status_filter(self, api_client, assertion_helper, authenticated_user):
        """Test getting processing jobs with status filter."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/processing/jobs", params={"status": "completed"}, user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "jobs", "total", "page", "size"
        ])
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_processing_engines(self, api_client, assertion_helper, authenticated_user):
        """Test getting processing engines."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/processing/engines", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_supported_formats(self, api_client, assertion_helper, authenticated_user):
        """Test getting supported file formats."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/processing/supported-formats", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_list_response(response)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_processing_jobs_unauthorized(self, api_client, assertion_helper):
        """Test getting processing jobs without authentication."""
        response = api_client.get("/knowledge/processing/jobs")
        assertion_helper.assert_unauthorized(response)


class TestKnowledgeStatistics:
    """Test knowledge base statistics."""
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_knowledge_stats(self, api_client, assertion_helper, authenticated_user):
        """Test getting knowledge base statistics."""
        token, user_data = authenticated_user
        
        response = api_client.get("/knowledge/stats", user_type="regular_user")
        
        assertion_helper.assert_success_response(response, 200)
        assertion_helper.assert_response_structure(response.json(), [
            "total_documents", "total_size", "documents_by_type", "recent_uploads"
        ])
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_get_knowledge_stats_unauthorized(self, api_client, assertion_helper):
        """Test getting knowledge stats without authentication."""
        response = api_client.get("/knowledge/stats")
        assertion_helper.assert_unauthorized(response)


class TestKnowledgeValidation:
    """Test knowledge base data validation."""
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_upload_document_missing_required_fields(self, api_client, assertion_helper, authenticated_user, test_data_manager):
        """Test document upload with missing required fields."""
        token, user_data = authenticated_user
        
        # Create temporary file
        file_content = "Test content"
        file_path = test_data_manager.create_temp_file(file_content, ".txt")
        
        # Upload without title
        with open(file_path, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            data = {
                "description": "Test description"
                # Missing title
            }
            
            response = api_client.post("/knowledge/documents", data=data, files=files, user_type="regular_user")
            assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_update_document_invalid_data(self, api_client, assertion_helper, test_document):
        """Test updating document with invalid data."""
        document_id = test_document["id"]
        
        invalid_data = {
            "title": ""  # Empty title
        }
        
        response = api_client.put(f"/knowledge/documents/{document_id}", data=invalid_data)
        assertion_helper.assert_error_response(response, 422)
    
    @pytest.mark.blackbox
    @pytest.mark.knowledge
    def test_search_invalid_query(self, api_client, assertion_helper, authenticated_user):
        """Test search with invalid query."""
        token, user_data = authenticated_user
        
        invalid_data = {
            "query": "",  # Empty query
            "limit": -1  # Invalid limit
        }
        
        response = api_client.post("/knowledge/search", data=invalid_data, user_type="regular_user")
        assertion_helper.assert_error_response(response, 422) 