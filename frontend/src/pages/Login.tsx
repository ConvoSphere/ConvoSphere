import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch } from '../hooks'
import { setCredentials, setError, clearError } from '../features/auth/authSlice'
import { useLoginMutation, useGetCurrentUserQuery } from '../services/apiSlice'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

const LoginPage = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [login, { isLoading }] = useLoginMutation()
  
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [formError, setFormError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    dispatch(clearError())
    
    try {
      const result = await login({ username, password }).unwrap()
      
      // Get user data after successful login
      const userResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/users/me`, {
        headers: {
          'Authorization': `Bearer ${result.access_token}`
        }
      })
      
      if (userResponse.ok) {
        const user = await userResponse.json()
        dispatch(setCredentials({ accessToken: result.access_token, user }))
        navigate('/dashboard', { replace: true })
      } else {
        throw new Error('Failed to fetch user data')
      }
    } catch (error: any) {
      const errorMessage = error.data?.detail || error.message || 'Login failed'
      setFormError(errorMessage)
      dispatch(setError(errorMessage))
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Welcome to ConvoSphere</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Username"
              type="text"
              value={username}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
            {formError && (
              <p className="text-sm text-red-500">{formError}</p>
            )}
            <Button
              type="submit"
              loading={isLoading}
              className="w-full"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default LoginPage
