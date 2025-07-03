"""
Advanced search component for the AI Assistant Platform.

This module provides comprehensive search functionality for the knowledge base
including filters, highlighting, and result management.
"""

from nicegui import ui
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from services.knowledge_service import SearchResult, Document, DocumentStatus, DocumentType
from utils.helpers import format_timestamp, highlight_text


class AdvancedSearchComponent:
    """Advanced search component for knowledge base."""
    
    def __init__(
        self,
        on_search: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_result_select: Optional[Callable[[SearchResult], None]] = None
    ):
        """
        Initialize search component.
        
        Args:
            on_search: Search callback function
            on_result_select: Result selection callback function
        """
        self.on_search = on_search
        self.on_result_select = on_result_select
        
        # Search state
        self.search_query = ""
        self.search_filters = {}
        self.search_results: List[SearchResult] = []
        self.is_searching = False
        self.current_page = 1
        self.results_per_page = 20
        
        # UI components
        self.container = None
        self.search_input = None
        self.filters_container = None
        self.results_container = None
        self.pagination_container = None
        
        self.create_search_component()
    
    def create_search_component(self):
        """Create the search component UI."""
        self.container = ui.element("div").classes("w-full")
        
        with self.container:
            # Search input
            self.create_search_input()
            
            # Filters
            self.create_filters()
            
            # Results
            self.create_results_section()
            
            # Pagination
            self.create_pagination()
    
    def create_search_input(self):
        """Create search input section."""
        with ui.element("div").classes("mb-6"):
            with ui.row().classes("items-center space-x-4"):
                # Search input
                self.search_input = ui.input(
                    placeholder="Dokumente durchsuchen...",
                    on_keydown=self.handle_search_keydown
                ).classes("flex-1")
                
                # Search button
                ui.button(
                    "Suchen",
                    icon="search",
                    on_click=self.perform_search
                ).classes("bg-blue-600 text-white")
                
                # Advanced search toggle
                ui.button(
                    "Filter",
                    icon="tune",
                    on_click=self.toggle_advanced_filters
                ).classes("bg-gray-500 text-white")
    
    def create_filters(self):
        """Create advanced filters section."""
        self.filters_container = ui.element("div").classes("mb-6 bg-gray-50 border rounded-lg p-4")
        
        with self.filters_container:
            with ui.row().classes("items-center space-x-4"):
                # Category filter
                self.category_filter = ui.select(
                    "Kategorie",
                    options=["alle"] + self.get_available_categories(),
                    value="alle",
                    on_change=self.update_filters
                ).classes("w-48")
                
                # Status filter
                self.status_filter = ui.select(
                    "Status",
                    options=["alle"] + [s.value for s in DocumentStatus],
                    value="alle",
                    on_change=self.update_filters
                ).classes("w-48")
                
                # Date range
                self.date_from = ui.date("Von").classes("w-32")
                self.date_to = ui.date("Bis").classes("w-32")
                
                # Results per page
                self.results_per_page_select = ui.select(
                    "Ergebnisse pro Seite",
                    options=["10", "20", "50", "100"],
                    value="20",
                    on_change=self.update_results_per_page
                ).classes("w-32")
                
                # Clear filters
                ui.button(
                    "Filter löschen",
                    icon="clear",
                    on_click=self.clear_filters
                ).classes("bg-red-500 text-white text-xs")
    
    def create_results_section(self):
        """Create search results section."""
        with ui.element("div").classes("mb-6"):
            # Results header
            self.results_header = ui.element("div").classes("mb-4")
            
            # Results container
            self.results_container = ui.element("div").classes("space-y-4")
    
    def create_pagination(self):
        """Create pagination section."""
        self.pagination_container = ui.element("div").classes("flex justify-center items-center space-x-2")
    
    def handle_search_keydown(self, event):
        """Handle search input keydown."""
        if event.key == "Enter":
            self.perform_search()
    
    def perform_search(self):
        """Perform search with current query and filters."""
        if not self.search_query.strip():
            ui.notify("Bitte geben Sie einen Suchbegriff ein", type="warning")
            return
        
        self.is_searching = True
        self.current_page = 1
        
        # Update search filters
        self.update_filters()
        
        # Call search callback
        if self.on_search:
            self.on_search(self.search_query, self.search_filters)
    
    def update_filters(self):
        """Update search filters."""
        self.search_filters = {
            "category": self.category_filter.value if self.category_filter.value != "alle" else None,
            "status": self.status_filter.value if self.status_filter.value != "alle" else None,
            "date_from": self.date_from.value.isoformat() if self.date_from.value else None,
            "date_to": self.date_to.value.isoformat() if self.date_to.value else None,
            "page": self.current_page,
            "limit": self.results_per_page
        }
    
    def update_results_per_page(self, event):
        """Update results per page."""
        self.results_per_page = int(event.value)
        self.current_page = 1
        if self.search_results:
            self.perform_search()
    
    def clear_filters(self):
        """Clear all filters."""
        self.category_filter.value = "alle"
        self.status_filter.value = "alle"
        self.date_from.value = None
        self.date_to.value = None
        self.search_filters = {}
    
    def toggle_advanced_filters(self):
        """Toggle advanced filters visibility."""
        if self.filters_container:
            self.filters_container.visible = not self.filters_container.visible
    
    def get_available_categories(self) -> List[str]:
        """Get available document categories."""
        # This would be populated from the knowledge service
        return ["Dokumentation", "Anleitungen", "Berichte", "Präsentationen"]
    
    def display_search_results(self, results: List[SearchResult], total_results: int = 0):
        """Display search results."""
        self.search_results = results
        
        # Update results header
        self.results_header.clear()
        with self.results_header:
            if results:
                ui.label(f"{len(results)} von {total_results} Ergebnissen gefunden").classes("text-lg font-medium")
            else:
                ui.label("Keine Ergebnisse gefunden").classes("text-lg text-gray-500")
        
        # Display results
        self.results_container.clear()
        
        if not results:
            with self.results_container:
                ui.label("Versuchen Sie andere Suchbegriffe oder Filter").classes("text-center text-gray-500 py-8")
            return
        
        with self.results_container:
            for result in results:
                self.create_result_item(result)
        
        # Update pagination
        self.update_pagination(total_results)
    
    def create_result_item(self, result: SearchResult):
        """Create a search result item."""
        with ui.element("div").classes("bg-white border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer").on("click", lambda: self.select_result(result)):
            # Result header
            with ui.row().classes("items-center justify-between mb-2"):
                ui.label(result.document_name).classes("font-medium text-blue-600")
                ui.label(f"Score: {result.score:.3f}").classes("text-sm text-gray-600")
            
            # Highlighted content
            highlighted_content = highlight_text(result.content, self.search_query)
            ui.html(f"<div class='text-sm text-gray-700 mb-2'>{highlighted_content}</div>")
            
            # Metadata
            with ui.row().classes("items-center justify-between text-xs text-gray-500"):
                with ui.row().classes("items-center space-x-4"):
                    ui.label(f"Chunk {result.chunk_index}")
                    ui.label(f"Position {result.start_position}-{result.end_position}")
                
                # Action buttons
                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Dokument öffnen",
                        icon="open_in_new",
                        on_click=lambda: self.open_document(result.document_id)
                    ).classes("bg-blue-500 text-white text-xs")
                    
                    ui.button(
                        "Kopieren",
                        icon="content_copy",
                        on_click=lambda: self.copy_content(result.content)
                    ).classes("bg-gray-500 text-white text-xs")
    
    def update_pagination(self, total_results: int):
        """Update pagination controls."""
        self.pagination_container.clear()
        
        if total_results <= self.results_per_page:
            return
        
        total_pages = (total_results + self.results_per_page - 1) // self.results_per_page
        
        with self.pagination_container:
            # Previous page
            if self.current_page > 1:
                ui.button(
                    "Zurück",
                    icon="chevron_left",
                    on_click=self.previous_page
                ).classes("bg-gray-500 text-white")
            
            # Page numbers
            start_page = max(1, self.current_page - 2)
            end_page = min(total_pages, self.current_page + 2)
            
            for page in range(start_page, end_page + 1):
                if page == self.current_page:
                    ui.button(str(page)).classes("bg-blue-600 text-white")
                else:
                    ui.button(
                        str(page),
                        on_click=lambda p=page: self.go_to_page(p)
                    ).classes("bg-gray-200 text-gray-700")
            
            # Next page
            if self.current_page < total_pages:
                ui.button(
                    "Weiter",
                    icon="chevron_right",
                    on_click=self.next_page
                ).classes("bg-gray-500 text-white")
    
    def select_result(self, result: SearchResult):
        """Select a search result."""
        if self.on_result_select:
            self.on_result_select(result)
    
    def open_document(self, document_id: str):
        """Open document in new view."""
        ui.notify(f"Dokument {document_id} wird geöffnet", type="info")
    
    def copy_content(self, content: str):
        """Copy content to clipboard."""
        # In a real implementation, this would copy to clipboard
        ui.notify("Inhalt in Zwischenablage kopiert", type="positive")
    
    def previous_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.perform_search()
    
    def next_page(self):
        """Go to next page."""
        self.current_page += 1
        self.perform_search()
    
    def go_to_page(self, page: int):
        """Go to specific page."""
        self.current_page = page
        self.perform_search()
    
    def set_search_query(self, query: str):
        """Set search query."""
        self.search_query = query
        if self.search_input:
            self.search_input.value = query
    
    def get_search_query(self) -> str:
        """Get current search query."""
        return self.search_query
    
    def get_search_filters(self) -> Dict[str, Any]:
        """Get current search filters."""
        return self.search_filters.copy()
    
    def clear_results(self):
        """Clear search results."""
        self.search_results = []
        self.results_container.clear()
        self.pagination_container.clear()
    
    def show_loading(self):
        """Show loading state."""
        self.is_searching = True
        self.results_container.clear()
        
        with self.results_container:
            with ui.row().classes("justify-center py-8"):
                ui.spinner("dots").classes("w-8 h-8")
                ui.label("Suche läuft...").classes("ml-2 text-gray-600")
    
    def hide_loading(self):
        """Hide loading state."""
        self.is_searching = False


def create_advanced_search_component(
    on_search: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    on_result_select: Optional[Callable[[SearchResult], None]] = None
) -> AdvancedSearchComponent:
    """
    Create an advanced search component.
    
    Args:
        on_search: Search callback function
        on_result_select: Result selection callback function
        
    Returns:
        AdvancedSearchComponent instance
    """
    return AdvancedSearchComponent(
        on_search=on_search,
        on_result_select=on_result_select
    ) 