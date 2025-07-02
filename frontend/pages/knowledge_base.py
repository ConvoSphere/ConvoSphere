"""
Knowledge Base Management Page.

This page provides a comprehensive interface for managing the knowledge base
used for RAG (Retrieval-Augmented Generation) in the AI assistant platform.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from services.api import api_client
from services.auth_service import auth_service


class KnowledgeBasePage:
    """Knowledge base management page."""
    
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.is_loading = False
        self.is_uploading = False
        self.search_query = ""
        self.search_results: List[Dict[str, Any]] = []
        self.is_searching = False
        self.selected_document = None
        
        # UI elements
        self.documents_list = None
        self.document_viewer = None
        self.upload_progress = None
        
        self.create_page()
    
    def create_page(self):
        """Create the knowledge base page layout."""
        with ui.column().classes("w-full h-full"):
            # Header
            with ui.row().classes("w-full p-4 bg-white border-b border-gray-200"):
                with ui.row().classes("flex-1 items-center gap-4"):
                    ui.label("Knowledge Base").classes("text-2xl font-bold")
                    
                    # Upload button
                    ui.button(
                        "Upload Document",
                        on_click=self.show_upload_dialog,
                        icon="upload"
                    ).classes("bg-blue-500 text-white")
                    
                    # Refresh button
                    ui.button(
                        "Refresh",
                        on_click=self.load_documents,
                        icon="refresh"
                    ).classes("bg-gray-500 text-white")
                
                with ui.row().classes("items-center gap-2"):
                    ui.button("Settings", on_click=self.show_settings).classes("bg-gray-500 text-white")
            
            # Main content area
            with ui.row().classes("w-full h-full flex-1 gap-0"):
                # Documents sidebar
                with ui.column().classes("w-80 bg-gray-50 border-r border-gray-200 p-4"):
                    ui.label("Documents").classes("text-lg font-semibold mb-4")
                    
                    # Search documents
                    search_input = ui.input(
                        "Search documents...",
                        on_change=self.on_search_change
                    ).classes("w-full mb-4")
                    
                    # Search button
                    ui.button(
                        "Search",
                        on_click=self.search_documents,
                        loading=self.is_searching
                    ).classes("w-full mb-4 bg-blue-500 text-white")
                    
                    # Search results
                    if self.search_results:
                        with ui.expansion("Search Results", icon="search").classes("mb-4"):
                            with ui.column().classes("space-y-2"):
                                for result in self.search_results:
                                    with ui.card().classes("w-full"):
                                        ui.label(f"Score: {result.get('score', 0):.3f}").classes("text-sm text-gray-600")
                                        ui.label(result.get('content', '')).classes("text-sm")
                    
                    # Documents list
                    self.documents_list = ui.column().classes("w-full flex-1 overflow-y-auto")
                    
                    # Load documents button
                    ui.button("Load More", on_click=self.load_documents).classes("w-full mt-4 bg-gray-500 text-white")
                
                # Document viewer area
                with ui.column().classes("flex-1 flex flex-col"):
                    # Document header
                    with ui.row().classes("p-4 border-b border-gray-200 bg-white"):
                        if self.selected_document:
                            with ui.row().classes("flex-1 items-center gap-4"):
                                ui.label(f"Document: {self.selected_document.get('title', 'Untitled')}").classes("text-lg font-semibold")
                                
                                # Document actions
                                ui.button(
                                    "Delete",
                                    on_click=self.delete_document,
                                    icon="delete"
                                ).classes("bg-red-500 text-white")
                                
                                ui.button(
                                    "Download",
                                    on_click=self.download_document,
                                    icon="download"
                                ).classes("bg-green-500 text-white")
                        else:
                            ui.label("Select a document to view").classes("text-lg text-gray-500")
                    
                    # Document content
                    with ui.column().classes("flex-1 p-4 overflow-y-auto") as content_area:
                        self.document_viewer = content_area
            
            # Create dialogs
            self.create_upload_dialog()
            self.create_settings_dialog()
            
            # Load initial data
            asyncio.create_task(self.load_documents())
    
    def create_upload_dialog(self):
        """Create the document upload dialog."""
        with ui.dialog() as self.upload_dialog, ui.card().classes("w-96"):
            ui.label("Upload Document").classes("text-lg font-semibold mb-4")
            
            # File input
            ui.label("Select Document").classes("font-medium mb-2")
            file_input = ui.upload(
                label="Choose file",
                multiple=False,
                accept=".pdf,.txt,.doc,.docx,.md"
            ).classes("w-full mb-4")
            
            # Document metadata
            ui.label("Document Title").classes("font-medium mb-2")
            title_input = ui.input("Untitled Document").classes("w-full mb-4")
            
            ui.label("Description (Optional)").classes("font-medium mb-2")
            description_input = ui.textarea("").classes("w-full mb-4")
            
            ui.label("Tags (Optional)").classes("font-medium mb-2")
            tags_input = ui.input("tag1, tag2, tag3").classes("w-full mb-4")
            
            # Upload progress
            self.upload_progress = ui.linear_progress().classes("w-full mb-4")
            self.upload_progress.visible = False
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.upload_dialog.close).classes("bg-gray-500")
                ui.button("Upload", on_click=self.upload_document).classes("bg-blue-500")
    
    def create_settings_dialog(self):
        """Create the knowledge base settings dialog."""
        with ui.dialog() as self.settings_dialog, ui.card().classes("w-96"):
            ui.label("Knowledge Base Settings").classes("text-lg font-semibold mb-4")
            
            # Chunk size setting
            ui.label("Chunk Size").classes("font-medium mb-2")
            chunk_size_input = ui.number(
                min=100, max=2000, value=500, step=50
            ).classes("w-full mb-4")
            
            # Overlap setting
            ui.label("Chunk Overlap").classes("font-medium mb-2")
            overlap_input = ui.number(
                min=0, max=500, value=50, step=10
            ).classes("w-full mb-4")
            
            # Embedding model
            ui.label("Embedding Model").classes("font-medium mb-2")
            model_select = ui.select(
                options=["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"],
                value="text-embedding-ada-002"
            ).classes("w-full mb-4")
            
            # Auto-refresh setting
            auto_refresh = ui.checkbox("Auto-refresh documents").classes("w-full mb-4")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.settings_dialog.close).classes("bg-gray-500")
                ui.button("Save", on_click=self.save_settings).classes("bg-blue-500")
    
    async def load_documents(self):
        """Load documents from the knowledge base."""
        try:
            self.is_loading = True
            
            # Use the internal _make_request method for custom endpoints
            response = await api_client._make_request(
                "GET",
                "/api/v1/knowledge/documents"
            )
            
            if response.success and response.data:
                self.documents = response.data
                self.update_documents_list()
            else:
                ui.notify(f"Error loading documents: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error loading documents: {str(e)}", type="error")
        finally:
            self.is_loading = False
    
    def update_documents_list(self):
        """Update the documents list display."""
        if not self.documents_list:
            return
        
        # Clear existing documents
        self.documents_list.clear()
        
        # Add documents
        for document in self.documents:
            with self.documents_list:
                with ui.card().classes("w-full p-3 cursor-pointer hover:bg-blue-50").on("click", lambda d=document: self.select_document(d)):
                    with ui.column().classes("w-full"):
                        ui.label(document.get('title', 'Untitled')).classes("font-semibold text-sm")
                        ui.label(document.get('description', 'No description')).classes("text-xs text-gray-600")
                        
                        with ui.row().classes("w-full justify-between items-center mt-2"):
                            ui.label(f"{document.get('chunk_count', 0)} chunks").classes("text-xs text-gray-500")
                            ui.label(document.get('uploaded_at', 'Unknown')).classes("text-xs text-gray-500")
                        
                        # Document status
                        status = document.get('status', 'unknown')
                        status_color = {
                            'processed': 'text-green-600',
                            'processing': 'text-yellow-600',
                            'error': 'text-red-600',
                            'unknown': 'text-gray-600'
                        }.get(status, 'text-gray-600')
                        
                        ui.label(f"Status: {status}").classes(f"text-xs {status_color}")
    
    def select_document(self, document: Dict[str, Any]):
        """Select a document to view."""
        self.selected_document = document
        self.update_document_viewer()
    
    def update_document_viewer(self):
        """Update the document viewer display."""
        if not self.document_viewer or not self.selected_document:
            return
        
        # Clear existing content
        self.document_viewer.clear()
        
        # Add document content
        with self.document_viewer:
            # Document metadata
            with ui.card().classes("w-full p-4 mb-4"):
                ui.label("Document Information").classes("text-lg font-semibold mb-2")
                
                with ui.row().classes("w-full gap-4"):
                    with ui.column().classes("flex-1"):
                        ui.label(f"Title: {self.selected_document.get('title', 'Untitled')}").classes("text-sm")
                        ui.label(f"Description: {self.selected_document.get('description', 'No description')}").classes("text-sm")
                        ui.label(f"File Type: {self.selected_document.get('file_type', 'Unknown')}").classes("text-sm")
                    
                    with ui.column().classes("flex-1"):
                        ui.label(f"Uploaded: {self.selected_document.get('uploaded_at', 'Unknown')}").classes("text-sm")
                        ui.label(f"Chunks: {self.selected_document.get('chunk_count', 0)}").classes("text-sm")
                        ui.label(f"Status: {self.selected_document.get('status', 'Unknown')}").classes("text-sm")
                
                # Tags
                tags = self.selected_document.get('tags', [])
                if tags:
                    with ui.row().classes("w-full mt-2"):
                        ui.label("Tags: ").classes("text-sm")
                        for tag in tags:
                            ui.label(tag).classes("bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1")
            
            # Document chunks
            chunks = self.selected_document.get('chunks', [])
            if chunks:
                ui.label("Document Chunks").classes("text-lg font-semibold mb-2")
                
                for i, chunk in enumerate(chunks):
                    with ui.card().classes("w-full p-3 mb-2"):
                        with ui.row().classes("w-full justify-between items-center mb-2"):
                            ui.label(f"Chunk {i+1}").classes("font-semibold text-sm")
                            ui.label(f"Tokens: {chunk.get('token_count', 0)}").classes("text-xs text-gray-500")
                        
                        ui.label(chunk.get('content', '')).classes("text-sm whitespace-pre-wrap")
            else:
                ui.label("No chunks available").classes("text-gray-500 text-center p-4")
    
    def show_upload_dialog(self):
        """Show the upload dialog."""
        self.upload_dialog.open()
    
    async def upload_document(self):
        """Upload a document to the knowledge base."""
        try:
            self.is_uploading = True
            self.upload_progress.visible = True
            self.upload_progress.value = 0
            
            # Get form data
            file_input = self.upload_dialog.find_child(ui.upload)
            title_input = self.upload_dialog.find_child(ui.input)
            description_input = self.upload_dialog.find_child(ui.textarea)
            tags_input = self.upload_dialog.find_child(ui.input, lambda x: x != title_input)
            
            if not file_input or not file_input.files:
                ui.notify("Please select a file to upload", type="warning")
                return
            
            file = file_input.files[0]
            title = title_input.value if title_input else "Untitled Document"
            description = description_input.value if description_input else ""
            tags = [tag.strip() for tag in tags_input.value.split(',')] if tags_input and tags_input.value else []
            
            # Simulate upload progress
            for i in range(10):
                await asyncio.sleep(0.1)
                self.upload_progress.value = (i + 1) / 10
            
            # Upload document
            # In a real implementation, this would upload the file to the backend
            response = await api_client._make_request(
                "POST",
                "/api/v1/knowledge/documents",
                data={
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "file_name": file.name,
                    "file_size": len(file.content) if hasattr(file, 'content') else 0
                }
            )
            
            if response.success:
                ui.notify("Document uploaded successfully", type="positive")
                self.upload_dialog.close()
                await self.load_documents()
            else:
                ui.notify(f"Upload failed: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error uploading document: {str(e)}", type="error")
        finally:
            self.is_uploading = False
            self.upload_progress.visible = False
    
    async def delete_document(self):
        """Delete the selected document."""
        if not self.selected_document:
            ui.notify("Please select a document to delete", type="warning")
            return
        
        try:
            document_id = self.selected_document.get('id')
            response = await api_client._make_request(
                "DELETE",
                f"/api/v1/knowledge/documents/{document_id}"
            )
            
            if response.success:
                ui.notify("Document deleted successfully", type="positive")
                self.selected_document = None
                await self.load_documents()
                self.update_document_viewer()
            else:
                ui.notify(f"Delete failed: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error deleting document: {str(e)}", type="error")
    
    async def download_document(self):
        """Download the selected document."""
        if not self.selected_document:
            ui.notify("Please select a document to download", type="warning")
            return
        
        try:
            document_id = self.selected_document.get('id')
            response = await api_client._make_request(
                "GET",
                f"/api/v1/knowledge/documents/{document_id}/download"
            )
            
            if response.success:
                # In a real implementation, this would trigger a file download
                ui.notify("Download started", type="positive")
            else:
                ui.notify(f"Download failed: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error downloading document: {str(e)}", type="error")
    
    async def search_documents(self):
        """Search documents in the knowledge base."""
        if not self.search_query.strip():
            self.search_results = []
            return
            
        self.is_searching = True
        try:
            response = await api_client._make_request(
                "POST",
                "/api/v1/search/knowledge",
                data={"query": self.search_query}
            )
            
            if response.success and response.data:
                self.search_results = response.data
            else:
                ui.notify(f'Search failed: {response.error}', type='error')
                
        except Exception as e:
            ui.notify(f'Search error: {str(e)}', type='error')
        finally:
            self.is_searching = False
    
    def show_settings(self):
        """Show settings dialog."""
        self.settings_dialog.open()
    
    def save_settings(self):
        """Save knowledge base settings."""
        # Save settings logic here
        self.settings_dialog.close()
        ui.notify("Settings saved", type="positive")
    
    async def on_search_change(self, e: ValueChangeEventArguments):
        """Handle search input change."""
        self.search_query = e.value


# Create page instance
knowledge_base_page = KnowledgeBasePage()

async def setup():
    """Setup the knowledge base page."""
    pass

def create_page():
    """Create the knowledge base page."""
    return setup() 