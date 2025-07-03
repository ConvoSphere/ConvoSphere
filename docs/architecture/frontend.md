# Frontend Architecture

## Overview

The frontend of the AI Assistant Platform is built with Streamlit, providing a modern, interactive web interface with real-time updates, responsive design, and seamless integration with the backend API.

## Technology Stack

### Core Framework
- **Streamlit**: Modern web framework for data applications
- **Streamlit-Extras**: Additional components and utilities
- **Streamlit-Authenticator**: Authentication components
- **Streamlit-Option-Menu**: Navigation menu components

### UI/UX Libraries
- **Custom CSS**: Themed styling and responsive design
- **Streamlit Components**: Custom interactive components
- **Icons**: Material Design and custom icons
- **Animations**: Smooth transitions and loading states

### State Management
- **Session State**: Streamlit's built-in session management
- **Local Storage**: Browser-based persistent storage
- **Cache**: Streamlit caching for performance optimization

### API Integration
- **HTTP Client**: Async HTTP requests to backend
- **WebSocket**: Real-time communication
- **Error Handling**: Comprehensive error management

## Project Structure

```
frontend/
├── __init__.py
├── main.py
├── assets/
│   └── themes.css
├── components/
│   ├── __init__.py
│   ├── accessibility/
│   │   └── accessibility_manager.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_form.py
│   ├── branding/
│   │   └── logo.py
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── chat_input.py
│   │   ├── chat_interface.py
│   │   └── message_bubble.py
│   ├── common/
│   │   ├── error_message.py
│   │   └── loading_spinner.py
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── dashboard_page.py
│   ├── dialogs/
│   ├── forms/
│   ├── header.py
│   ├── knowledge/
│   │   ├── document_card.py
│   │   ├── search_component.py
│   │   └── upload_component.py
│   ├── layout/
│   │   ├── __init__.py
│   │   └── page_layout.py
│   ├── responsive/
│   │   └── responsive_layout.py
│   ├── sidebar.py
│   ├── theme_switcher.py
│   └── user/
│       └── profile_card.py
├── pages/
│   ├── __init__.py
│   ├── admin.py
│   ├── assistants.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── profile.py
│   │   └── register.py
│   ├── chat.py
│   ├── conversations.py
│   ├── dashboard.py
│   ├── knowledge_base.py
│   ├── mcp_tools.py
│   ├── settings.py
│   └── tools.py
├── services/
│   ├── __init__.py
│   ├── api_client.py
│   ├── api.py
│   ├── assistant_service.py
│   ├── auth_service.py
│   ├── conversation_service.py
│   ├── error_handler.py
│   ├── http_client.py
│   ├── knowledge_service.py
│   ├── message_service.py
│   ├── tool_service.py
│   ├── user_service.py
│   └── websocket_service.py
├── static/
│   └── css/
│       └── themes.css
├── utils/
│   ├── __init__.py
│   ├── constants.py
│   ├── design_system.py
│   ├── helpers.py
│   ├── i18n_manager.py
│   ├── performance_manager.py
│   ├── router.py
│   ├── theme_manager.py
│   └── validators.py
├── i18n/
│   ├── de.json
│   └── en.json
├── requirements.txt
└── tests/
    ├── test_components.py
    ├── test_pages.py
    └── test_services.py
```

## Application Entry Point

### Main Application Setup

```python
# main.py
import streamlit as st
from streamlit_authenticator import Authenticate
from streamlit_option_menu import option_menu
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.theme_manager import ThemeManager
from utils.i18n_manager import I18nManager
from utils.performance_manager import PerformanceManager
from services.auth_service import AuthService
from components.header import Header
from components.sidebar import Sidebar
from pages.dashboard import DashboardPage
from pages.chat import ChatPage
from pages.assistants import AssistantsPage
from pages.conversations import ConversationsPage
from pages.knowledge_base import KnowledgeBasePage
from pages.tools import ToolsPage
from pages.settings import SettingsPage

class AIAssistantApp:
    def __init__(self):
        self.theme_manager = ThemeManager()
        self.i18n_manager = I18nManager()
        self.performance_manager = PerformanceManager()
        self.auth_service = AuthService()
        
        # Initialize session state
        self._init_session_state()
        
        # Setup page configuration
        self._setup_page_config()
    
    def _init_session_state(self):
        """Initialize session state variables."""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        
        if 'language' not in st.session_state:
            st.session_state.language = 'en'
    
    def _setup_page_config(self):
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title="AI Assistant Platform",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def run(self):
        """Run the main application."""
        # Apply theme
        self.theme_manager.apply_theme(st.session_state.theme)
        
        # Setup authentication
        if not st.session_state.authenticated:
            self._show_login_page()
            return
        
        # Main application layout
        self._render_main_layout()
    
    def _show_login_page(self):
        """Show login page."""
        from pages.auth.login import LoginPage
        login_page = LoginPage()
        login_page.render()
    
    def _render_main_layout(self):
        """Render main application layout."""
        # Header
        header = Header()
        header.render()
        
        # Sidebar
        sidebar = Sidebar()
        selected_page = sidebar.render()
        
        # Update current page
        if selected_page:
            st.session_state.current_page = selected_page
        
        # Main content area
        self._render_page_content()
    
    def _render_page_content(self):
        """Render page content based on current page."""
        current_page = st.session_state.current_page
        
        if current_page == 'dashboard':
            page = DashboardPage()
        elif current_page == 'chat':
            page = ChatPage()
        elif current_page == 'assistants':
            page = AssistantsPage()
        elif current_page == 'conversations':
            page = ConversationsPage()
        elif current_page == 'knowledge':
            page = KnowledgeBasePage()
        elif current_page == 'tools':
            page = ToolsPage()
        elif current_page == 'settings':
            page = SettingsPage()
        else:
            page = DashboardPage()
        
        page.render()

if __name__ == "__main__":
    app = AIAssistantApp()
    app.run()
```

## Component Architecture

### Base Component Class

```python
# components/base_component.py
import streamlit as st
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseComponent(ABC):
    """Base class for all components."""
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._init_component()
    
    def _init_component(self):
        """Initialize component-specific attributes."""
        pass
    
    @abstractmethod
    def render(self, **kwargs) -> Any:
        """Render the component."""
        pass
    
    def get_styles(self) -> Dict[str, str]:
        """Get component-specific styles."""
        return {}
    
    def apply_styles(self):
        """Apply component styles."""
        styles = self.get_styles()
        if styles:
            css = "\n".join([f"{k}: {v};" for k, v in styles.items()])
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# components/common/loading_spinner.py
class LoadingSpinner(BaseComponent):
    def __init__(self, text: str = "Loading...", **kwargs):
        self.text = text
        super().__init__(**kwargs)
    
    def render(self, **kwargs):
        """Render loading spinner."""
        with st.spinner(self.text):
            # Component content goes here
            pass
    
    def get_styles(self) -> Dict[str, str]:
        return {
            ".stSpinner": "border-color: var(--primary-color);",
            ".stSpinner > div": "border-color: var(--primary-color) transparent transparent transparent;"
        }

# components/common/error_message.py
class ErrorMessage(BaseComponent):
    def __init__(self, message: str, error_type: str = "error", **kwargs):
        self.message = message
        self.error_type = error_type
        super().__init__(**kwargs)
    
    def render(self, **kwargs):
        """Render error message."""
        if self.error_type == "error":
            st.error(self.message)
        elif self.error_type == "warning":
            st.warning(self.message)
        elif self.error_type == "info":
            st.info(self.message)
        else:
            st.error(self.message)
```

### Chat Components

```python
# components/chat/chat_interface.py
import streamlit as st
from typing import List, Dict, Optional
from components.base_component import BaseComponent
from components.chat.message_bubble import MessageBubble
from components.chat.chat_input import ChatInput
from services.conversation_service import ConversationService

class ChatInterface(BaseComponent):
    def __init__(self, conversation_id: Optional[str] = None, **kwargs):
        self.conversation_id = conversation_id
        self.conversation_service = ConversationService()
        super().__init__(**kwargs)
    
    def render(self, **kwargs):
        """Render chat interface."""
        # Chat messages area
        self._render_messages_area()
        
        # Chat input area
        self._render_input_area()
    
    def _render_messages_area(self):
        """Render chat messages area."""
        st.markdown("### Chat Messages")
        
        # Get messages for current conversation
        messages = self._get_messages()
        
        # Render each message
        for message in messages:
            message_bubble = MessageBubble(
                content=message["content"],
                sender=message["sender"],
                timestamp=message["timestamp"],
                message_type=message["type"]
            )
            message_bubble.render()
    
    def _render_input_area(self):
        """Render chat input area."""
        st.markdown("### Send Message")
        
        chat_input = ChatInput(
            placeholder="Type your message here...",
            on_send=self._handle_message_send
        )
        chat_input.render()
    
    def _get_messages(self) -> List[Dict]:
        """Get messages for current conversation."""
        if self.conversation_id:
            return self.conversation_service.get_messages(self.conversation_id)
        return []
    
    def _handle_message_send(self, message: str):
        """Handle message send event."""
        if message.strip():
            # Send message to backend
            response = self.conversation_service.send_message(
                conversation_id=self.conversation_id,
                message=message
            )
            
            # Update conversation
            st.rerun()

# components/chat/message_bubble.py
class MessageBubble(BaseComponent):
    def __init__(self, content: str, sender: str, timestamp: str, 
                 message_type: str = "text", **kwargs):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp
        self.message_type = message_type
        super().__init__(**kwargs)
    
    def render(self, **kwargs):
        """Render message bubble."""
        # Determine alignment based on sender
        is_user = self.sender == "user"
        alignment = "right" if is_user else "left"
        
        # Create message container
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            
            if alignment == "right":
                with col2:
                    self._render_message_content()
                with col3:
                    self._render_timestamp()
            else:
                with col1:
                    self._render_avatar()
                with col2:
                    self._render_message_content()
                with col3:
                    self._render_timestamp()
    
    def _render_message_content(self):
        """Render message content."""
        # Apply message styling
        css_class = "user-message" if self.sender == "user" else "assistant-message"
        
        st.markdown(
            f"""
            <div class="{css_class}">
                <div class="message-content">
                    {self.content}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _render_timestamp(self):
        """Render message timestamp."""
        st.caption(self.timestamp)
    
    def _render_avatar(self):
        """Render sender avatar."""
        if self.sender == "assistant":
            st.image("assets/assistant_avatar.png", width=40)
        else:
            st.image("assets/user_avatar.png", width=40)
    
    def get_styles(self) -> Dict[str, str]:
        return {
            ".user-message": """
                background-color: var(--primary-color);
                color: white;
                border-radius: 15px 15px 0 15px;
                padding: 10px 15px;
                margin: 5px 0;
                text-align: right;
            """,
            ".assistant-message": """
                background-color: var(--secondary-bg);
                color: var(--text-color);
                border-radius: 15px 15px 15px 0;
                padding: 10px 15px;
                margin: 5px 0;
                text-align: left;
            """,
            ".message-content": """
                word-wrap: break-word;
                white-space: pre-wrap;
            """
        }

# components/chat/chat_input.py
class ChatInput(BaseComponent):
    def __init__(self, placeholder: str = "Type your message...", 
                 on_send=None, **kwargs):
        self.placeholder = placeholder
        self.on_send = on_send
        super().__init__(**kwargs)
    
    def render(self, **kwargs):
        """Render chat input."""
        with st.container():
            # Text input
            message = st.text_area(
                label="Message",
                placeholder=self.placeholder,
                key="chat_input",
                height=100
            )
            
            # Send button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Send", key="send_button"):
                    if message.strip() and self.on_send:
                        self.on_send(message.strip())
                        # Clear input
                        st.session_state.chat_input = ""
                        st.rerun()
```

### Layout Components

```python
# components/layout/page_layout.py
import streamlit as st
from components.base_component import BaseComponent

class PageLayout(BaseComponent):
    def __init__(self, title: str, show_sidebar: bool = True, **kwargs):
        self.title = title
        self.show_sidebar = show_sidebar
        super().__init__(**kwargs)
    
    def render(self, content_func=None, **kwargs):
        """Render page layout."""
        # Page title
        st.title(self.title)
        
        # Main content area
        if self.show_sidebar:
            # Two-column layout with sidebar
            sidebar_col, main_col = st.columns([1, 4])
            
            with sidebar_col:
                self._render_sidebar()
            
            with main_col:
                if content_func:
                    content_func()
        else:
            # Full-width layout
            if content_func:
                content_func()
    
    def _render_sidebar(self):
        """Render sidebar content."""
        st.sidebar.title("Navigation")
        
        # Add sidebar content here
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Quick Actions")
        
        if st.sidebar.button("New Chat"):
            st.session_state.current_page = "chat"
            st.rerun()
        
        if st.sidebar.button("Settings"):
            st.session_state.current_page = "settings"
            st.rerun()

# components/responsive/responsive_layout.py
class ResponsiveLayout(BaseComponent):
    def __init__(self, breakpoint: str = "md", **kwargs):
        self.breakpoint = breakpoint
        super().__init__(**kwargs)
    
    def render(self, desktop_content=None, mobile_content=None, **kwargs):
        """Render responsive layout."""
        # Detect screen size (simplified)
        screen_width = st.get_option("server.maxUploadSize")
        
        if screen_width and screen_width > 768:  # Desktop
            if desktop_content:
                desktop_content()
        else:  # Mobile
            if mobile_content:
                mobile_content()
    
    def get_styles(self) -> Dict[str, str]:
        return {
            "@media (max-width: 768px)": """
                .main-content {
                    padding: 10px;
                }
                .sidebar {
                    display: none;
                }
            """,
            "@media (min-width: 769px)": """
                .main-content {
                    padding: 20px;
                }
            """
        }
```

## Service Layer

### API Client

```python
# services/api_client.py
import requests
import streamlit as st
from typing import Dict, Any, Optional
from services.error_handler import ErrorHandler

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.error_handler = ErrorHandler()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authentication token if available
        if 'auth_token' in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
        
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self.error_handler.handle_error(e)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self.error_handler.handle_error(e)
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.put(
                url,
                headers=self._get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self.error_handler.handle_error(e)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.delete(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self.error_handler.handle_error(e)

# services/auth_service.py
from services.api_client import APIClient
from typing import Optional, Dict, Any

class AuthService:
    def __init__(self):
        self.api_client = APIClient()
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user."""
        data = {
            "email": email,
            "password": password
        }
        
        response = self.api_client.post("/api/v1/auth/login", data)
        
        if response.get("success"):
            # Store token in session state
            st.session_state.auth_token = response["access_token"]
            st.session_state.authenticated = True
            st.session_state.current_user = response["user"]
        
        return response
    
    def register(self, email: str, name: str, password: str) -> Dict[str, Any]:
        """Register new user."""
        data = {
            "email": email,
            "name": name,
            "password": password
        }
        
        response = self.api_client.post("/api/v1/auth/register", data)
        
        if response.get("success"):
            # Auto-login after registration
            return self.login(email, password)
        
        return response
    
    def logout(self):
        """Logout user."""
        # Clear session state
        if 'auth_token' in st.session_state:
            del st.session_state.auth_token
        st.session_state.authenticated = False
        st.session_state.current_user = None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user information."""
        if not st.session_state.authenticated:
            return None
        
        response = self.api_client.get("/api/v1/users/me")
        return response.get("user") if response.get("success") else None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return st.session_state.authenticated

# services/conversation_service.py
from services.api_client import APIClient
from typing import List, Dict, Any, Optional

class ConversationService:
    def __init__(self):
        self.api_client = APIClient()
    
    def get_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user conversations."""
        response = self.api_client.get(f"/api/v1/conversations?limit={limit}")
        return response.get("conversations", []) if response.get("success") else []
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get specific conversation."""
        response = self.api_client.get(f"/api/v1/conversations/{conversation_id}")
        return response.get("conversation") if response.get("success") else None
    
    def create_conversation(self, assistant_id: str, title: str = None) -> Dict[str, Any]:
        """Create new conversation."""
        data = {
            "assistant_id": assistant_id
        }
        if title:
            data["title"] = title
        
        response = self.api_client.post("/api/v1/conversations", data)
        return response
    
    def send_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Send message to conversation."""
        data = {
            "content": message,
            "type": "user"
        }
        
        response = self.api_client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data
        )
        return response
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages for conversation."""
        response = self.api_client.get(f"/api/v1/conversations/{conversation_id}/messages")
        return response.get("messages", []) if response.get("success") else []
    
    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Delete conversation."""
        response = self.api_client.delete(f"/api/v1/conversations/{conversation_id}")
        return response
```

## Page Architecture

### Base Page Class

```python
# pages/base_page.py
import streamlit as st
from abc import ABC, abstractmethod
from components.layout.page_layout import PageLayout
from services.error_handler import ErrorHandler

class BasePage(ABC):
    """Base class for all pages."""
    
    def __init__(self, title: str, show_sidebar: bool = True):
        self.title = title
        self.show_sidebar = show_sidebar
        self.layout = PageLayout(title, show_sidebar)
        self.error_handler = ErrorHandler()
    
    def render(self):
        """Render the page."""
        try:
            self.layout.render(content_func=self._render_content)
        except Exception as e:
            self.error_handler.handle_error(e)
    
    @abstractmethod
    def _render_content(self):
        """Render page content (to be implemented by subclasses)."""
        pass
    
    def _show_loading(self, text: str = "Loading..."):
        """Show loading state."""
        with st.spinner(text):
            pass
    
    def _show_error(self, message: str):
        """Show error message."""
        st.error(message)
    
    def _show_success(self, message: str):
        """Show success message."""
        st.success(message)

# pages/chat.py
from pages.base_page import BasePage
from components.chat.chat_interface import ChatInterface
from services.conversation_service import ConversationService
from services.assistant_service import AssistantService

class ChatPage(BasePage):
    def __init__(self):
        super().__init__("Chat", show_sidebar=True)
        self.conversation_service = ConversationService()
        self.assistant_service = AssistantService()
    
    def _render_content(self):
        """Render chat page content."""
        # Assistant selection
        self._render_assistant_selection()
        
        # Conversation selection
        self._render_conversation_selection()
        
        # Chat interface
        self._render_chat_interface()
    
    def _render_assistant_selection(self):
        """Render assistant selection."""
        st.markdown("### Select Assistant")
        
        # Get available assistants
        assistants = self.assistant_service.get_assistants()
        
        if assistants:
            assistant_names = [assistant["name"] for assistant in assistants]
            selected_assistant = st.selectbox(
                "Choose an assistant:",
                assistant_names,
                key="selected_assistant"
            )
            
            # Store selected assistant
            if selected_assistant:
                st.session_state.selected_assistant = selected_assistant
        else:
            st.warning("No assistants available.")
    
    def _render_conversation_selection(self):
        """Render conversation selection."""
        st.markdown("### Conversations")
        
        # Get user conversations
        conversations = self.conversation_service.get_conversations()
        
        if conversations:
            # Show existing conversations
            for conversation in conversations:
                if st.button(
                    f"{conversation['title']} ({conversation['created_at']})",
                    key=f"conv_{conversation['id']}"
                ):
                    st.session_state.current_conversation = conversation['id']
                    st.rerun()
        
        # New conversation button
        if st.button("New Conversation"):
            if 'selected_assistant' in st.session_state:
                # Create new conversation
                response = self.conversation_service.create_conversation(
                    assistant_id=st.session_state.selected_assistant
                )
                if response.get("success"):
                    st.session_state.current_conversation = response["conversation"]["id"]
                    st.rerun()
            else:
                st.warning("Please select an assistant first.")
    
    def _render_chat_interface(self):
        """Render chat interface."""
        if 'current_conversation' in st.session_state:
            chat_interface = ChatInterface(
                conversation_id=st.session_state.current_conversation
            )
            chat_interface.render()
        else:
            st.info("Please select or create a conversation to start chatting.")

# pages/dashboard.py
from pages.base_page import BasePage
from components.dashboard.dashboard_page import DashboardComponent
from services.user_service import UserService

class DashboardPage(BasePage):
    def __init__(self):
        super().__init__("Dashboard", show_sidebar=True)
        self.user_service = UserService()
    
    def _render_content(self):
        """Render dashboard content."""
        # Welcome message
        self._render_welcome_message()
        
        # Quick stats
        self._render_quick_stats()
        
        # Recent activity
        self._render_recent_activity()
        
        # Quick actions
        self._render_quick_actions()
    
    def _render_welcome_message(self):
        """Render welcome message."""
        user = st.session_state.current_user
        if user:
            st.markdown(f"## Welcome back, {user['name']}! 👋")
            st.markdown("Here's what's happening with your AI assistants today.")
    
    def _render_quick_stats(self):
        """Render quick statistics."""
        st.markdown("### Quick Stats")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Conversations", "24")
        
        with col2:
            st.metric("Active Assistants", "3")
        
        with col3:
            st.metric("Messages Today", "156")
        
        with col4:
            st.metric("Knowledge Items", "42")
    
    def _render_recent_activity(self):
        """Render recent activity."""
        st.markdown("### Recent Activity")
        
        # Placeholder for recent activity
        activities = [
            {"type": "conversation", "title": "New chat with GPT-4", "time": "2 minutes ago"},
            {"type": "assistant", "title": "Updated Assistant settings", "time": "1 hour ago"},
            {"type": "knowledge", "title": "Uploaded new document", "time": "3 hours ago"}
        ]
        
        for activity in activities:
            st.markdown(f"**{activity['title']}** - {activity['time']}")
    
    def _render_quick_actions(self):
        """Render quick actions."""
        st.markdown("### Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start New Chat", key="new_chat_btn"):
                st.session_state.current_page = "chat"
                st.rerun()
            
            if st.button("Manage Assistants", key="assistants_btn"):
                st.session_state.current_page = "assistants"
                st.rerun()
        
        with col2:
            if st.button("Upload Knowledge", key="knowledge_btn"):
                st.session_state.current_page = "knowledge"
                st.rerun()
            
            if st.button("View Conversations", key="conversations_btn"):
                st.session_state.current_page = "conversations"
                st.rerun()
```

## State Management

### Session State Management

```python
# utils/state_manager.py
import streamlit as st
from typing import Any, Optional

class StateManager:
    """Manages application state using Streamlit session state."""
    
    @staticmethod
    def set(key: str, value: Any):
        """Set a value in session state."""
        st.session_state[key] = value
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get a value from session state."""
        return st.session_state.get(key, default)
    
    @staticmethod
    def delete(key: str):
        """Delete a value from session state."""
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def clear():
        """Clear all session state."""
        st.session_state.clear()
    
    @staticmethod
    def has_key(key: str) -> bool:
        """Check if key exists in session state."""
        return key in st.session_state
    
    @staticmethod
    def get_user() -> Optional[dict]:
        """Get current user from session state."""
        return st.session_state.get('current_user')
    
    @staticmethod
    def set_user(user: dict):
        """Set current user in session state."""
        st.session_state['current_user'] = user
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def set_authenticated(authenticated: bool):
        """Set authentication status."""
        st.session_state['authenticated'] = authenticated

# utils/cache_manager.py
import streamlit as st
from typing import Any, Optional, Callable
import time

class CacheManager:
    """Manages caching for performance optimization."""
    
    @staticmethod
    def cache_data(ttl_seconds: int = 300):
        """Decorator for caching data with TTL."""
        def decorator(func: Callable) -> Callable:
            @st.cache_data(ttl=ttl_seconds)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def cache_resource(ttl_seconds: int = 300):
        """Decorator for caching resources with TTL."""
        def decorator(func: Callable) -> Callable:
            @st.cache_resource(ttl=ttl_seconds)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def clear_cache():
        """Clear all cached data."""
        st.cache_data.clear()
        st.cache_resource.clear()

# Example usage
@CacheManager.cache_data(ttl_seconds=600)
def get_user_conversations(user_id: str):
    """Get user conversations with caching."""
    # This will be cached for 10 minutes
    conversation_service = ConversationService()
    return conversation_service.get_conversations()
```

## Theme and Styling

### Theme Manager

```python
# utils/theme_manager.py
import streamlit as st
from typing import Dict, Any

class ThemeManager:
    """Manages application themes and styling."""
    
    def __init__(self):
        self.themes = {
            'light': self._get_light_theme(),
            'dark': self._get_dark_theme(),
            'blue': self._get_blue_theme()
        }
    
    def apply_theme(self, theme_name: str):
        """Apply theme to the application."""
        if theme_name in self.themes:
            theme = self.themes[theme_name]
            self._inject_css(theme)
    
    def _get_light_theme(self) -> Dict[str, str]:
        """Get light theme configuration."""
        return {
            '--primary-color': '#1f77b4',
            '--secondary-color': '#ff7f0e',
            '--background-color': '#ffffff',
            '--secondary-bg': '#f0f2f6',
            '--text-color': '#262730',
            '--border-color': '#e0e0e0'
        }
    
    def _get_dark_theme(self) -> Dict[str, str]:
        """Get dark theme configuration."""
        return {
            '--primary-color': '#4CAF50',
            '--secondary-color': '#FF9800',
            '--background-color': '#0e1117',
            '--secondary-bg': '#262730',
            '--text-color': '#fafafa',
            '--border-color': '#4a4a4a'
        }
    
    def _get_blue_theme(self) -> Dict[str, str]:
        """Get blue theme configuration."""
        return {
            '--primary-color': '#2196F3',
            '--secondary-color': '#FFC107',
            '--background-color': '#f5f5f5',
            '--secondary-bg': '#e3f2fd',
            '--text-color': '#1976d2',
            '--border-color': '#bbdefb'
        }
    
    def _inject_css(self, theme: Dict[str, str]):
        """Inject CSS variables into the page."""
        css_vars = "\n".join([f"{k}: {v};" for k, v in theme.items()])
        
        css = f"""
        <style>
        :root {{
            {css_vars}
        }}
        
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}
        
        .stButton > button {{
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
        }}
        
        .stButton > button:hover {{
            background-color: var(--secondary-color);
        }}
        
        .stTextInput > div > div > input {{
            background-color: var(--secondary-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }}
        
        .stSelectbox > div > div > select {{
            background-color: var(--secondary-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)

# components/theme_switcher.py
class ThemeSwitcher(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def render(self, **kwargs):
        """Render theme switcher."""
        st.sidebar.markdown("### Theme")
        
        current_theme = st.session_state.get('theme', 'light')
        new_theme = st.sidebar.selectbox(
            "Choose theme:",
            ['light', 'dark', 'blue'],
            index=['light', 'dark', 'blue'].index(current_theme)
        )
        
        if new_theme != current_theme:
            st.session_state.theme = new_theme
            st.rerun()
```

## Error Handling

### Error Handler

```python
# services/error_handler.py
import streamlit as st
from typing import Dict, Any
import traceback

class ErrorHandler:
    """Handles application errors gracefully."""
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle and display error."""
        error_message = str(error)
        error_type = type(error).__name__
        
        # Log error
        self._log_error(error, error_type)
        
        # Display user-friendly error message
        self._display_error(error_message, error_type)
        
        return {
            "success": False,
            "error": error_message,
            "error_type": error_type
        }
    
    def _log_error(self, error: Exception, error_type: str):
        """Log error for debugging."""
        st.error(f"Error ({error_type}): {str(error)}")
        
        # Show detailed error in development
        if st.get_option("server.headless"):
            st.code(traceback.format_exc())
    
    def _display_error(self, message: str, error_type: str):
        """Display user-friendly error message."""
        if "Connection" in error_type:
            st.error("Unable to connect to the server. Please check your internet connection.")
        elif "Authentication" in error_type:
            st.error("Authentication failed. Please log in again.")
        elif "Validation" in error_type:
            st.error(f"Invalid input: {message}")
        elif "Permission" in error_type:
            st.error("You don't have permission to perform this action.")
        else:
            st.error(f"An error occurred: {message}")
    
    def handle_api_error(self, response: Dict[str, Any]) -> bool:
        """Handle API response errors."""
        if not response.get("success", True):
            error_message = response.get("detail", "Unknown error occurred")
            st.error(error_message)
            return False
        return True
```

## Performance Optimization

### Performance Manager

```python
# utils/performance_manager.py
import streamlit as st
import time
from typing import Callable, Any
from functools import wraps

class PerformanceManager:
    """Manages application performance and optimization."""
    
    @staticmethod
    def measure_time(func: Callable) -> Callable:
        """Decorator to measure function execution time."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            if execution_time > 1.0:  # Log slow operations
                st.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
            
            return result
        return wrapper
    
    @staticmethod
    def lazy_load(condition: Callable[[], bool]):
        """Decorator for lazy loading components."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if condition():
                    return func(*args, **kwargs)
                else:
                    st.info("Loading...")
                    return None
            return wrapper
        return decorator
    
    @staticmethod
    def optimize_rendering(func: Callable) -> Callable:
        """Decorator to optimize component rendering."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Use container to prevent unnecessary re-renders
            with st.container():
                return func(*args, **kwargs)
        return wrapper

# Example usage
@PerformanceManager.measure_time
def load_user_data(user_id: str):
    """Load user data with performance monitoring."""
    # Simulate API call
    time.sleep(0.5)
    return {"user_id": user_id, "name": "John Doe"}

@PerformanceManager.lazy_load(lambda: st.session_state.get('authenticated', False))
def render_user_dashboard():
    """Render user dashboard only when authenticated."""
    st.title("User Dashboard")
    # Dashboard content
```

## Internationalization

### I18n Manager

```python
# utils/i18n_manager.py
import json
import os
from typing import Dict, Any

class I18nManager:
    """Manages internationalization and translations."""
    
    def __init__(self, default_language: str = "en"):
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files."""
        i18n_dir = os.path.join(os.path.dirname(__file__), "..", "i18n")
        
        for filename in os.listdir(i18n_dir):
            if filename.endswith(".json"):
                language = filename.replace(".json", "")
                filepath = os.path.join(i18n_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.translations[language] = json.load(f)
    
    def set_language(self, language: str):
        """Set current language."""
        if language in self.translations:
            self.current_language = language
    
    def get_text(self, key: str, **kwargs) -> str:
        """Get translated text."""
        translation = self.translations.get(
            self.current_language,
            self.translations.get(self.default_language, {})
        )
        
        text = translation.get(key, key)
        
        # Replace placeholders
        for k, v in kwargs.items():
            text = text.replace(f"{{{k}}}", str(v))
        
        return text
    
    def get_available_languages(self) -> list:
        """Get list of available languages."""
        return list(self.translations.keys())

# Example usage
i18n = I18nManager()

# In components
welcome_message = i18n.get_text("welcome_message", name="John")
st.markdown(welcome_message)
```

This frontend architecture provides a comprehensive foundation for the AI Assistant Platform with proper component organization, state management, and performance optimization. 