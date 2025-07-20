"""
Advanced search component for knowledge base.

This module provides an enhanced search interface with filters,
advanced search options, and real-time search suggestions.
"""

from nicegui import ui
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import asyncio

from services.knowledge_service import knowledge_service, Document, SearchResult
from utils.helpers import format_timestamp, format_file_size
from utils.i18n_manager import t


class AdvancedSearchComponent:
    """Advanced search component for knowledge base."""
    
    def __init__(
        self,
        on_search: Optional[Callable[[List[SearchResult]], None]] = None,
        on_filter_change: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Initialize the search component.
        
        Args:
            on_search: Callback for search results
            on_filter_change: Callback for filter changes
        """
        self.on_search = on_search
        self.on_filter_change = on_filter_change
        
        # Search state
        self.current_query = ""
        self.current_filters = {}
        self.search_results: List[SearchResult] = []
        self.is_searching = False
        self.search_history: List[str] = []
        
        # UI components
        self.container = None
        self.search_input = None
        self.filters_container = None
        self.results_container = None
        self.suggestions_container = None
        
        self.create_search_component()
    
    def create_search_component(self):
        """Create the search component UI."""
        self.container = ui.element("div").classes("w-full")
        
        with self.container:
            # Search header
            self.create_search_header()
            
            # Search input and filters
            self.create_search_input()
            
            # Advanced filters
            self.create_advanced_filters()
            
            # Search suggestions
            self.create_search_suggestions()
            
            # Search results
            self.create_search_results()
    
    def create_search_header(self):
        """Create search header section."""
        with ui.element("div").classes("mb-6"):
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label(t("knowledge.search_title")).classes("text-2xl font-bold")
                    ui.label(t("knowledge.search_subtitle")).classes("text-gray-600")
                
                with ui.row().classes("space-x-2"):
                    # Search history button
                    ui.button(
                        icon="history",
                        on_click=self.show_search_history
                    ).classes("w-10 h-10 bg-gray-100 text-gray-600")
                    
                    # Save search button
                    ui.button(
                        icon="bookmark",
                        on_click=self.save_current_search
                    ).classes("w-10 h-10 bg-gray-100 text-gray-600")
    
    def create_search_input(self):
        """Create search input section."""
        with ui.element("div").classes("mb-4"):
            with ui.row().classes("items-center space-x-4"):
                # Main search input
                self.search_input = ui.input(
                    placeholder=t("knowledge.search_placeholder"),
                    on_change=self.handle_search_input_change,
                    on_keydown=self.handle_search_keydown
                ).classes("flex-1").props("autofocus")
                
                # Search button
                ui.button(
                    t("knowledge.search_button"),
                    icon="search",
                    on_click=self.perform_search
                ).classes("bg-blue-600 text-white px-6")
                
                # Advanced search toggle
                ui.button(
                    icon="tune",
                    on_click=self.toggle_advanced_filters
                ).classes("w-10 h-10 bg-gray-100 text-gray-600")
    
    def create_advanced_filters(self):
        """Create advanced filters section."""
        self.filters_container = ui.element("div").classes("mb-4 p-4 bg-gray-50 rounded-lg hidden")
        
        with self.filters_container:
            ui.label(t("knowledge.advanced_filters")).classes("text-lg font-medium mb-3")
            
            with ui.row().classes("grid grid-cols-1 md:grid-cols-3 gap-4"):
                # Document type filter
                self.type_filter = ui.select(
                    options=[
                        {"label": t("knowledge.all_types"), "value": "all"},
                        {"label": "PDF", "value": "pdf"},
                        {"label": "DOCX", "value": "docx"},
                        {"label": "TXT", "value": "txt"},
                        {"label": "Markdown", "value": "md"},
                        {"label": "HTML", "value": "html"}
                    ],
                    value="all",
                    label=t("knowledge.document_type"),
                    on_change=self.handle_filter_change
                ).classes("w-full")
                
                # Date range filter
                self.date_filter = ui.select(
                    options=[
                        {"label": t("knowledge.all_dates"), "value": "all"},
                        {"label": t("knowledge.last_day"), "value": "1d"},
                        {"label": t("knowledge.last_week"), "value": "7d"},
                        {"label": t("knowledge.last_month"), "value": "30d"},
                        {"label": t("knowledge.last_year"), "value": "365d"}
                    ],
                    value="all",
                    label=t("knowledge.date_range"),
                    on_change=self.handle_filter_change
                ).classes("w-full")
                
                # Language filter
                self.language_filter = ui.select(
                    options=[
                        {"label": t("knowledge.all_languages"), "value": "all"},
                        {"label": "English", "value": "en"},
                        {"label": "Deutsch", "value": "de"}
                    ],
                    value="all",
                    label=t("knowledge.language"),
                    on_change=self.handle_filter_change
                ).classes("w-full")
            
            with ui.row().classes("grid grid-cols-1 md:grid-cols-2 gap-4 mt-4"):
                # Topics filter
                self.topics_filter = ui.select(
                    options=[
                        {"label": t("knowledge.all_topics"), "value": "all"},
                        {"label": "Programming", "value": "programming"},
                        {"label": "Database", "value": "database"},
                        {"label": "Web Development", "value": "web"},
                        {"label": "AI/ML", "value": "ai"},
                        {"label": "DevOps", "value": "devops"},
                        {"label": "Security", "value": "security"}
                    ],
                    value="all",
                    label=t("knowledge.topics"),
                    on_change=self.handle_filter_change
                ).classes("w-full")
                
                # Sort order
                self.sort_filter = ui.select(
                    options=[
                        {"label": t("knowledge.relevance"), "value": "relevance"},
                        {"label": t("knowledge.date_newest"), "value": "date_desc"},
                        {"label": t("knowledge.date_oldest"), "value": "date_asc"},
                        {"label": t("knowledge.title"), "value": "title"},
                        {"label": t("knowledge.size"), "value": "size"}
                    ],
                    value="relevance",
                    label=t("knowledge.sort_by"),
                    on_change=self.handle_filter_change
                ).classes("w-full")
            
            # Additional filters
            with ui.row().classes("mt-4"):
                with ui.column().classes("space-y-2"):
                    ui.label(t("knowledge.additional_filters")).classes("font-medium")
                    
                    with ui.row().classes("space-x-4"):
                        # Has entities filter
                        self.has_entities_filter = ui.switch(
                            t("knowledge.has_entities")
                        ).classes("w-full")
                        
                        # Has keywords filter
                        self.has_keywords_filter = ui.switch(
                            t("knowledge.has_keywords")
                        ).classes("w-full")
                    
                    with ui.row().classes("space-x-4"):
                        # Min importance score
                        self.min_importance_filter = ui.number(
                            label=t("knowledge.min_importance"),
                            min=0.0,
                            max=2.0,
                            step=0.1,
                            value=0.0
                        ).classes("w-32")
                        
                        # Max reading time
                        self.max_reading_time_filter = ui.number(
                            label=t("knowledge.max_reading_time"),
                            min=1,
                            max=120,
                            step=1,
                            value=60
                        ).classes("w-32")
    
    def create_search_suggestions(self):
        """Create search suggestions section."""
        self.suggestions_container = ui.element("div").classes("mb-4")
        
        with self.suggestions_container:
            ui.label(t("knowledge.search_suggestions")).classes("text-sm font-medium mb-2")
            
            # Popular searches
            with ui.row().classes("flex-wrap gap-2"):
                popular_searches = [
                    "API documentation",
                    "Database schema",
                    "Authentication",
                    "Error handling",
                    "Deployment guide"
                ]
                
                for search in popular_searches:
                    ui.button(
                        search,
                        on_click=lambda s=search: self.set_search_query(s)
                    ).classes("text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded")
    
    def create_search_results(self):
        """Create search results section."""
        self.results_container = ui.element("div").classes("space-y-4")
        
        with self.results_container:
            # Results header
            self.results_header = ui.element("div").classes("flex items-center justify-between p-4 bg-gray-50 rounded")
            
            with self.results_header:
                ui.label(t("knowledge.no_results")).classes("text-gray-500")
    
    def handle_search_input_change(self, event):
        """Handle search input change."""
        self.current_query = event.value
        self.update_search_suggestions()
    
    def handle_search_keydown(self, event):
        """Handle search input keydown."""
        if event.key == "Enter":
            self.perform_search()
    
    def handle_filter_change(self, event):
        """Handle filter change."""
        self.current_filters = self.get_current_filters()
        
        if self.on_filter_change:
            self.on_filter_change(self.current_filters)
    
    def get_current_filters(self) -> Dict[str, Any]:
        """Get current filter values."""
        return {
            "document_type": self.type_filter.value,
            "date_range": self.date_filter.value,
            "language": self.language_filter.value,
            "topics": self.topics_filter.value,
            "sort_by": self.sort_filter.value,
            "has_entities": self.has_entities_filter.value,
            "has_keywords": self.has_keywords_filter.value,
            "min_importance": self.min_importance_filter.value,
            "max_reading_time": self.max_reading_time_filter.value
        }
    
    async def perform_search(self):
        """Perform search with current query and filters."""
        if not self.current_query.strip():
            return
        
        self.is_searching = True
        self.update_search_ui()
        
        try:
            # Add to search history
            if self.current_query not in self.search_history:
                self.search_history.append(self.current_query)
                if len(self.search_history) > 10:
                    self.search_history.pop(0)
            
            # Perform search
            filters = self.get_current_filters()
            results = await knowledge_service.search_documents(
                query=self.current_query,
                filters=filters,
                limit=50
            )
            
            self.search_results = results
            self.display_search_results()
            
            if self.on_search:
                self.on_search(results)
                
        except Exception as e:
            ui.notify(f"Search error: {str(e)}", type="error")
        finally:
            self.is_searching = False
            self.update_search_ui()
    
    def display_search_results(self):
        """Display search results."""
        self.results_container.clear()
        
        with self.results_container:
            # Results header
            with ui.element("div").classes("flex items-center justify-between p-4 bg-gray-50 rounded"):
                if self.search_results:
                    ui.label(f"{len(self.search_results)} {t('knowledge.results_found')}")
                else:
                    ui.label(t("knowledge.no_results"))
                
                # Export results button
                if self.search_results:
                    ui.button(
                        t("knowledge.export_results"),
                        icon="download",
                        on_click=self.export_results
                    ).classes("text-sm bg-green-600 text-white")
            
            # Results list
            if self.search_results:
                for result in self.search_results:
                    self.create_result_item(result)
            else:
                with ui.element("div").classes("text-center py-8"):
                    ui.icon("search_off").classes("text-6xl text-gray-300 mb-4")
                    ui.label(t("knowledge.no_results_message")).classes("text-gray-500")
    
    def create_result_item(self, result: SearchResult):
        """Create a search result item."""
        with ui.element("div").classes("border rounded-lg p-4 hover:shadow-md transition-shadow"):
            with ui.row().classes("items-start justify-between"):
                # Result content
                with ui.column().classes("flex-1"):
                    # Title and score
                    with ui.row().classes("items-center space-x-2 mb-2"):
                        ui.label(result.document_name).classes("font-medium text-lg")
                        ui.badge(f"{result.score:.2f}").classes("bg-blue-100 text-blue-700")
                    
                    # Content preview
                    content_preview = result.content[:300] + "..." if len(result.content) > 300 else result.content
                    ui.label(content_preview).classes("text-gray-700 mb-2")
                    
                    # Metadata
                    with ui.row().classes("items-center space-x-4 text-sm text-gray-500"):
                        ui.label(f"Chunk {result.chunk_index}")
                        ui.label(f"Position {result.start_position}-{result.end_position}")
                        
                        # Highlight matched terms
                        if hasattr(result, 'highlighted_content'):
                            ui.html(result.highlighted_content).classes("text-sm")
                
                # Actions
                with ui.column().classes("space-y-2"):
                    ui.button(
                        icon="visibility",
                        on_click=lambda: self.view_document(result.document_id)
                    ).classes("w-8 h-8 bg-gray-100 text-gray-600")
                    
                    ui.button(
                        icon="download",
                        on_click=lambda: self.download_document(result.document_id)
                    ).classes("w-8 h-8 bg-gray-100 text-gray-600")
    
    def update_search_suggestions(self):
        """Update search suggestions based on current query."""
        # This would typically call an API for suggestions
        # For now, we'll just show static suggestions
        pass
    
    def update_search_ui(self):
        """Update search UI based on current state."""
        if self.is_searching:
            self.search_input.disable()
        else:
            self.search_input.enable()
    
    def toggle_advanced_filters(self):
        """Toggle advanced filters visibility."""
        if "hidden" in self.filters_container.classes:
            self.filters_container.classes("block")
        else:
            self.filters_container.classes("hidden")
    
    def set_search_query(self, query: str):
        """Set search query."""
        self.current_query = query
        self.search_input.value = query
        self.perform_search()
    
    def show_search_history(self):
        """Show search history dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-md"):
            ui.label(t("knowledge.search_history")).classes("text-lg font-medium mb-4")
            
            if self.search_history:
                with ui.column().classes("space-y-2"):
                    for query in reversed(self.search_history):
                        ui.button(
                            query,
                            on_click=lambda q=query: self.set_search_query(q)
                        ).classes("w-full text-left justify-start bg-gray-50 hover:bg-gray-100")
            else:
                ui.label(t("knowledge.no_search_history")).classes("text-gray-500 text-center py-4")
    
    def save_current_search(self):
        """Save current search as a saved search."""
        if not self.current_query:
            ui.notify(t("knowledge.no_query_to_save"), type="warning")
            return
        
        # This would typically save to user preferences
        ui.notify(t("knowledge.search_saved"), type="positive")
    
    def export_results(self):
        """Export search results."""
        if not self.search_results:
            return
        
        # This would typically export to CSV or JSON
        ui.notify(t("knowledge.results_exported"), type="positive")
    
    def view_document(self, document_id: str):
        """View document details."""
        # This would typically open a document viewer
        ui.notify(f"Viewing document {document_id}", type="info")
    
    def download_document(self, document_id: str):
        """Download document."""
        # This would typically trigger a download
        ui.notify(f"Downloading document {document_id}", type="info")


def create_advanced_search_component(
    on_search: Optional[Callable[[List[SearchResult]], None]] = None,
    on_filter_change: Optional[Callable[[Dict[str, Any]], None]] = None
) -> AdvancedSearchComponent:
    """
    Create an advanced search component.
    
    Args:
        on_search: Callback for search results
        on_filter_change: Callback for filter changes
        
    Returns:
        AdvancedSearchComponent instance
    """
    return AdvancedSearchComponent(on_search=on_search, on_filter_change=on_filter_change) 