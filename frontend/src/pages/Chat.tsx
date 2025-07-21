import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useGetConversationsQuery, useCreateConversationMutation, useGetMessagesQuery, useSendMessageMutation, useSearchMessagesMutation, type Message, useExportConversationMutation, useGetAssistantsQuery, useUpdateConversationMutation, useGetConversationContextQuery, useUpdateConversationContextMutation, useAddMessageReactionMutation, useRemoveMessageReactionMutation, type MessageReaction, useDeleteMessageMutation } from '../services/apiSlice'
import type { Conversation } from '../services/apiSlice'
import { websocketService, type WebSocketMessage } from '../services/websocketService'
import { fileService, type UploadResult } from '../services/fileService'
import { Button, Input } from '../components/ui'
import FileUpload from '../components/ui/FileUpload'

const ChatPage = () => {
  useTranslation() // t wird aktuell nicht verwendet
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [newConversationTitle, setNewConversationTitle] = useState('')
  const [showNewConversation, setShowNewConversation] = useState(false)
  
  const { data: conversations, isLoading, error } = useGetConversationsQuery(undefined)
  const [createConversation, { isLoading: isCreating }] = useCreateConversationMutation()

  const handleCreateConversation = async () => {
    if (!newConversationTitle.trim()) return
    
    try {
      const newConversation = await createConversation({ 
        assistant_id: 'default', // TODO: Get from available assistants
        title: newConversationTitle 
      }).unwrap()
      setSelectedConversation(newConversation)
      setNewConversationTitle('')
      setShowNewConversation(false)
    } catch (error: unknown) {
      console.error('Failed to create conversation:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Failed to load conversations</p>
      </div>
    )
  }

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className="w-80 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Conversations</h2>
            <Button
              size="sm"
              onClick={() => setShowNewConversation(true)}
            >
              New Chat
            </Button>
          </div>
          
          {showNewConversation && (
            <div className="space-y-2 mb-4">
                             <Input
                 placeholder="Conversation title..."
                 value={newConversationTitle}
                 onChange={setNewConversationTitle}
                 onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleCreateConversation()}
               />
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  loading={isCreating}
                  onClick={handleCreateConversation}
                >
                  Create
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setShowNewConversation(false)
                    setNewConversationTitle('')
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto">
          {conversations && conversations.length > 0 ? (
            <div className="space-y-1 p-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedConversation?.id === conversation.id
                      ? 'bg-indigo text-smoke'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                  onClick={() => setSelectedConversation(conversation)}
                >
                  <div className="font-medium truncate">{conversation.title}</div>
                  <div className="text-sm opacity-75">
                    {conversation.messages_count} messages
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 text-center text-gray-500">
              No conversations yet. Start a new chat!
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <ChatInterface conversation={selectedConversation} />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Welcome to ConvoSphere Chat</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Select a conversation or start a new one to begin chatting.
              </p>
              <Button onClick={() => setShowNewConversation(true)}>
                Start New Conversation
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Chat Interface Component
interface ChatInterfaceProps {
  conversation: Conversation
}

const exportFormats = [
  { value: 'json', label: 'JSON' },
  { value: 'markdown', label: 'Markdown' },
  { value: 'pdf', label: 'PDF' },
  { value: 'txt', label: 'Text' },
]

const commonEmojis = ['👍', '👎', '❤️', '😂', '😮', '😢', '😡', '🎉', '👏', '🔥', '💯', '🤔', '👀', '💪', '🙏', '✨']

const ChatInterface = ({ conversation }: ChatInterfaceProps) => {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<UploadResult[]>([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  const { data: messages, isLoading } = useGetMessagesQuery({ conversationId: conversation.id })
  const [sendMessage, { isLoading: isSending }] = useSendMessageMutation()
  // Message search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchActive, setSearchActive] = useState(false)
  const [searchMessages, { data: searchResults, isLoading: isSearching }] = useSearchMessagesMutation()
  const [exportFormat, setExportFormat] = useState('json')
  const [exportConversation, { isLoading: isExporting }] = useExportConversationMutation()
  const [exportError, setExportError] = useState<string | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)
  const { data: assistants, isLoading: isLoadingAssistants } = useGetAssistantsQuery({ status: 'active' })
  const [updateConversation, { isLoading: isUpdatingConversation }] = useUpdateConversationMutation()
  const [selectedAssistantId, setSelectedAssistantId] = useState(conversation.assistant_id || '')
  const [assistantError, setAssistantError] = useState<string | null>(null)
  const [showContext, setShowContext] = useState(false)
  const { data: context, isLoading: isLoadingContext } = useGetConversationContextQuery(conversation.id)
  const [updateContext, { isLoading: isUpdatingContext }] = useUpdateConversationContextMutation()
  const [contextError, setContextError] = useState<string | null>(null)
  const [userPreferences, setUserPreferences] = useState<Record<string, unknown>>({})
  const [addReaction] = useAddMessageReactionMutation()
  const [removeReaction] = useRemoveMessageReactionMutation()
  const [showReactionPicker, setShowReactionPicker] = useState<string | null>(null)
  const [deleteMessage, { isLoading: isDeleting }] = useDeleteMessageMutation()
  const [messageToDelete, setMessageToDelete] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  // WebSocket connection and message handling
  useEffect(() => {
    const connectWebSocket = async () => {
      try {
        await websocketService.connect()
      } catch (error: unknown) {
        console.error('Failed to connect WebSocket:', error)
      }
    }

    connectWebSocket()

    // Subscribe to real-time messages
    const unsubscribe = websocketService.subscribe('message', (wsMessage: WebSocketMessage) => {
      if (wsMessage.conversation_id === conversation.id) {
        // Handle real-time message updates
        console.log('Received real-time message:', wsMessage)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [conversation.id])

  const handleSendMessage = async () => {
    if (!message.trim() && attachments.length === 0) return
    try {
      websocketService.sendMessage({
        type: 'message',
        data: {
          content: message,
          attachments: attachments.map(att => att.id)
        },
        conversation_id: conversation.id
      })
      await sendMessage({
        conversation_id: conversation.id,
        content: message
      }).unwrap()
      setMessage('')
      setAttachments([])
    } catch (error: unknown) {
      console.error('Failed to send message:', error)
    }
  }

  const handleFileUpload = (result: UploadResult) => {
    setAttachments(prev => [...prev, result])
    setShowFileUpload(false)
  }

  const removeAttachment = (fileId: string) => {
    setAttachments(prev => prev.filter(att => att.id !== fileId))
  }

  // Message search handlers
  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setSearchActive(true)
    await searchMessages({ conversation_id: conversation.id, query: searchQuery })
  }
  const handleClearSearch = () => {
    setSearchQuery('')
    setSearchActive(false)
  }

  // Export handler
  const handleExport = async () => {
    setExportError(null)
    setDownloadUrl(null)
    try {
      const result = await exportConversation({
        conversation_id: conversation.id,
        format: exportFormat as ExportFormat,
        include_metadata: true,
        include_attachments: true,
      }).unwrap()
      setDownloadUrl(result.download_url)
    } catch {
      setExportError('Export failed')
    }
  }

  // Handle assistant switching
  const handleAssistantChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newAssistantId = e.target.value
    setSelectedAssistantId(newAssistantId)
    setAssistantError(null)
    try {
      await updateConversation({
        id: conversation.id,
        data: { assistant_id: newAssistantId }
      }).unwrap()
    } catch {
      setAssistantError('Failed to switch assistant')
    }
  }

  // Handle context updates
  const handleContextUpdate = async () => {
    setContextError(null)
    try {
      await updateContext({
        conversation_id: conversation.id,
        context: { user_preferences: userPreferences }
      }).unwrap()
    } catch {
      setContextError('Failed to update context')
    }
  }

  // Handle adding reaction
  const handleAddReaction = async (messageId: string, emoji: string) => {
    try {
      await addReaction({
        conversation_id: conversation.id,
        message_id: messageId,
        emoji
      }).unwrap()
    } catch {
      // Fehler beim Hinzufügen der Reaktion ignorieren
    }
  }

  // Handle removing reaction
  const handleRemoveReaction = async (messageId: string, reactionId: string) => {
    try {
      await removeReaction({
        conversation_id: conversation.id,
        message_id: messageId,
        reaction_id: reactionId
      }).unwrap()
    } catch {
      // Fehler beim Entfernen der Reaktion ignorieren
    }
  }

  // Group reactions by emoji
  const groupReactions = (reactions: MessageReaction[] = []) => {
    const grouped: Record<string, { count: number; reactions: MessageReaction[] }> = {}
    reactions.forEach(reaction => {
      if (!grouped[reaction.emoji]) {
        grouped[reaction.emoji] = { count: 0, reactions: [] }
      }
      grouped[reaction.emoji].count++
      grouped[reaction.emoji].reactions.push(reaction)
    })
    return grouped
  }

  // Handle message deletion
  const handleDeleteMessage = async (messageId: string) => {
    try {
      await deleteMessage({
        conversation_id: conversation.id,
        message_id: messageId
      }).unwrap()
      setShowDeleteConfirm(false)
      setMessageToDelete(null)
    } catch {
      // Fehler beim Löschen der Nachricht ignorieren
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">{conversation.title}</h2>
            <p className="text-sm text-gray-500">
              {conversation.messages_count} messages
            </p>
            {/* Assistant Switcher */}
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-gray-500">Assistant:</span>
              <select
                className="border rounded px-2 py-1 text-sm"
                value={selectedAssistantId}
                onChange={handleAssistantChange}
                disabled={isLoadingAssistants || isUpdatingConversation}
              >
                {assistants && assistants.length > 0 ? (
                  assistants.map(a => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))
                ) : (
                  <option value="">No assistants</option>
                )}
              </select>
              {isUpdatingConversation && <span className="text-xs text-gray-400 ml-2">Updating...</span>}
            </div>
            {assistantError && <div className="text-xs text-red-500 mt-1">{assistantError}</div>}
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-500">
              {websocketService.isConnected() ? '🟢 Connected' : '🔴 Disconnected'}
            </div>
            {/* Context Toggle */}
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowContext(!showContext)}
            >
              {showContext ? 'Hide' : 'Show'} Context
            </Button>
            {/* Export Dropdown */}
            <div className="flex items-center gap-2">
              <select
                className="border rounded px-2 py-1 text-sm"
                value={exportFormat}
                onChange={e => setExportFormat(e.target.value)}
                disabled={isExporting}
              >
                {exportFormats.map(f => (
                  <option key={f.value} value={f.value}>{f.label}</option>
                ))}
              </select>
              <Button size="sm" onClick={handleExport} loading={isExporting}>
                Export
              </Button>
            </div>
          </div>
        </div>
        {/* Context Management Section */}
        {showContext && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="text-sm font-semibold mb-3">Conversation Context</h3>
            {isLoadingContext ? (
              <div className="text-sm text-gray-500">Loading context...</div>
            ) : context ? (
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-500">Context Window:</label>
                  <div className="text-sm">{context.context_window} messages</div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Relevant Documents:</label>
                  <div className="text-sm">
                    {context.relevant_documents.length > 0 ? (
                      <ul className="list-disc list-inside">
                        {context.relevant_documents.map((docId, index) => (
                          <li key={index}>{docId}</li>
                        ))}
                      </ul>
                    ) : (
                      'No documents'
                    )}
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">User Preferences:</label>
                  <div className="text-sm">
                    <textarea
                      className="w-full p-2 border rounded text-xs"
                      rows={3}
                      placeholder="Enter user preferences (JSON format)"
                      value={JSON.stringify(context.user_preferences || {}, null, 2)}
                      onChange={(e) => {
                        try {
                          setUserPreferences(JSON.parse(e.target.value))
                        } catch {
                          // Invalid JSON, ignore
                        }
                      }}
                    />
                    <Button
                      size="sm"
                      onClick={handleContextUpdate}
                      loading={isUpdatingContext}
                      className="mt-2"
                    >
                      Update Preferences
                    </Button>
                  </div>
                </div>
                {contextError && <div className="text-xs text-red-500">{contextError}</div>}
              </div>
            ) : (
              <div className="text-sm text-gray-500">No context available</div>
            )}
          </div>
        )}
        {/* Message Search Bar */}
        <div className="mt-4 flex items-center gap-2">
          <Input
            placeholder="Search messages..."
            value={searchQuery}
            onChange={setSearchQuery}
            onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleSearch()}
            className="flex-1"
          />
          {searchActive ? (
            <Button size="sm" variant="outline" onClick={handleClearSearch}>Clear</Button>
          ) : (
            <Button size="sm" onClick={handleSearch} disabled={!searchQuery.trim() || isSearching}>Search</Button>
          )}
        </div>
        {/* Export result */}
        {downloadUrl && (
          <div className="mt-2">
            <a
              href={downloadUrl}
              download
              className="text-indigo-600 hover:underline text-sm"
              target="_blank"
              rel="noopener noreferrer"
            >
              Download exported conversation
            </a>
          </div>
        )}
        {exportError && (
          <div className="mt-2 text-red-500 text-sm">{exportError}</div>
        )}
      </div>

      {/* Messages or Search Results */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {searchActive ? (
          isSearching ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo"></div>
            </div>
          ) : searchResults && searchResults.messages.length > 0 ? (
            <>
              <div className="mb-2 text-xs text-gray-500">{searchResults.total} result(s) for "{searchResults.query}"</div>
              {searchResults.messages.map((msg: Message) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg relative group ${
                      msg.role === 'user'
                        ? 'bg-indigo text-smoke'
                        : 'bg-gray-100 dark:bg-gray-800'
                    }`}
                  >
                    {/* Delete Button (Hover Overlay) */}
                    {msg.role === 'user' && (
                      <div className="absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors"
                          onClick={() => {
                            setMessageToDelete(msg.id)
                            setShowDeleteConfirm(true)
                          }}
                          title="Delete message"
                        >
                          ×
                        </button>
                      </div>
                    )}
                    <p className="text-sm">{msg.content}</p>
                    <p className="text-xs opacity-75 mt-1">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                    {/* Message Reactions */}
                    {msg.reactions && msg.reactions.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {Object.entries(groupReactions(msg.reactions)).map(([emoji, { count, reactions }]) => (
                          <button
                            key={emoji}
                            className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded-full text-xs hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                            onClick={() => {
                              // Check if user already reacted
                              const userReaction = reactions.find(r => r.user_id === 'current-user-id') // TODO: Get actual user ID
                              if (userReaction) {
                                handleRemoveReaction(msg.id, userReaction.id)
                              } else {
                                handleAddReaction(msg.id, emoji)
                              }
                            }}
                          >
                            {emoji} {count}
                          </button>
                        ))}
                      </div>
                    )}
                    {/* Reaction Picker */}
                    <div className="mt-2 relative">
                      <button
                        className="text-xs opacity-75 hover:opacity-100 transition-opacity"
                        onClick={() => setShowReactionPicker(showReactionPicker === msg.id ? null : msg.id)}
                      >
                        😊 Add reaction
                      </button>
                      {showReactionPicker === msg.id && (
                        <div className="absolute bottom-full left-0 mb-2 p-2 bg-white dark:bg-gray-800 border rounded-lg shadow-lg z-10">
                          <div className="grid grid-cols-8 gap-1">
                            {commonEmojis.map(emoji => (
                              <button
                                key={emoji}
                                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-sm"
                                onClick={() => {
                                  handleAddReaction(msg.id, emoji)
                                  setShowReactionPicker(null)
                                }}
                              >
                                {emoji}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <div className="text-center text-gray-500">No results found.</div>
          )
        ) : isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo"></div>
          </div>
        ) : messages && messages.length > 0 ? (
          messages.map((msg: Message) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg relative group ${
                  msg.role === 'user'
                    ? 'bg-indigo text-smoke'
                    : 'bg-gray-100 dark:bg-gray-800'
                }`}
              >
                {/* Delete Button (Hover Overlay) */}
                {msg.role === 'user' && (
                  <div className="absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors"
                      onClick={() => {
                        setMessageToDelete(msg.id)
                        setShowDeleteConfirm(true)
                      }}
                      title="Delete message"
                    >
                      ×
                    </button>
                  </div>
                )}
                <p className="text-sm">{msg.content}</p>
                <p className="text-xs opacity-75 mt-1">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </p>
                {/* Message Reactions */}
                {msg.reactions && msg.reactions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {Object.entries(groupReactions(msg.reactions)).map(([emoji, { count, reactions }]) => (
                      <button
                        key={emoji}
                        className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded-full text-xs hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                        onClick={() => {
                          // Check if user already reacted
                          const userReaction = reactions.find(r => r.user_id === 'current-user-id') // TODO: Get actual user ID
                          if (userReaction) {
                            handleRemoveReaction(msg.id, userReaction.id)
                          } else {
                            handleAddReaction(msg.id, emoji)
                          }
                        }}
                      >
                        {emoji} {count}
                      </button>
                    ))}
                  </div>
                )}
                {/* Reaction Picker */}
                <div className="mt-2 relative">
                  <button
                    className="text-xs opacity-75 hover:opacity-100 transition-opacity"
                    onClick={() => setShowReactionPicker(showReactionPicker === msg.id ? null : msg.id)}
                  >
                    😊 Add reaction
                  </button>
                  {showReactionPicker === msg.id && (
                    <div className="absolute bottom-full left-0 mb-2 p-2 bg-white dark:bg-gray-800 border rounded-lg shadow-lg z-10">
                      <div className="grid grid-cols-8 gap-1">
                        {commonEmojis.map(emoji => (
                          <button
                            key={emoji}
                            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-sm"
                            onClick={() => {
                              handleAddReaction(msg.id, emoji)
                              setShowReactionPicker(null)
                            }}
                          >
                            {emoji}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500">
            No messages yet. Start the conversation!
          </div>
        )}
      </div>
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Delete Message</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Are you sure you want to delete this message? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowDeleteConfirm(false)
                  setMessageToDelete(null)
                }}
              >
                Cancel
              </Button>
                              <Button
                  variant="danger"
                  onClick={() => messageToDelete && handleDeleteMessage(messageToDelete)}
                  loading={isDeleting}
                >
                  Delete
                </Button>
            </div>
          </div>
        </div>
      )}

      {/* Attachments Preview */}
      {attachments.length > 0 && (
        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-2">
            {attachments.map((attachment) => (
              <div
                key={attachment.id}
                className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-lg"
              >
                <span>{fileService.getFileIcon(attachment.mime_type)}</span>
                <span className="text-sm truncate max-w-32">{attachment.filename}</span>
                <button
                  onClick={() => removeAttachment(attachment.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* File Upload */}
      {showFileUpload && (
        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
          <FileUpload
            variant="chat"
            onUpload={handleFileUpload}
            onError={(error) => console.error('Upload error:', error)}
          />
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFileUpload(!showFileUpload)}
            disabled={isSending}
          >
            📎
          </Button>
          <Input
            placeholder="Type your message..."
            value={message}
            onChange={setMessage}
            onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleSendMessage()}
            className="flex-1"
          />
          <Button
            loading={isSending}
            onClick={handleSendMessage}
            disabled={!message.trim() && attachments.length === 0}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
