import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { BaseQueryFn } from '@reduxjs/toolkit/query/react'
import type { RootState } from '../app/store'
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
  username: string
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

// Custom base query with token refresh logic
const baseQueryWithReauth: BaseQueryFn = async (args, api, extraOptions) => {
  const baseQuery = fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
    prepareHeaders: async (headers, { getState }) => {
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
  tagTypes: ['User', 'Conversation', 'Message', 'Dashboard'],
  endpoints: (builder) => ({
    // Authentication endpoints
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/auth/jwt/login',
        method: 'POST',
        body: credentials,
      }),
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
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
      query: () => '/users/me',
      providesTags: ['User'],
    }),
    
    // Conversation endpoints
    getConversations: builder.query<Conversation[], void>({
      query: () => '/conversations',
      providesTags: ['Conversation'],
    }),
    
    getConversation: builder.query<Conversation, string>({
      query: (id) => `/conversations/${id}`,
      providesTags: (result, error, id) => [{ type: 'Conversation', id }],
    }),
    
    createConversation: builder.mutation<Conversation, { title: string }>({
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
      providesTags: (result, error, conversationId) => [
        { type: 'Message', id: conversationId }
      ],
    }),
    
    sendMessage: builder.mutation<Message, { conversation_id: string; content: string }>({
      query: (message) => ({
        url: `/conversations/${message.conversation_id}/messages`,
        method: 'POST',
        body: { content: message.content },
      }),
      invalidatesTags: (result, error, { conversation_id }) => [
        { type: 'Message', id: conversation_id },
        { type: 'Conversation', id: conversation_id }
      ],
    }),
    
    // Dashboard endpoints
    getDashboardStats: builder.query<DashboardStats, void>({
      query: () => '/dashboard/stats',
      providesTags: ['Dashboard'],
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
} = apiSlice 