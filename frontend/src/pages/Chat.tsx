import { useState, useEffect } from 'react'
import { useGetConversationsQuery, useCreateConversationMutation, useGetMessagesQuery, useSendMessageMutation } from '../services/apiSlice'
import { websocketService, type WebSocketMessage } from '../services/websocketService'
import { fileService, type UploadResult } from '../services/fileService'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import FileUpload from '../components/ui/FileUpload'
import type { Conversation, Message } from '../services/apiSlice'

const ChatPage = () => {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [newConversationTitle, setNewConversationTitle] = useState('')
  const [showNewConversation, setShowNewConversation] = useState(false)
  
  const { data: conversations, isLoading, error } = useGetConversationsQuery()
  const [createConversation, { isLoading: isCreating }] = useCreateConversationMutation()

  const handleCreateConversation = async () => {
    if (!newConversationTitle.trim()) return
    
    try {
      const newConversation = await createConversation({ title: newConversationTitle }).unwrap()
      setSelectedConversation(newConversation)
      setNewConversationTitle('')
      setShowNewConversation(false)
    } catch (error) {
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
                 onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewConversationTitle(e.target.value)}
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

const ChatInterface = ({ conversation }: ChatInterfaceProps) => {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<UploadResult[]>([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  const { data: messages, isLoading } = useGetMessagesQuery(conversation.id)
  const [sendMessage, { isLoading: isSending }] = useSendMessageMutation()

  // WebSocket connection and message handling
  useEffect(() => {
    const connectWebSocket = async () => {
      try {
        await websocketService.connect()
      } catch (error) {
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
      // Send message via WebSocket for real-time delivery
      websocketService.sendMessage({
        type: 'message',
        data: {
          content: message,
          attachments: attachments.map(att => att.id)
        },
        conversation_id: conversation.id
      })

      // Also send via REST API for persistence
      await sendMessage({
        conversation_id: conversation.id,
        content: message
      }).unwrap()
      
      setMessage('')
      setAttachments([])
    } catch (error) {
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
          </div>
          <div className="text-sm text-gray-500">
            {websocketService.isConnected() ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoading ? (
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
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-indigo text-smoke'
                    : 'bg-gray-100 dark:bg-gray-800'
                }`}
              >
                <p className="text-sm">{msg.content}</p>
                <p className="text-xs opacity-75 mt-1">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500">
            No messages yet. Start the conversation!
          </div>
        )}
      </div>

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
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)}
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
