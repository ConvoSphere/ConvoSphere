"""
Chat Interface Page.

This page provides a modern chat interface for conversations with AI assistants,
including real-time messaging, tool execution, and conversation management.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from services.api import api_client
from services.auth_service import auth_service


class ChatPage:
    """Chat interface page."""
    
    def __init__(self):
        self.current_conversation_id: Optional[int] = None
        self.current_assistant_id: Optional[int] = None
        self.messages: List[Dict[str, Any]] = []
        self.assistants: List[Dict[str, Any]] = []
        self.tools: List[Dict[str, Any]] = []
        self.conversations: List[Dict[str, Any]] = []
        self.is_loading = False
        self.is_typing = False
        self.search_query = ""
        self.search_results: List[Dict[str, Any]] = []
        self.is_searching = False
        
        # WebSocket connection
        self.websocket = None
        
        # UI elements
        self.conversations_list = None
        self.messages_container = None
        self.message_input = None
        self.assistant_selector = None
        
        self.create_page()
    
    def create_page(self):
        """Create the chat page layout."""
        with ui.column().classes("w-full h-full"):
            # Header
            with ui.row().classes("w-full p-4 bg-white border-b border-gray-200"):
                with ui.row().classes("flex-1 items-center gap-4"):
                    ui.label("Chat").classes("text-2xl font-bold")
                    
                    # Assistant selector
                    self.assistant_selector = ui.select(
                        label="Select Assistant",
                        options=[],
                        on_change=self.on_assistant_change
                    ).classes("w-64")
                    
                    # New conversation button
                    ui.button("New Chat", on_click=self.start_new_conversation).classes("bg-blue-500 text-white")
                
                with ui.row().classes("items-center gap-2"):
                    ui.button("Settings", on_click=self.show_settings).classes("bg-gray-500 text-white")
            
            # Main chat area
            with ui.row().classes("w-full h-full flex-1 gap-0"):
                # Conversations sidebar
                with ui.column().classes("w-80 bg-gray-50 border-r border-gray-200 p-4"):
                    ui.label("Conversations").classes("text-lg font-semibold mb-4")
                    
                    # Search conversations
                    search_input = ui.input(
                        "Search conversations...",
                        on_change=self.on_search_change
                    ).classes("w-full mb-4")
                    
                    # Search button
                    ui.button(
                        "Search",
                        on_click=self.search_conversations,
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
                    
                    # Conversations list
                    self.conversations_list = ui.column().classes("w-full flex-1 overflow-y-auto")
                    
                    # Load conversations button
                    ui.button("Load More", on_click=self.load_conversations).classes("w-full mt-4 bg-gray-500 text-white")
                
                # Chat area
                with ui.column().classes("flex-1 flex flex-col"):
                    # Messages area
                    with ui.column().classes("flex-1 p-4 overflow-y-auto") as messages_area:
                        self.messages_container = messages_area
                    
                    # Input area
                    with ui.row().classes("p-4 border-t border-gray-200 bg-white"):
                        with ui.row().classes("w-full items-end gap-2"):
                            # Message input
                            self.message_input = ui.textarea(
                                placeholder="Type your message...",
                                rows=1,
                                auto_grow=True,
                                on_keydown=self.on_message_keydown
                            ).classes("flex-1 min-h-[40px] max-h-[120px]")
                            
                            # Send button
                            ui.button(
                                "Send",
                                on_click=self.send_message,
                                icon="send"
                            ).classes("bg-blue-500 text-white px-6 py-2")
                            
                            # Tools button
                            ui.button(
                                "Tools",
                                on_click=self.show_tools,
                                icon="build"
                            ).classes("bg-gray-500 text-white px-4 py-2")
            
            # Create dialogs
            self.create_settings_dialog()
            self.create_tools_dialog()
            self.create_new_conversation_dialog()
            
            # Load initial data
            asyncio.create_task(self.load_initial_data())
    
    def create_settings_dialog(self):
        """Create the settings dialog."""
        with ui.dialog() as self.settings_dialog, ui.card().classes("w-96"):
            ui.label("Chat Settings").classes("text-lg font-semibold mb-4")
            
            # Model settings
            ui.label("AI Model").classes("font-medium mb-2")
            model_select = ui.select(
                options=["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"],
                value="gpt-4"
            ).classes("w-full mb-4")
            
            # Temperature setting
            ui.label("Creativity (Temperature)").classes("font-medium mb-2")
            temperature_slider = ui.slider(min=0, max=2, step=0.1, value=0.7).classes("w-full mb-4")
            
            # Max tokens
            ui.label("Max Tokens").classes("font-medium mb-2")
            max_tokens_input = ui.number(min=100, max=4000, value=2000).classes("w-full mb-4")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.settings_dialog.close).classes("bg-gray-500")
                ui.button("Save", on_click=self.save_settings).classes("bg-blue-500")
    
    def create_tools_dialog(self):
        """Create the tools dialog."""
        with ui.dialog() as self.tools_dialog, ui.card().classes("w-96"):
            ui.label("Available Tools").classes("text-lg font-semibold mb-4")
            
            # Assistant info
            if self.current_assistant_id:
                assistant = next((a for a in self.assistants if a['id'] == self.current_assistant_id), None)
                if assistant:
                    ui.label(f"Assistant: {assistant.get('name', 'Unknown Assistant')}").classes("text-sm text-gray-600 mb-4")
            
            self.tools_list = ui.column().classes("w-full max-h-64 overflow-y-auto")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.tools_dialog.close).classes("bg-gray-500")
                ui.button("Refresh", on_click=self.load_assistant_tools).classes("bg-blue-500")
    
    def create_new_conversation_dialog(self):
        """Create the new conversation dialog."""
        with ui.dialog() as self.new_conversation_dialog, ui.card().classes("w-96"):
            ui.label("Start New Conversation").classes("text-lg font-semibold mb-4")
            
            # Assistant selection
            ui.label("Select Assistant").classes("font-medium mb-2")
            assistant_select = ui.select(
                options=[(a['id'], a['name']) for a in self.assistants],
                value=self.current_assistant_id
            ).classes("w-full mb-4")
            
            # Title input
            ui.label("Conversation Title (Optional)").classes("font-medium mb-2")
            title_input = ui.input("New Conversation").classes("w-full mb-4")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.new_conversation_dialog.close).classes("bg-gray-500")
                ui.button("Create", on_click=self.create_conversation).classes("bg-blue-500")
    
    async def load_initial_data(self):
        """Load initial data for the chat page."""
        try:
            self.is_loading = True
            
            # Load assistants
            assistants_response = await api_client.get_assistants()
            if assistants_response.success and assistants_response.data:
                self.assistants = assistants_response.data
                if self.assistants:
                    self.current_assistant_id = self.assistants[0]['id']
                self.update_assistant_selector()
            
            # Load conversations
            await self.load_conversations()
            
            # Load tools
            tools_response = await api_client.get_tools()
            if tools_response.success and tools_response.data:
                self.tools = tools_response.data
                
        except Exception as e:
            ui.notify(f"Error loading data: {str(e)}", type="error")
        finally:
            self.is_loading = False
    
    def update_assistant_selector(self):
        """Update the assistant selector options."""
        if self.assistant_selector:
            options = [(a['id'], a['name']) for a in self.assistants]
            self.assistant_selector.options = options
            if options and not self.current_assistant_id:
                self.current_assistant_id = options[0][0]
                self.assistant_selector.value = self.current_assistant_id
    
    async def load_conversations(self):
        """Load user conversations."""
        try:
            conversations_response = await api_client.get_conversations()
            if conversations_response.success and conversations_response.data:
                self.conversations = conversations_response.data
                self.update_conversations_list()
            else:
                ui.notify(f"Error loading conversations: {conversations_response.error}", type="error")
        except Exception as e:
            ui.notify(f"Error loading conversations: {str(e)}", type="error")
    
    def update_conversations_list(self):
        """Update the conversations list display."""
        if not self.conversations_list:
            return
        
        # Clear existing conversations
        self.conversations_list.clear()
        
        # Add conversations
        for conversation in self.conversations:
            with self.conversations_list:
                with ui.card().classes("w-full p-3 cursor-pointer hover:bg-blue-50").on("click", lambda c=conversation: self.select_conversation(str(c['id']))):
                    with ui.column().classes("w-full"):
                        ui.label(conversation.get('title', 'Untitled')).classes("font-semibold text-sm")
                        ui.label(conversation.get('assistant_name', 'Unknown Assistant')).classes("text-xs text-gray-600")
                        
                        with ui.row().classes("w-full justify-between items-center mt-2"):
                            ui.label(f"{conversation.get('message_count', 0)} messages").classes("text-xs text-gray-500")
                            ui.label(conversation.get('updated_at', 'Unknown')).classes("text-xs text-gray-500")
    
    async def select_conversation(self, conversation_id: str):
        """Select a conversation to load."""
        try:
            self.current_conversation_id = int(conversation_id)
            
            # Load messages
            messages_response = await api_client.get_conversation_messages(conversation_id)
            if messages_response.success and messages_response.data:
                self.messages = messages_response.data
                self.update_messages_display()
            else:
                ui.notify(f"Error loading messages: {messages_response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error selecting conversation: {str(e)}", type="error")
    
    def update_messages_display(self):
        """Update the messages display."""
        if not self.messages_container:
            return
        
        # Clear existing messages
        self.messages_container.clear()
        
        # Add messages
        for message in self.messages:
            with self.messages_container:
                self.create_message_bubble(message)
    
    def create_message_bubble(self, message: Dict[str, Any]):
        """Create a message bubble for display."""
        is_user = message.get('role', 'user') == "user"
        
        with ui.row().classes(f"w-full justify-{'end' if is_user else 'start'} mb-4"):
            with ui.column().classes("max-w-3xl"):
                # Message bubble
                bubble_classes = "p-3 rounded-lg"
                if is_user:
                    bubble_classes += " bg-blue-500 text-white"
                else:
                    bubble_classes += " bg-gray-200"
                
                with ui.card().classes(bubble_classes):
                    if message.get('tool_result'):
                        self.create_tool_result_display(message)
                    else:
                        ui.label(message.get('content', '')).classes("whitespace-pre-wrap")
                
                # Timestamp
                timestamp = message.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime("%H:%M")
                    except:
                        time_str = timestamp
                else:
                    time_str = "Unknown"
                
                ui.label(time_str).classes("text-xs text-gray-500 mt-1")
    
    def create_tool_result_display(self, message: Dict[str, Any]):
        """Create a tool result display."""
        metadata = message.get('metadata', {}) or {}
        
        with ui.column().classes("w-full"):
            # Tool header
            tool_name = metadata.get("tool_name", "Unknown Tool")
            ui.label(f"🔧 {tool_name}").classes("font-semibold text-sm mb-2")
            
            # Tool result
            if isinstance(message.get('content', ''), dict):
                result_data = message.get('content', {})
            else:
                result_data = {"result": message.get('content', 'Success')}
            
            # Display result in a formatted way
            if isinstance(result_data, dict):
                for key, value in result_data.items():
                    if key != "tool_name":
                        ui.label(f"{key}: {value}").classes("text-sm")
            else:
                ui.label(str(result_data)).classes("text-sm")
    
    async def send_message(self):
        """Send a message to the current conversation."""
        if not self.message_input or not self.message_input.value.strip():
            return
        
        if not self.current_conversation_id:
            ui.notify("Please select a conversation first", type="warning")
            return
        
        try:
            self.is_typing = True
            content = self.message_input.value.strip()
            
            # Add user message to display immediately
            user_message = {
                'id': len(self.messages) + 1,
                'content': content,
                'role': 'user',
                'timestamp': datetime.now().isoformat(),
                'conversation_id': self.current_conversation_id
            }
            self.messages.append(user_message)
            self.update_messages_display()
            
            # Clear input
            self.message_input.value = ""
            
            # Search knowledge base for RAG context
            knowledge_results = await self.search_knowledge_base()
            
            # Send message to backend
            response = await api_client.send_message(
                str(self.current_conversation_id),
                content
            )
            
            if response.success:
                # The response will come through WebSocket or be added here
                pass
            else:
                ui.notify(f"Error sending message: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error sending message: {str(e)}", type="error")
        finally:
            self.is_typing = False
    
    def scroll_to_bottom(self):
        """Scroll messages to bottom."""
        # This would scroll the messages container to the bottom
        pass
    
    def on_assistant_change(self, e: ValueChangeEventArguments):
        """Handle assistant selection change."""
        self.current_assistant_id = e.value
        # Update current conversation if needed
        pass
    
    def start_new_conversation(self):
        """Start a new conversation."""
        self.new_conversation_dialog.open()
    
    async def create_conversation(self, assistant_id: str = None, title: str = None):
        """Create a new conversation."""
        try:
            if not assistant_id:
                assistant_id = str(self.current_assistant_id) if self.current_assistant_id else None
            if not title:
                title = "New Conversation"
                
            if not assistant_id:
                ui.notify("Please select an assistant first", type="warning")
                return
                
            response = await api_client.create_conversation(assistant_id, title)
            
            if response.success and response.data:
                conversation = response.data
                self.conversations.insert(0, conversation)
                self.current_conversation_id = int(conversation['id'])
                self.messages = []
                
                self.update_conversations_list()
                self.update_messages_display()
                self.new_conversation_dialog.close()
                
                ui.notify("New conversation created", type="positive")
            else:
                ui.notify(f"Error creating conversation: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error creating conversation: {str(e)}", type="error")
    
    def show_settings(self):
        """Show settings dialog."""
        self.settings_dialog.open()
    
    def save_settings(self):
        """Save chat settings."""
        # Save settings logic here
        self.settings_dialog.close()
        ui.notify("Settings saved", type="positive")
    
    def show_tools(self):
        """Show tools dialog."""
        self.tools_dialog.open()
        asyncio.create_task(self.load_assistant_tools())
    
    async def load_assistant_tools(self):
        """Load tools available for the current assistant."""
        try:
            if not self.current_conversation_id:
                ui.notify("Please select a conversation first", type="warning")
                return
            
            # Get assistant details to see configured tools
            assistant = next((a for a in self.assistants if a['id'] == self.current_assistant_id), None)
            if not assistant:
                ui.notify("Error loading assistant details", type="error")
                return
            
            configured_tools = assistant.get("tools_config", [])
            
            # Clear existing tools
            if self.tools_list:
                self.tools_list.clear()
            
            # Load all available tools
            all_tools = []
            
            # Regular tools
            tools_response = await api_client.get_tools()
            if tools_response.success and tools_response.data:
                all_tools.extend(tools_response.data)
            
            # MCP tools
            mcp_tools_response = await api_client.get_mcp_tools()
            if mcp_tools_response.success and mcp_tools_response.data:
                all_tools.extend(mcp_tools_response.data)
            
            # Filter tools for this assistant
            available_tools = []
            for tool in all_tools:
                if tool['id'] in configured_tools or not configured_tools:
                    available_tools.append(tool)
            
            # Display tools
            if self.tools_list:
                for tool in available_tools:
                    with self.tools_list:
                        with ui.card().classes("w-full p-3 mb-2"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label(tool.get('name', 'Unknown Tool')).classes("font-semibold")
                                ui.button(
                                    "Use",
                                    on_click=lambda t=tool: self.use_tool(t),
                                    size="sm"
                                ).classes("bg-blue-500 text-white")
                            
                            ui.label(tool.get('description', 'No description')).classes("text-sm text-gray-600")
                            
                            if tool.get('category'):
                                ui.label(f"Category: {tool['category']}").classes("text-xs text-gray-500")
            
        except Exception as e:
            ui.notify(f"Error loading tools: {str(e)}", type="error")
    
    def use_tool(self, tool: Dict[str, Any]):
        """Use a tool in the current conversation."""
        if not self.current_conversation_id:
            ui.notify("Please select a conversation first", type="warning")
            return
        
        # For now, just show a notification
        ui.notify(f"Tool {tool['name']} would be executed here", type="info")
        self.tools_dialog.close()
    
    async def search_conversations(self):
        """Search conversations using semantic search"""
        if not self.search_query.strip():
            self.search_results = []
            return
            
        self.is_searching = True
        try:
            # Use the internal _make_request method for custom endpoints
            response = await api_client._make_request(
                "POST",
                "/api/v1/search/conversations",
                data={
                    "query": self.search_query,
                    "conversation_id": self.current_conversation_id
                }
            )
            
            if response.success and response.data:
                self.search_results = response.data
            else:
                ui.notify(f'Search failed: {response.error}', type='error')
                
        except Exception as e:
            ui.notify(f'Search error: {str(e)}', type='error')
        finally:
            self.is_searching = False
    
    async def search_knowledge_base(self):
        """Search knowledge base for RAG context"""
        if not self.search_query.strip():
            return []
            
        try:
            # Use the internal _make_request method for custom endpoints
            response = await api_client._make_request(
                "POST",
                "/api/v1/search/knowledge",
                data={"query": self.search_query}
            )
            
            if response.success and response.data:
                return response.data
            else:
                ui.notify(f'Knowledge search failed: {response.error}', type='error')
                return []
                
        except Exception as e:
            ui.notify(f'Knowledge search error: {str(e)}', type='error')
            return []
    
    async def on_search_change(self, e: ValueChangeEventArguments):
        """Handle search input change"""
        self.search_query = e.value
    
    async def on_message_keydown(self, e):
        """Handle message input keydown"""
        if e.key == 'Enter' and not e.shift:
            await self.send_message()


# Create page instance
chat_page = ChatPage()

async def setup():
    """Setup the chat page."""
    pass

def create_page():
    """Create the chat page."""
    return setup() 