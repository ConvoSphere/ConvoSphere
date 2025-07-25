# User Guide - Using ConvoSphere

## 🎯 Overview

ConvoSphere is a comprehensive AI chat platform with an advanced knowledge base, real-time messaging, powerful AI assistants, and enterprise-grade features. This guide shows you how to use all features effectively.

## 🏠 Dashboard

The Dashboard is your central hub providing:

- **System Overview**: Key statistics and metrics
- **Quick Actions**: Fast access to create new chats, upload documents, or manage assistants
- **Recent Activity**: Latest conversations, uploads, and system activities
- **Performance Metrics**: Real-time system health and usage statistics
- **User Analytics**: Your activity summary and usage patterns

**Navigation**: Access via the home icon in the sidebar or go to `/dashboard`

## 💬 Chat Interface

### Starting Conversations

**Multiple ways to start chatting:**
1. **Dashboard** → "New Chat" or "New Conversation" button
2. **Chat Page** → "+" button in sidebar
3. **Direct Navigation** → Go to `/` (default route)
4. **Sidebar** → Click "Chat" in the navigation menu

### Sending Messages

- **Text Input**: Type in the message input field at the bottom
- **Send**: Press `Enter` to send immediately
- **New Line**: Use `Shift+Enter` for line breaks
- **File Attachments**: Click the paperclip icon to attach files
- **Voice Input**: Use the microphone icon for speech-to-text

### Chat Features

#### **Real-time Features**
- **Instant Delivery**: Messages appear immediately via WebSocket
- **Typing Indicators**: See when AI assistants are responding
- **Status Updates**: Real-time connection and processing status
- **Live Notifications**: Instant alerts for new messages

#### **File Attachments**
**Supported formats:**
- **PDF** (.pdf) - Full text extraction and processing
- **Word Documents** (.docx) - Complete document analysis
- **Text Files** (.txt) - Direct text processing
- **Markdown** (.md) - Formatted text with structure preservation

**Features:**
- **Size Limit**: Up to 50MB per file
- **Drag & Drop**: Simply drag files into the chat
- **Bulk Upload**: Select multiple files at once
- **Processing Status**: Real-time upload and processing feedback

#### **Message Formatting**
- **Markdown Support**: Use *italic*, **bold**, `code`, and more
- **Code Blocks**: Syntax highlighting for programming languages
- **Lists**: Numbered and bullet lists
- **Tables**: Formatted data presentation
- **Links**: Automatic link detection and formatting

#### **Chat Management**
- **Message History**: All conversations automatically saved
- **Search**: Find specific messages or topics
- **Export**: Download conversation history
- **Conversation Threading**: Organized message flows

## 📚 Knowledge Base

### Document Management

#### **Upload Documents**
1. **Navigate**: Go to Knowledge Base page (`/knowledge-base`)
2. **Upload Methods**:
   - **Drag & Drop**: Drop files directly onto the upload area
   - **File Browser**: Click "Upload" to select files
   - **Bulk Import**: Select multiple files simultaneously
3. **Document Metadata**:
   - **Title**: Custom document title
   - **Description**: Document summary or notes
   - **Tags**: Categorization labels
   - **Category**: Document classification
4. **Processing**: Automatic text extraction and chunking

#### **Advanced Upload Features**
- **Bulk Operations**: Upload dozens of files at once
- **Progress Tracking**: Real-time upload and processing status
- **Error Handling**: Clear feedback on failed uploads
- **Duplicate Detection**: Automatic detection of duplicate content
- **Metadata Auto-extraction**: Automatic title and description generation

### Document Organization

#### **Tag Management**
- **Tag Creation**: Create custom tags for organization
- **Tag Clouds**: Visual representation of tag popularity
- **Tag Statistics**: Usage analytics and insights
- **Bulk Tagging**: Apply tags to multiple documents
- **System Tags**: Pre-defined organizational categories

#### **Advanced Search**
- **Semantic Search**: AI-powered content discovery
- **Full-text Search**: Find exact phrases and terms
- **Tag Filtering**: Filter by single or multiple tags
- **Metadata Filters**: Search by author, date, file type
- **Advanced Operators**: Complex search queries
- **Search History**: Previous search results and queries

#### **Document Actions**
- **View**: Preview document content and metadata
- **Edit**: Modify document information and tags
- **Download**: Retrieve original files
- **Delete**: Remove documents (with confirmation)
- **Reprocess**: Re-extract and re-chunk content
- **Share**: Control document access and permissions

### Role-based Access

ConvoSphere implements a comprehensive role-based access system:

| Feature | User | Premium | Moderator | Admin |
|---------|------|---------|-----------|-------|
| Upload documents | ✓ | ✓ | ✓ | ✓ |
| Manage own documents | ✓ | ✓ | ✓ | ✓ |
| Bulk import | ✗ | ✓ | ✓ | ✓ |
| Tag management | ✗ | ✓ | ✓ | ✓ |
| Create system tags | ✗ | ✗ | ✗ | ✓ |
| View all documents | ✗ | ✗ | ✓ | ✓ |
| User management | ✗ | ✗ | ✗ | ✓ |
| System statistics | ✗ | ✗ | ✗ | ✓ |

### AI Integration with Knowledge Base

#### **Context-Aware Responses**
- **Automatic Context**: AI automatically uses relevant documents
- **Manual Selection**: Choose specific documents for context
- **Source Citations**: AI responses include document references
- **Content Summarization**: AI creates summaries of large documents

#### **Smart Document Discovery**
- **Semantic Matching**: AI finds relevant content based on meaning
- **Topic Association**: Related documents suggested automatically
- **Content Ranking**: Most relevant documents prioritized
- **Context Windows**: Optimal content chunks for AI processing

## 🤖 AI Assistants

### Creating Custom Assistants

1. **Navigate**: Go to Assistants page (`/assistants`)
2. **Create Assistant**: Click "Create New Assistant"
3. **Configuration Options**:
   - **Name & Description**: Assistant identity
   - **AI Model Selection**: Choose from available providers
   - **Personality Settings**: Define response style and behavior
   - **Knowledge Base Linking**: Connect to specific documents
   - **Tool Access**: Enable specific tools and capabilities
   - **Response Parameters**: Temperature, max tokens, etc.

### Assistant Management

#### **Available Features**
- **Template Library**: Pre-built assistant templates
- **Custom Personalities**: Define unique response styles
- **Multi-Model Support**: OpenAI, Anthropic, and other providers
- **Performance Tuning**: Adjust response quality and speed
- **Usage Analytics**: Track assistant performance and usage
- **Sharing Options**: Share assistants with other users

#### **Using Assistants**
- **Chat Selection**: Choose assistant from dropdown in chat
- **Direct Mention**: Use `@AssistantName` to invoke specific assistants
- **Default Assistant**: Set your preferred default assistant
- **Context Switching**: Switch assistants mid-conversation
- **Assistant Comparison**: Test multiple assistants simultaneously

## 🔧 Tools & Integrations

### Model Context Protocol (MCP) Tools

Navigate to **Tools** (`/tools`) or **MCP Tools** (`/mcp-tools`) to access:

#### **Available Tool Categories**
- **Search Tools**: Web search, document search, semantic search
- **Calculator**: Mathematical computations and analysis
- **File Processing**: Document analysis, format conversion
- **API Integrations**: External service connections
- **Data Analysis**: Statistical analysis and visualization
- **Custom Tools**: User-defined tool implementations

#### **Tool Management**
- **Tool Discovery**: Browse available tools
- **Installation**: Add new tools to your workspace
- **Configuration**: Set up tool parameters and credentials
- **Execution Tracking**: Monitor tool usage and performance
- **Custom Development**: Create your own tools
- **Performance Metrics**: Tool execution statistics

#### **Using Tools in Chat**
- **Tool Invocation**: AI automatically selects appropriate tools
- **Manual Selection**: Explicitly request specific tools
- **Tool Chaining**: Combine multiple tools for complex tasks
- **Result Integration**: Tool outputs integrated into conversations
- **Error Handling**: Clear feedback on tool execution issues

## 👤 Profile & Settings

### Profile Management (`/profile`)

**Personal Information**:
- **Name & Email**: Update your contact information
- **Avatar**: Upload and manage profile picture
- **Language Preference**: Choose interface language (EN/DE)
- **Timezone**: Set your local timezone
- **Notification Preferences**: Configure alert settings

### Application Settings (`/settings`)

**Interface Customization**:
- **Theme Selection**: Switch between dark and light themes
- **Language**: Change interface language
- **Default Assistant**: Set your preferred AI assistant
- **Chat Preferences**: Configure default chat behavior
- **Performance Settings**: Adjust UI performance options

### Notifications

**Notification Types**:
- **Email Notifications**: Configure email alerts
- **Browser Notifications**: In-app notification settings
- **Mobile Push**: Push notification preferences (if applicable)
- **Frequency Control**: Set notification frequency limits
- **Type Filtering**: Choose which events trigger notifications

## 🔐 Authentication & Security

### Account Management

**Registration** (`/register`):
- **Account Creation**: Create new user account
- **Email Verification**: Verify email address
- **Profile Setup**: Initial profile configuration
- **Role Assignment**: Automatic role assignment

**Login** (`/login`):
- **Standard Login**: Email/password authentication
- **Remember Me**: Persistent login sessions
- **Password Recovery**: Reset forgotten passwords
- **Security Features**: Failed login attempt protection

### Security Features

- **JWT Authentication**: Secure token-based authentication
- **Session Management**: Automatic session timeout and renewal
- **Password Security**: Strong password requirements
- **Two-Factor Authentication**: Enhanced security options (if enabled)
- **Audit Logging**: Track account security events

## 👨‍💼 Admin Features (Admin Only)

### Admin Dashboard (`/admin`)

**System Overview**:
- **User Management**: Create, edit, and manage user accounts
- **Role Assignment**: Assign and modify user roles
- **System Statistics**: Comprehensive usage analytics
- **Performance Monitoring**: Real-time system health metrics
- **Audit Logs**: Security and usage audit trails

### System Monitoring (`/admin/system-status`)

**Real-time Metrics**:
- **System Health**: Server status and performance
- **Database Performance**: Connection and query metrics
- **Memory Usage**: RAM and storage utilization
- **User Activity**: Active users and session statistics
- **Error Tracking**: System errors and resolution status

### Administrative Tools

- **User Analytics**: Detailed user behavior analysis
- **Content Moderation**: Review and manage user content
- **System Configuration**: Adjust global system settings
- **Backup Management**: Data backup and recovery options
- **Integration Management**: External service configurations

## 💬 Conversation Management (`/conversations`)

### Conversation History

**Features**:
- **Complete History**: Access all past conversations
- **Search & Filter**: Find specific conversations
- **Organization**: Sort by date, assistant, or topic
- **Favorites**: Mark important conversations
- **Archives**: Long-term conversation storage

### Conversation Actions

- **Continue**: Resume previous conversations
- **Export**: Download conversation transcripts
- **Share**: Share conversations with other users
- **Duplicate**: Create copies of conversations
- **Delete**: Remove unwanted conversations

## 🎨 User Experience Features

### Theme & Customization

- **Dark/Light Mode**: Toggle between themes
- **System Preference**: Automatic theme based on OS settings
- **Custom Colors**: Personalize interface colors
- **Layout Options**: Adjust sidebar and layout preferences
- **Accessibility**: High contrast and screen reader support

### Performance Features

- **Lazy Loading**: Fast page loading with code splitting
- **Real-time Updates**: Instant UI updates via WebSocket
- **Offline Support**: Limited functionality when offline
- **Mobile Optimization**: Responsive design for all devices
- **Progressive Loading**: Gradual content loading for better UX

### Internationalization

- **Language Support**: Full English and German translations
- **Locale Adaptation**: Date, time, and number formatting
- **Cultural Adaptation**: UI patterns adapted for different cultures
- **Easy Switching**: Instant language switching without reload

## 🆘 Troubleshooting

### Common Issues

**Connection Problems**:
- Check internet connectivity
- Verify WebSocket connection status
- Refresh browser or restart application

**Upload Issues**:
- Verify file size is under 50MB limit
- Check file format is supported
- Ensure sufficient storage space

**Performance Issues**:
- Clear browser cache and cookies
- Close unnecessary browser tabs
- Check system resources (RAM, CPU)

### Getting Help

- **Documentation**: Comprehensive guides and FAQ
- **Support Tickets**: Report issues through the system
- **Community**: Discord server and GitHub discussions
- **Error Messages**: Clear, actionable error descriptions

---

**Ready to get started?** Begin with the [Quick Start Guide](quick-start.md) or explore the [Dashboard](/) to see all features in action!