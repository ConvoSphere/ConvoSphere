# Enhanced Chat Features

ConvoSphere provides advanced chat capabilities that go beyond basic messaging, including message search, conversation export, context management, emoji reactions, and dynamic assistant switching.

## Overview

The Enhanced Chat Features provide users with powerful tools to manage, search, and interact with their conversations more effectively. These features are designed to improve productivity and user experience in AI-assisted conversations.

## Message Search

### Overview
Search functionality allows users to quickly find specific messages within conversations using text queries and advanced filters.

### Features
- **Text Search:** Search message content using keywords and phrases
- **Advanced Filters:** Filter by role (user/assistant), message type, and date range
- **Real-time Results:** Instant search results with pagination
- **Highlighted Matches:** Search terms are highlighted in results

### API Endpoint
```
POST /api/v1/conversations/{conversation_id}/messages/search
```

### Request Example
```json
{
  "query": "weather forecast",
  "filters": {
    "role": "assistant",
    "message_type": "text",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z"
  },
  "limit": 50,
  "offset": 0
}
```

### Response Example
```json
{
  "messages": [
    {
      "id": "uuid",
      "content": "The weather forecast shows sunny skies...",
      "role": "assistant",
      "message_type": "text",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "query": "weather forecast"
}
```

### Frontend Integration
The search feature is integrated into the chat interface with:
- Search bar in the chat header
- Real-time search results
- Clear search functionality
- Search result highlighting

## Conversation Export

### Overview
Export conversations in multiple formats for documentation, sharing, or backup purposes.

### Supported Formats
- **JSON:** Complete conversation data with metadata
- **Markdown:** Formatted markdown with emojis and structure
- **TXT:** Plain text format for simple sharing
- **PDF:** Professional PDF format (requires additional setup)

### API Endpoint
```
POST /api/v1/conversations/{conversation_id}/export
```

### Request Example
```json
{
  "format": "markdown",
  "include_metadata": true,
  "include_attachments": true
}
```

### Response Example
```json
{
  "download_url": "/api/v1/conversations/uuid/export/download/conversation_uuid_20240101_120000.md",
  "filename": "conversation_uuid_20240101_120000.md",
  "size": 2048,
  "expires_at": "2024-01-02T00:00:00Z"
}
```

### Export Formats

#### JSON Format
```json
{
  "conversation": {
    "id": "uuid",
    "title": "Weather Discussion",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "messages": [
    {
      "role": "user",
      "content": "What's the weather like?",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "export_info": {
    "format": "json",
    "exported_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Markdown Format
```markdown
# Weather Discussion

**Created:** 2024-01-01T00:00:00Z
**Assistant:** Weather Assistant

---

## 👤 User

What's the weather like?

---

## 🤖 Assistant

The current weather shows sunny skies with a temperature of 22°C.

---
```

#### TXT Format
```
Conversation: Weather Discussion
Created: 2024-01-01T00:00:00Z
Assistant: Weather Assistant

==================================================

[USER]
What's the weather like?

[ASSISTANT]
The current weather shows sunny skies with a temperature of 22°C.
```

### Frontend Integration
The export feature provides:
- Export dropdown in chat header
- Format selection (JSON, Markdown, TXT, PDF)
- Download link after export
- Export progress indication

## Context Management

### Overview
Context management allows users to control and customize the conversation context, including relevant documents, assistant settings, and user preferences.

### Features
- **Context Window Control:** Adjust the number of messages used for context
- **Relevant Documents:** Link specific documents to the conversation
- **Assistant Context:** Customize assistant behavior and settings
- **User Preferences:** Store user-specific preferences

### API Endpoints

#### Get Context
```
GET /api/v1/conversations/{conversation_id}/context
```

#### Update Context
```
PUT /api/v1/conversations/{conversation_id}/context
```

### Context Structure
```json
{
  "conversation_id": "uuid",
  "context_window": 50,
  "relevant_documents": [
    "document-uuid-1",
    "document-uuid-2"
  ],
  "assistant_context": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "system_prompt": "You are a helpful assistant..."
  },
  "user_preferences": {
    "language": "en",
    "style": "formal",
    "response_length": "detailed"
  }
}
```

### Frontend Integration
The context management feature includes:
- Collapsible context section in chat header
- Context window size display
- Relevant documents list
- Editable user preferences as JSON
- Real-time context updates

## Emoji Reactions

### Overview
Emoji reactions allow users to quickly respond to messages with emotional feedback, making conversations more interactive and engaging.

### Features
- **Common Emojis:** Quick access to frequently used reactions
- **Reaction Counts:** Display number of each reaction type
- **User-specific Reactions:** Users can add/remove their own reactions
- **Real-time Updates:** Reactions update instantly across all connected clients

### API Endpoints

#### Add Reaction
```
POST /api/v1/conversations/{conversation_id}/messages/{message_id}/reactions
```

#### Remove Reaction
```
DELETE /api/v1/conversations/{conversation_id}/messages/{message_id}/reactions/{reaction_id}
```

### Request Examples

#### Add Reaction
```json
{
  "emoji": "👍"
}
```

#### Reaction Response
```json
{
  "id": "uuid",
  "emoji": "👍",
  "message_id": "uuid",
  "user_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Frontend Integration
The emoji reactions feature includes:
- Reaction display under each message
- Reaction counts for each emoji
- Emoji picker with common reactions
- Add/remove reaction functionality
- Hover effects and animations

### Common Emojis
The system provides quick access to these common reactions:
- 👍 (thumbs up)
- ❤️ (heart)
- 😂 (laughing)
- 😮 (surprised)
- 😢 (sad)
- 👏 (clapping)
- 🔥 (fire)
- 💯 (100)

## Assistant Switching

### Overview
Assistant switching allows users to dynamically change the AI assistant during a conversation, either preserving or clearing the conversation context.

### Features
- **Dynamic Switching:** Change assistants without starting a new conversation
- **Context Preservation:** Option to keep or clear conversation history
- **Assistant Information:** Display current assistant details
- **Seamless Transition:** Smooth handoff between assistants

### API Endpoints

#### Switch Assistant
```
POST /api/v1/conversations/{conversation_id}/switch-assistant
```

#### Get Current Assistant
```
GET /api/v1/conversations/{conversation_id}/assistant
```

### Request Example
```json
{
  "assistant_id": "new-assistant-uuid",
  "preserve_context": true
}
```

### Response Example
```json
{
  "conversation_id": "uuid",
  "old_assistant_id": "old-assistant-uuid",
  "new_assistant_id": "new-assistant-uuid",
  "assistant_name": "Code Assistant",
  "context_preserved": true,
  "message": "Switched to Code Assistant"
}
```

### Assistant Information
```json
{
  "assistant_id": "uuid",
  "assistant_name": "Code Assistant",
  "assistant_description": "Specialized in programming and code review",
  "assistant_avatar": "https://example.com/avatar.png",
  "assistant_capabilities": ["chat", "rag", "tools", "code_review"]
}
```

### Frontend Integration
The assistant switching feature includes:
- Assistant dropdown in chat header
- Current assistant display
- Switch confirmation dialog
- Context preservation options
- Assistant information panel

### Use Cases
1. **Specialized Assistance:** Switch to a coding assistant for programming questions
2. **Language Support:** Switch to a language-specific assistant
3. **Domain Expertise:** Switch to assistants with specific knowledge areas
4. **Fresh Start:** Clear context and start with a new assistant

## Message Deletion

### Overview
Message deletion allows users to remove their own messages from conversations, providing control over conversation content.

### Features
- **User Messages Only:** Users can only delete their own messages
- **Confirmation Dialog:** Safety confirmation before deletion
- **Real-time Updates:** Messages disappear instantly for all users
- **Audit Trail:** Deletion events are logged for moderation

### API Endpoint
```
DELETE /api/v1/conversations/{conversation_id}/messages/{message_id}
```

### Frontend Integration
The message deletion feature includes:
- Delete button on user messages (hover overlay)
- Confirmation modal before deletion
- Visual feedback during deletion
- Error handling for failed deletions

## Technical Implementation

### Database Schema

#### MessageReaction Table
```sql
CREATE TABLE message_reactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    emoji VARCHAR(10) NOT NULL,
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Enhanced Conversation Table
```sql
ALTER TABLE conversations ADD COLUMN archived_at TIMESTAMP;
ALTER TABLE conversations RENAME COLUMN conversation_metadata TO metadata;
```

#### Enhanced Message Table
```sql
ALTER TABLE messages RENAME COLUMN message_metadata TO metadata;
ALTER TABLE messages ADD COLUMN reactions JSONB DEFAULT '[]';
```

### Service Layer

#### ConversationService Enhancements
- `search_messages()`: Full-text search with filters
- `export_conversation()`: Multi-format export
- `get_conversation_context()`: Context retrieval
- `update_conversation_context()`: Context updates
- `add_message_reaction()`: Reaction management
- `remove_message_reaction()`: Reaction removal
- `switch_assistant()`: Assistant switching
- `delete_message()`: Message deletion

### Security Considerations

#### Access Control
- Users can only access their own conversations
- Message deletion limited to user's own messages
- Reaction management limited to user's own reactions
- Export access verified against conversation ownership

#### Rate Limiting
- Message search: 100 requests per minute
- Export: 10 requests per minute
- Reactions: 200 requests per minute
- Context updates: 50 requests per minute

#### Data Privacy
- Export files expire after 24 hours
- Deleted messages are permanently removed
- Context data is user-specific and encrypted

## Performance Optimizations

### Search Optimization
- Database indexes on message content and metadata
- Full-text search capabilities
- Pagination for large result sets
- Caching of frequent search results

### Export Optimization
- Asynchronous export processing for large conversations
- File compression for download optimization
- Background cleanup of expired export files
- Streaming for large file downloads

### Real-time Updates
- WebSocket connections for instant updates
- Efficient message broadcasting
- Connection pooling and management
- Graceful disconnection handling

## Future Enhancements

### Planned Features
1. **Advanced Search:** Semantic search using embeddings
2. **Export Templates:** Customizable export formats
3. **Reaction Analytics:** Usage statistics and insights
4. **Context Sharing:** Share context between conversations
5. **Assistant Chaining:** Automatic assistant switching based on content

### Integration Opportunities
1. **Knowledge Base:** Link conversations to knowledge articles
2. **Analytics Dashboard:** Conversation insights and metrics
3. **Collaboration Tools:** Multi-user conversation features
4. **API Integrations:** Third-party tool connections
5. **Mobile Support:** Enhanced mobile chat experience

## Troubleshooting

### Common Issues

#### Search Not Working
- Verify database indexes are created
- Check search query syntax
- Ensure proper permissions

#### Export Fails
- Verify file system permissions
- Check available disk space
- Ensure export format is supported

#### Reactions Not Updating
- Check WebSocket connection status
- Verify user permissions
- Ensure proper error handling

#### Assistant Switch Fails
- Verify assistant exists and is accessible
- Check user permissions for assistant
- Ensure proper context handling

### Debug Information
Enable debug logging to troubleshoot issues:
```python
import logging
logging.getLogger('app.services.conversation_service').setLevel(logging.DEBUG)
```

## Support

For technical support or feature requests related to Enhanced Chat Features, please:

1. Check the [API Documentation](../api/conversations.md)
2. Review the [Troubleshooting Guide](../troubleshooting.md)
3. Contact the development team
4. Submit an issue on the project repository 