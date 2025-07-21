import { store } from '../app/store'
import { setCredentials, logout } from '../features/auth/authSlice'

export interface RefreshTokenResponse {
  access_token: string
  token_type: string
}

class AuthService {
  private refreshPromise: Promise<RefreshTokenResponse> | null = null

  /**
   * Refresh the access token using the refresh token
   */
  public async refreshToken(): Promise<RefreshTokenResponse> {
    // If a refresh is already in progress, return the existing promise
    if (this.refreshPromise) {
      return this.refreshPromise
    }

    this.refreshPromise = this.performRefresh()

    try {
      const result = await this.refreshPromise
      return result
    } finally {
      this.refreshPromise = null
    }
  }

  private async performRefresh(): Promise<RefreshTokenResponse> {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/auth/jwt/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        throw new Error('Failed to refresh token')
      }

      const data: RefreshTokenResponse = await response.json()
      
      // Update the store with new credentials
      const userResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/users/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      })

      if (userResponse.ok) {
        const user = await userResponse.json()
        store.dispatch(setCredentials({ accessToken: data.access_token, user }))
        localStorage.setItem('access_token', data.access_token)
      }

      return data
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.handleAuthError()
      throw error
    }
  }

  /**
   * Handle authentication errors by logging out the user
   */
  public handleAuthError(): void {
    store.dispatch(logout())
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    // Redirect to login page
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
  }

  /**
   * Check if the current token is expired
   */
  public isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const expirationTime = payload.exp * 1000 // Convert to milliseconds
      const currentTime = Date.now()
      
      // Consider token expired if it expires within the next 5 minutes
      return currentTime >= (expirationTime - 5 * 60 * 1000)
    } catch {
      return true
    }
  }

  /**
   * Get the current access token, refreshing if necessary
   */
  public async getValidToken(): Promise<string | null> {
    const currentToken = store.getState().auth.accessToken
    
    if (!currentToken) {
      return null
    }

    if (this.isTokenExpired(currentToken)) {
      try {
        const refreshResult = await this.refreshToken()
        return refreshResult.access_token
      } catch {
        this.handleAuthError()
        return null
      }
    }

    return currentToken
  }

  /**
   * Store tokens in localStorage
   */
  public storeTokens(accessToken: string, refreshToken?: string): void {
    localStorage.setItem('access_token', accessToken)
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken)
    }
  }

  /**
   * Clear all stored tokens
   */
  public clearTokens(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  /**
   * Initialize authentication state from localStorage
   */
  public initializeAuth(): void {
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    
    if (accessToken && !this.isTokenExpired(accessToken)) {
      // Token is valid, fetch user data
      this.fetchUserData(accessToken)
    } else if (refreshToken) {
      // Try to refresh the token
      this.refreshToken().catch(() => {
        this.handleAuthError()
      })
    }
  }

  private async fetchUserData(accessToken: string): Promise<void> {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/users/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })

      if (response.ok) {
        const user = await response.json()
        store.dispatch(setCredentials({ accessToken, user }))
      } else {
        throw new Error('Failed to fetch user data')
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error)
      this.handleAuthError()
    }
  }
}

// Export singleton instance
export const authService = new AuthService() 