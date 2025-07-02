"""
Chat Interface Page.

This page provides a modern chat interface for conversations with AI assistants,
including real-time messaging, tool execution, and conversation management.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from nicegui import ui, app
import asyncio

from services.api import api_client
from services.auth_service import auth_service
from services.conversation_service import conversation_service


@dataclass
class Message:
    """Chat message data model."""
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Conversation:
    """Conversation data model."""
    id: str
    title: str
    assistant_id: str
    assistant_name: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ChatPage:
    """Chat interface page."""
    
    def __init__(self):
        self.conversations: List[Conversation] = []
        self.current_conversation: Optional[Conversation] = None
        self.messages: List[Message] = []
        self.assistants: List[Dict[str, Any]] = []
        self.is_loading = False
        self.is_sending = False
        
        # UI elements
        self.conversations_list = None
        self.messages_container = None
        self.message_input = None
        self.assistant_selector = None
        self.selected_tool = None
        self.tool_execution_dialog = None
        
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
                    ui.input("Search conversations...").classes("w-full mb-4")
                    
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
                                auto_grow=True
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
            self.load_initial_data()
    
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
            if self.current_conversation:
                ui.label(f"Assistant: {self.current_conversation.assistant_name}").classes("text-sm text-gray-600 mb-4")
            
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
                label="Assistant",
                options=[],
                on_change=lambda e: setattr(self, 'selected_assistant_id', e.value)
            ).classes("w-full mb-4")
            
            # Conversation title
            title_input = ui.input("Conversation Title (Optional)").classes("w-full mb-4")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.new_conversation_dialog.close).classes("bg-gray-500")
                ui.button("Start", on_click=lambda: self.create_conversation(
                    assistant_select.value,
                    title_input.value
                )).classes("bg-blue-500")
    
    async def load_initial_data(self):
        """Load initial data for the chat page."""
        try:
            self.is_loading = True
            
            # Load assistants
            assistants_response = await api_client.get_assistants()
            if assistants_response.success:
                self.assistants = assistants_response.data
                self.update_assistant_selector()
            
            # Load conversations
            await self.load_conversations()
            
        except Exception as e:
            ui.notify(f"Error loading data: {e}", type="error")
        finally:
            self.is_loading = False
    
    def update_assistant_selector(self):
        """Update the assistant selector options."""
        if not self.assistant_selector:
            return
        
        options = [
            {"label": assistant["name"], "value": assistant["id"]}
            for assistant in self.assistants
        ]
        
        self.assistant_selector.options = options
        if options:
            self.assistant_selector.value = options[0]["value"]
    
    async def load_conversations(self):
        """Load user conversations."""
        try:
            conversations_response = await api_client.get_conversations()
            if conversations_response.success:
                self.conversations = [
                    Conversation(**conv_data) for conv_data in conversations_response.data
                ]
                self.update_conversations_list()
            
        except Exception as e:
            ui.notify(f"Error loading conversations: {e}", type="error")
    
    def update_conversations_list(self):
        """Update the conversations list UI."""
        if not self.conversations_list:
            return
        
        # Clear existing content
        self.conversations_list.clear()
        
        for conversation in self.conversations:
            with self.conversations_list:
                with ui.card().classes("w-full p-3 cursor-pointer hover:bg-blue-50").on("click", lambda c=conversation: self.select_conversation(c)):
                    with ui.column().classes("w-full"):
                        ui.label(conversation.title or "Untitled").classes("font-semibold text-sm")
                        ui.label(conversation.assistant_name).classes("text-xs text-gray-600")
                        
                        with ui.row().classes("w-full justify-between items-center mt-2"):
                            ui.label(f"{conversation.message_count} messages").classes("text-xs text-gray-500")
                            ui.label(conversation.updated_at.strftime("%m/%d")).classes("text-xs text-gray-500")
    
    async def select_conversation(self, conversation: Conversation):
        """Select a conversation to load."""
        try:
            self.current_conversation = conversation
            
            # Load messages
            messages_response = await api_client.get_conversation_messages(conversation.id)
            if messages_response.success:
                self.messages = [
                    Message(**msg_data) for msg_data in messages_response.data
                ]
                self.update_messages_display()
            
        except Exception as e:
            ui.notify(f"Error loading conversation: {e}", type="error")
    
    def update_messages_display(self):
        """Update the messages display."""
        if not self.messages_container:
            return
        
        # Clear existing content
        self.messages_container.clear()
        
        for message in self.messages:
            with self.messages_container:
                self.create_message_bubble(message)
    
    def create_message_bubble(self, message: Message):
        """Create a message bubble for display."""
        is_user = message.role == "user"
        
        with ui.row().classes(f"w-full justify-{'end' if is_user else 'start'} mb-4"):
            with ui.column().classes(f"max-w-[70%] {'items-end' if is_user else 'items-start'}"):
                # Message bubble
                bubble_classes = "p-3 rounded-lg"
                if is_user:
                    bubble_classes += " bg-blue-500 text-white"
                else:
                    bubble_classes += " bg-gray-100 text-gray-800"
                
                with ui.card().classes(bubble_classes):
                    if message.message_type == "text":
                        ui.label(message.content).classes("whitespace-pre-wrap")
                    elif message.message_type == "tool_result":
                        self.create_tool_result_display(message)
                    else:
                        ui.label(f"[{message.message_type}] {message.content}")
                
                # Timestamp
                ui.label(message.timestamp.strftime("%H:%M")).classes("text-xs text-gray-500 mt-1")
    
    def create_tool_result_display(self, message: Message):
        """Create a tool result display."""
        metadata = message.metadata or {}
        
        with ui.column().classes("w-full"):
            # Tool name
            tool_name = metadata.get("tool_name", "Unknown Tool")
            ui.label(f"🔧 {tool_name}").classes("font-semibold text-sm mb-2")
            
            # Tool result
            if isinstance(message.content, dict):
                result_data = message.content
            else:
                result_data = {"result": message.content}
            
            # Display result in a formatted way
            with ui.expansion("View Result", icon="info").classes("w-full"):
                ui.code(str(result_data)).classes("w-full text-xs")
    
    async def send_message(self):
        """Send a message to the current conversation."""
        if not self.message_input or not self.message_input.value.strip():
            return
        
        if not self.current_conversation:
            ui.notify("Please select a conversation first", type="warning")
            return
        
        try:
            self.is_sending = True
            content = self.message_input.value.strip()
            
            # Add user message to display immediately
            user_message = Message(
                id=f"temp_{datetime.now().timestamp()}",
                content=content,
                role="user",
                timestamp=datetime.now()
            )
            self.messages.append(user_message)
            self.update_messages_display()
            
            # Clear input
            self.message_input.value = ""
            
            # Send message to backend
            response = await api_client.send_message(
                self.current_conversation.id,
                content
            )
            
            if response.success:
                # Add assistant response
                assistant_message = Message(
                    id=response.data.get("id", f"resp_{datetime.now().timestamp()}"),
                    content=response.data.get("content", "No response received"),
                    role="assistant",
                    timestamp=datetime.now(),
                    message_type=response.data.get("message_type", "text"),
                    metadata=response.data.get("metadata")
                )
                self.messages.append(assistant_message)
                self.update_messages_display()
                
                # Scroll to bottom
                self.scroll_to_bottom()
            else:
                ui.notify(f"Error sending message: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error sending message: {e}", type="error")
        finally:
            self.is_sending = False
    
    def scroll_to_bottom(self):
        """Scroll messages to bottom."""
        # In a real implementation, this would scroll the messages container
        pass
    
    def on_assistant_change(self, event):
        """Handle assistant selection change."""
        # Update current conversation if needed
        pass
    
    def start_new_conversation(self):
        """Start a new conversation."""
        self.new_conversation_dialog.open()
    
    async def create_conversation(self, assistant_id: str, title: str = None):
        """Create a new conversation."""
        try:
            response = await api_client.create_conversation(assistant_id, title)
            
            if response.success:
                conversation = Conversation(**response.data)
                self.conversations.insert(0, conversation)
                self.current_conversation = conversation
                self.messages = []
                
                self.update_conversations_list()
                self.update_messages_display()
                self.new_conversation_dialog.close()
                
                ui.notify("New conversation created", type="positive")
            else:
                ui.notify(f"Error creating conversation: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error creating conversation: {e}", type="error")
    
    def show_settings(self):
        """Show chat settings dialog."""
        self.settings_dialog.open()
    
    def save_settings(self):
        """Save chat settings."""
        # In a real implementation, this would save settings
        ui.notify("Settings saved", type="positive")
        self.settings_dialog.close()
    
    def show_tools(self):
        """Show tools dialog."""
        self.tools_dialog.open()
    
    async def load_assistant_tools(self):
        """Load tools available for the current assistant."""
        try:
            if not self.current_conversation:
                ui.notify("Please select a conversation first", type="warning")
                return
            
            # Get assistant details to see configured tools
            assistant_response = await api_client.get_assistant(self.current_conversation.assistant_id)
            if not assistant_response.success:
                ui.notify("Error loading assistant details", type="error")
                return
            
            assistant = assistant_response.data
            configured_tools = assistant.get("tools_config", [])
            
            # Get all available tools (including MCP tools)
            all_tools = []
            
            # Regular tools
            tools_response = await api_client.get_tools()
            if tools_response.success:
                all_tools.extend(tools_response.data)
            
            # MCP tools
            mcp_tools_response = await api_client.get_mcp_tools()
            if mcp_tools_response.success:
                all_tools.extend(mcp_tools_response.data)
            
            # Filter tools for this assistant
            available_tools = []
            for tool in all_tools:
                tool_id = tool.get("id", tool.get("name"))
                for configured_tool in configured_tools:
                    if configured_tool.get("id") == tool_id:
                        available_tools.append(tool)
                        break
            
            # Update tools list
            self.tools_list.clear()
            
            if not available_tools:
                ui.label("No tools configured for this assistant").classes("text-gray-500 text-center p-4")
                return
            
            for tool in available_tools:
                with self.tools_list:
                    with ui.card().classes("w-full p-3 mb-2 cursor-pointer hover:bg-blue-50").on("click", lambda t=tool: self.select_tool_for_execution(t)):
                        with ui.row().classes("w-full justify-between items-start"):
                            with ui.column().classes("flex-1"):
                                ui.label(tool["name"]).classes("font-semibold")
                                ui.label(tool["description"]).classes("text-sm text-gray-600")
                                
                                # Show tool category
                                category = tool.get("category", "unknown")
                                ui.label(f"Category: {category}").classes("text-xs text-gray-500")
                            
                            ui.button("Execute", on_click=lambda t=tool: self.select_tool_for_execution(t)).classes("bg-blue-500 text-white text-xs")
            
        except Exception as e:
            ui.notify(f"Error loading assistant tools: {e}", type="error")
    
    def select_tool_for_execution(self, tool: Dict[str, Any]):
        """Select a tool for execution and show parameter dialog."""
        self.selected_tool = tool
        self.tools_dialog.close()
        self.show_tool_execution_dialog()
    
    def show_tool_execution_dialog(self):
        """Show dialog for tool parameter input and execution."""
        if not self.selected_tool:
            return
        
        with ui.dialog() as self.tool_execution_dialog, ui.card().classes("w-96"):
            ui.label(f"Execute: {self.selected_tool['name']}").classes("text-lg font-semibold mb-4")
            ui.label(self.selected_tool["description"]).classes("text-sm text-gray-600 mb-4")
            
            # Parameter inputs
            self.tool_parameters = {}
            self.parameter_inputs = {}
            
            parameters = self.selected_tool.get("parameters", [])
            if parameters:
                for param in parameters:
                    param_name = param["name"]
                    param_type = param["type"]
                    param_description = param.get("description", "")
                    param_required = param.get("required", False)
                    
                    label_text = f"{param_name}{'*' if param_required else ''}"
                    if param_description:
                        label_text += f" - {param_description}"
                    
                    if param_type == "string":
                        input_field = ui.input(label_text).classes("w-full mb-2")
                    elif param_type == "number":
                        input_field = ui.number(label_text).classes("w-full mb-2")
                    elif param_type == "boolean":
                        input_field = ui.checkbox(label_text).classes("w-full mb-2")
                    else:
                        input_field = ui.input(label_text).classes("w-full mb-2")
                    
                    self.parameter_inputs[param_name] = input_field
            else:
                ui.label("No parameters required").classes("text-gray-500 mb-4")
            
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=self.tool_execution_dialog.close).classes("bg-gray-500")
                ui.button("Execute", on_click=self.execute_selected_tool).classes("bg-blue-500")
    
    async def execute_selected_tool(self):
        """Execute the selected tool with provided parameters."""
        if not self.selected_tool or not self.current_conversation:
            return
        
        try:
            # Collect parameters
            arguments = {}
            for param_name, input_field in self.parameter_inputs.items():
                if hasattr(input_field, 'value'):
                    arguments[param_name] = input_field.value
            
            # Execute tool based on type
            tool_id = self.selected_tool.get("id", self.selected_tool.get("name"))
            tool_category = self.selected_tool.get("category", "unknown")
            
            if tool_category == "mcp":
                # Execute MCP tool
                response = await api_client.execute_mcp_tool(tool_id, arguments)
            else:
                # Execute regular tool
                response = await api_client.execute_tool(tool_id, arguments)
            
            if response.success:
                # Add tool execution as a message
                tool_message = Message(
                    id=f"tool_{datetime.now().timestamp()}",
                    content=response.data,
                    role="assistant",
                    timestamp=datetime.now(),
                    message_type="tool_result",
                    metadata={
                        "tool_name": self.selected_tool["name"],
                        "tool_category": tool_category,
                        "arguments": arguments,
                        "success": True
                    }
                )
                
                self.messages.append(tool_message)
                self.update_messages_display()
                self.tool_execution_dialog.close()
                
                ui.notify("Tool executed successfully", type="positive")
            else:
                ui.notify(f"Tool execution failed: {response.error}", type="error")
                
        except Exception as e:
            ui.notify(f"Error executing tool: {e}", type="error")
    
    async def load_tools(self):
        """Load all available tools (legacy method)."""
        await self.load_assistant_tools()
    
    def use_tool(self, tool: Dict[str, Any]):
        """Use a tool in the current conversation."""
        if not self.current_conversation:
            ui.notify("Please select a conversation first", type="warning")
            return
        
        # In a real implementation, this would open a tool execution dialog
        ui.notify(f"Tool {tool['name']} would be executed here", type="info")
        self.tools_dialog.close()


# Create page instance
chat_page = ChatPage() 