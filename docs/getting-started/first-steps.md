# First Steps

Welcome to the AI Chat Application! This guide will help you get started with your first conversation and explore the key features of the platform.

## Quick Start Checklist

Before you begin, ensure you have:

- ✅ [Installed the application](installation.md)
- ✅ [Configured your environment](configuration.md)
- ✅ Started the backend and frontend services
- ✅ Set up your AI provider API keys

## Accessing the Application

### Web Interface

1. Open your web browser
2. Navigate to `http://localhost:3000` (or your configured frontend URL)
3. You should see the AI Chat Application login page

### API Access

If you prefer to use the API directly:

```bash
# Test the API health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Creating Your First Account

### Option 1: Web Interface Registration

1. Click "Sign Up" on the login page
2. Fill in your details:
   - **Email**: Your email address
   - **Password**: A strong password (minimum 8 characters)
   - **Name**: Your full name
3. Click "Create Account"
4. Verify your email (if email verification is enabled)

### Option 2: API Registration

```bash
# Register a new user via API
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-secure-password",
    "full_name": "Your Full Name"
  }'

# Expected response:
{
  "id": "user-uuid",
  "email": "your-email@example.com",
  "full_name": "Your Full Name",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Logging In

### Web Interface Login

1. Enter your email and password
2. Click "Sign In"
3. You'll be redirected to the main chat interface

### API Login

```bash
# Login via API
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-secure-password"
  }'

# Save the access token for future requests
export ACCESS_TOKEN="your-access-token-here"
```

## Starting Your First Conversation

### Using the Web Interface

1. **Create a New Conversation**:
   - Click the "New Chat" button
   - Choose a conversation type (General, Code, Analysis, etc.)

2. **Send Your First Message**:
   - Type your message in the input field
   - Press Enter or click the send button
   - Wait for the AI response

3. **Example First Messages**:
   - "Hello! Can you help me with a coding problem?"
   - "I need help understanding machine learning concepts"
   - "Can you analyze this data for me?"

### Using the API

```bash
# Create a new conversation
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Conversation",
    "type": "general"
  }'

# Send your first message
curl -X POST "http://localhost:8000/api/v1/conversations/{conversation_id}/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello! Can you help me get started?",
    "role": "user"
  }'
```

## Exploring Key Features

### 1. Chat Interface

The main chat interface includes:

- **Message History**: View all messages in the conversation
- **Real-time Responses**: See AI responses as they're generated
- **Message Actions**: Edit, delete, or copy messages
- **Conversation Management**: Rename, archive, or delete conversations

### 2. File Upload

Upload documents to enhance your conversations:

1. Click the file upload button (📎)
2. Select a supported file type:
   - **Documents**: PDF, DOC, DOCX
   - **Text**: TXT, MD
   - **Data**: CSV, JSON
3. The AI will process and reference the file content

```bash
# Upload a file via API
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@/path/to/your/document.pdf"
```

### 3. Knowledge Base

Create and manage your knowledge base:

1. **Add Documents**: Upload files to your knowledge base
2. **Organize**: Create collections and tags
3. **Search**: Find relevant information quickly
4. **Reference**: AI will use your knowledge base for responses

### 4. Settings and Preferences

Customize your experience:

1. **Profile Settings**: Update your name, email, and password
2. **AI Preferences**: Choose default models and settings
3. **Interface**: Customize theme and layout
4. **Notifications**: Configure email and in-app notifications

## Understanding AI Responses

### Response Types

The AI can provide different types of responses:

- **Text Responses**: Standard conversational responses
- **Code Blocks**: Formatted code with syntax highlighting
- **Tables**: Structured data in table format
- **Lists**: Bulleted or numbered lists
- **Links**: Relevant references and resources

### Response Quality

To get better responses:

1. **Be Specific**: Provide clear, detailed questions
2. **Use Context**: Reference previous messages or uploaded files
3. **Iterate**: Ask follow-up questions to refine responses
4. **Provide Examples**: Show what you're looking for

## Troubleshooting Common Issues

### Login Problems

```bash
# Check if the backend is running
curl http://localhost:8000/health

# Verify your credentials
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email", "password": "your-password"}'
```

### Connection Issues

1. **Backend Not Responding**:
   - Check if the backend service is running
   - Verify the port configuration
   - Check logs for error messages

2. **Frontend Not Loading**:
   - Ensure the frontend service is running
   - Check browser console for errors
   - Verify CORS configuration

### AI Response Issues

1. **No Response**:
   - Check your AI provider API key
   - Verify API quotas and limits
   - Check network connectivity

2. **Poor Quality Responses**:
   - Try rephrasing your question
   - Provide more context
   - Use a different AI model

## Next Steps

Now that you've completed your first steps:

1. **Explore Advanced Features**:
   - [File Management](user-guide/file-management.md)
   - [Knowledge Base](features/knowledge-base.md)
   - [API Integration](api/overview.md)

2. **Learn Best Practices**:
   - [Effective Prompting](user-guide/chat-interface.md)
   - [Security Guidelines](architecture/security.md)
   - [Performance Tips](features/performance.md)

3. **Customize Your Setup**:
   - [User Settings](user-guide/settings.md)
   - [AI Provider Configuration](configuration.md)
   - [Advanced Configuration](deployment/production.md)

4. **Get Help**:
   - [Troubleshooting Guide](user-guide/troubleshooting.md)
   - [FAQ](user-guide/faq.md)
   - [Community Support](project/contributing.md)

## Example Workflows

### Workflow 1: Code Review

1. Upload your code file
2. Ask: "Can you review this code for best practices?"
3. Follow up: "What specific improvements would you suggest?"
4. Ask: "Can you show me how to implement these changes?"

### Workflow 2: Data Analysis

1. Upload your CSV data file
2. Ask: "What insights can you find in this data?"
3. Request: "Create a summary table of the key metrics"
4. Follow up: "What trends do you notice over time?"

### Workflow 3: Learning New Concepts

1. Start with: "I want to learn about machine learning"
2. Ask: "Can you explain the basic concepts?"
3. Request: "Show me some practical examples"
4. Follow up: "What resources would you recommend?"

## Getting Help

If you encounter any issues:

1. **Check the Documentation**: Browse the [User Guide](user-guide/) section
2. **Review Logs**: Check application logs for error messages
3. **Community Support**: Join our [Discord server](https://discord.gg/your-server)
4. **Report Issues**: Open an issue on [GitHub](https://github.com/your-org/ai-chat-app/issues)

## Congratulations! 🎉

You've successfully completed your first steps with the AI Chat Application. You now have:

- ✅ A working account
- ✅ Your first conversation
- ✅ Understanding of key features
- ✅ Knowledge of how to get help

Ready to explore more? Check out the [User Guide](user-guide/) for detailed information about all features and capabilities.