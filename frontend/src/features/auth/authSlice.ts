import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import api from '../../services/api'

interface AuthState {
  accessToken: string | null
  status: 'idle' | 'loading' | 'failed'
  error?: string
}

const initialState: AuthState = {
  accessToken: localStorage.getItem('access_token'),
  status: 'idle',
}

export const login = createAsyncThunk(
  'auth/login',
  async (params: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const res = await api.post('/auth/jwt/login', params)
      return res.data.access_token as string
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.detail ?? 'Login failed')
    }
  },
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      state.accessToken = null
      localStorage.removeItem('access_token')
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.status = 'loading'
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<string>) => {
        state.status = 'idle'
        state.accessToken = action.payload
        localStorage.setItem('access_token', action.payload)
      })
      .addCase(login.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.payload as string
      })
  },
})

export const { logout } = authSlice.actions
export default authSlice.reducer
