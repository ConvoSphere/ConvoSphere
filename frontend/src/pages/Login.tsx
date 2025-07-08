import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../hooks'
import { login } from '../features/auth/authSlice'

const LoginPage = () => {
    const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { status, error, accessToken } = useAppSelector((s) => s.auth)

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    dispatch(login({ username, password })).unwrap().then(() => {
      navigate('/dashboard', { replace: true })
    })
  }

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-2xl font-semibold mb-4">Login</h1>
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-700"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-700"
          required
        />
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={status === 'loading'}
          className="w-full bg-indigo text-smoke py-2 rounded disabled:opacity-50"
        >
          {status === 'loading' ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  )
}

export default LoginPage
