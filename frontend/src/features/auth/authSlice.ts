import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { User } from '../../services/apiSlice'

interface AuthState {
  accessToken: string | null
  user: User | null
  status: 'idle' | 'loading' | 'failed'
  error?: string
}

const initialState: AuthState = {
  accessToken: localStorage.getItem('access_token'),
  user: null,
  status: 'idle',
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action: PayloadAction<{ accessToken: string; user: User | null }>) => {
      state.accessToken = action.payload.accessToken
      state.user = action.payload.user
      localStorage.setItem('access_token', action.payload.accessToken)
    },
    logout: (state) => {
      state.accessToken = null
      state.user = null
      localStorage.removeItem('access_token')
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload
      state.status = 'failed'
    },
    clearError: (state) => {
      state.error = undefined
      state.status = 'idle'
    },
  },
})

export const { setCredentials, logout, setError, clearError } = authSlice.actions
export default authSlice.reducer
