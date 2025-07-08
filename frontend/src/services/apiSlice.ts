import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { BaseQueryFn } from '@reduxjs/toolkit/query/react'
import { authService } from './authService'

// Define types for API responses
export interface User {
  id: string
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages_count: number
}

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  created_at: string
  conversation_id: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface DashboardStats {
  total_conversations: number
  total_messages: number
  active_assistants: number
  recent_activity: Array<{
    id: string
    type: string
    description: string
    created_at: string
  }>
}

export interface Assistant {
  id: string
  name: string
  description?: string
  version: string
  personality?: string
  system_prompt: string
  instructions?: string
  model: string
  temperature: string
  max_tokens: string
  status: string
  is_public: boolean
  is_template: boolean
  tools_config: Array<Record<string, any>>
  tools_enabled: boolean
  category?: string
  tags: string[]
  metadata: Record<string, any>
  creator_id: string
  created_at?: string
  updated_at?: string
  tool_count: number
  is_active: boolean
}

export interface AssistantCreate {
  name: string
  system_prompt: string
  description?: string
  personality?: string
  instructions?: string
  model: string
  temperature: string
  max_tokens: string
  category?: string
  tags: string[]
  is_public: boolean
  is_template: boolean
}

export interface AssistantUpdate {
  name?: string
  system_prompt?: string
  description?: string
  personality?: string
  instructions?: string
  model?: string
  temperature?: string
  max_tokens?: string
  category?: string
  tags?: string[]
  is_public?: boolean
  is_template?: boolean
  status?: string
  tools_enabled?: boolean
}

export interface Document {
  id: string
  title: string
  description?: string
  file_name: string
  file_type: string
  file_size: number
  status: string
  tags: string[]
  chunk_count: number
  total_tokens: number
  created_at: string
  updated_at: string
  processed_at?: string
}

export interface DocumentList {
  documents: Document[]
  total: number
  skip: number
  limit: number
}

export interface SearchRequest {
  query: string
  filters?: Record<string, any>
  limit?: number
  include_metadata?: boolean
}

export interface SearchResponse {
  results: Array<{
    document_id: string
    title: string
    content: string
    score: number
    metadata?: Record<string, any>
  }>
  total: number
  query: string
}

// Custom base query with token refresh logic
const baseQueryWithReauth: BaseQueryFn = async (args, api, extraOptions) => {
  const baseQuery = fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
    prepareHeaders: async (headers) => {
      const token = await authService.getValidToken()
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  })

  let result = await baseQuery(args, api, extraOptions)

  if (result.error && result.error.status === 401) {
    // Try to refresh the token
    try {
      await authService.refreshToken()
      // Retry the original request
      result = await baseQuery(args, api, extraOptions)
    } catch (error) {
      // Refresh failed, user will be logged out
      authService.handleAuthError()
    }
  }

  return result
}

// Create the API slice
export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User', 'Conversation', 'Message', 'Dashboard', 'Assistants', 'PublicAssistants', 'Documents', 'SearchHistory', 'SupportedFormats'],
  endpoints: (builder) => ({
    // Authentication endpoints
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
      async onQueryStarted(_, { queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          // Store both tokens
          authService.storeTokens(data.access_token, data.refresh_token)
        } catch (error) {
          console.error('Login failed:', error)
        }
      },
    }),
    
    register: builder.mutation<User, RegisterRequest>({
      query: (userData) => ({
        url: '/auth/register',
        method: 'POST',
        body: userData,
      }),
    }),
    
    getCurrentUser: builder.query<User, void>({
      query: () => '/auth/me',
      providesTags: ['User'],
    }),
    
    // Conversation endpoints
    getConversations: builder.query<Conversation[], void>({
      query: () => '/conversations',
      providesTags: ['Conversation'],
    }),
    
    getConversation: builder.query<Conversation, string>({
      query: (id) => `/conversations/${id}`,
      providesTags: (_, __, id) => [{ type: 'Conversation', id }],
    }),
    
    createConversation: builder.mutation<Conversation, { assistant_id: string; title?: string }>({
      query: (conversation) => ({
        url: '/conversations',
        method: 'POST',
        body: conversation,
      }),
      invalidatesTags: ['Conversation'],
    }),
    
    // Message endpoints
    getMessages: builder.query<Message[], string>({
      query: (conversationId) => `/conversations/${conversationId}/messages`,
      providesTags: (_, __, conversationId) => [
        { type: 'Message', id: conversationId }
      ],
    }),
    
    sendMessage: builder.mutation<Message, { conversation_id: string; content: string }>({
      query: (message) => ({
        url: `/conversations/${message.conversation_id}/messages`,
        method: 'POST',
        body: { content: message.content },
      }),
      invalidatesTags: (_, __, { conversation_id }) => [
        { type: 'Message', id: conversation_id },
        { type: 'Conversation', id: conversation_id }
      ],
    }),
    
    // Dashboard endpoints
    getDashboardStats: builder.query<DashboardStats, void>({
      query: () => '/dashboard/stats',
      providesTags: ['Dashboard'],
    }),

    // Assistant endpoints
    getAssistants: builder.query<Assistant[], { status?: string; category?: string; include_public?: boolean }>({
      query: (params) => ({
        url: '/assistants/',
        params,
      }),
      providesTags: ['Assistants'],
    }),

    getAssistant: builder.query<Assistant, string>({
      query: (id) => `/assistants/${id}`,
      providesTags: (_result, _error, id) => [{ type: 'Assistants', id }],
    }),

    createAssistant: builder.mutation<Assistant, AssistantCreate>({
      query: (assistant) => ({
        url: '/assistants/',
        method: 'POST',
        body: assistant,
      }),
      invalidatesTags: ['Assistants'],
    }),

    updateAssistant: builder.mutation<Assistant, { id: string; data: AssistantUpdate }>({
      query: ({ id, data }) => ({
        url: `/assistants/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: 'Assistants', id }, 'Assistants'],
    }),

    deleteAssistant: builder.mutation<void, string>({
      query: (id) => ({
        url: `/assistants/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Assistants'],
    }),

    activateAssistant: builder.mutation<Assistant, string>({
      query: (id) => ({
        url: `/assistants/${id}/activate`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _error, id) => [{ type: 'Assistants', id }, 'Assistants'],
    }),

    deactivateAssistant: builder.mutation<Assistant, string>({
      query: (id) => ({
        url: `/assistants/${id}/deactivate`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _error, id) => [{ type: 'Assistants', id }, 'Assistants'],
    }),

    getPublicAssistants: builder.query<Assistant[], { category?: string; tags?: string; limit?: number }>({
      query: (params) => ({
        url: '/assistants/public',
        params,
      }),
      providesTags: ['PublicAssistants'],
    }),

    // Knowledge Base endpoints
    getDocuments: builder.query<DocumentList, { skip?: number; limit?: number; status?: string }>({
      query: (params) => ({
        url: '/knowledge/documents',
        params,
      }),
      providesTags: ['Documents'],
    }),

    getDocument: builder.query<Document, string>({
      query: (id) => `/knowledge/documents/${id}`,
      providesTags: (_result, _error, id) => [{ type: 'Documents', id }],
    }),

    uploadDocument: builder.mutation<Document, FormData>({
      query: (formData) => ({
        url: '/knowledge/documents',
        method: 'POST',
        body: formData,
        // Don't set Content-Type header, let browser set it with boundary
      }),
      invalidatesTags: ['Documents'],
    }),

    deleteDocument: builder.mutation<void, string>({
      query: (id) => ({
        url: `/knowledge/documents/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Documents'],
    }),

    processDocument: builder.mutation<void, string>({
      query: (id) => ({
        url: `/knowledge/documents/${id}/process`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _error, id) => [{ type: 'Documents', id }, 'Documents'],
    }),

    searchDocuments: builder.mutation<SearchResponse, SearchRequest>({
      query: (searchRequest) => ({
        url: '/knowledge/search',
        method: 'POST',
        body: searchRequest,
      }),
    }),

    getSearchHistory: builder.query<Array<{ id: string; query: string; created_at: string }>, { skip?: number; limit?: number }>({
      query: (params) => ({
        url: '/knowledge/search/history',
        params,
      }),
      providesTags: ['SearchHistory'],
    }),

    getSupportedFormats: builder.query<string[], void>({
      query: () => '/knowledge/processing/supported-formats',
      providesTags: ['SupportedFormats'],
    }),
  }),
})

// Export hooks for use in components
export const {
  useLoginMutation,
  useRegisterMutation,
  useGetCurrentUserQuery,
  useGetConversationsQuery,
  useGetConversationQuery,
  useCreateConversationMutation,
  useGetMessagesQuery,
  useSendMessageMutation,
  useGetDashboardStatsQuery,
  useGetAssistantsQuery,
  useGetAssistantQuery,
  useCreateAssistantMutation,
  useUpdateAssistantMutation,
  useDeleteAssistantMutation,
  useActivateAssistantMutation,
  useDeactivateAssistantMutation,
  useGetPublicAssistantsQuery,
  useGetDocumentsQuery,
  useGetDocumentQuery,
  useUploadDocumentMutation,
  useDeleteDocumentMutation,
  useProcessDocumentMutation,
  useSearchDocumentsMutation,
  useGetSearchHistoryQuery,
  useGetSupportedFormatsQuery,
} = apiSlice 