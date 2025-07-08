import { Outlet, Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../hooks'
import { logout } from '../features/auth/authSlice'
import ThemeToggle from '../components/ui/ThemeToggle'
import Button from '../components/ui/Button'

const AppLayout = () => {
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((state) => state.auth)

  const handleLogout = () => {
    dispatch(logout())
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      <header className="flex items-center justify-between px-6 py-4 shadow bg-indigo text-smoke">
        <Link to="/dashboard" className="text-xl font-semibold">
          ConvoSphere
        </Link>
        <nav className="flex items-center space-x-4">
          <Link to="/dashboard" className="hover:underline">
            Dashboard
          </Link>
          <Link to="/chat" className="hover:underline">
            Chat
          </Link>
          <ThemeToggle />
          {user && (
            <div className="flex items-center space-x-2">
              <span className="text-sm">Welcome, {user.username}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="text-smoke border-smoke hover:bg-smoke hover:text-indigo"
              >
                Logout
              </Button>
            </div>
          )}
        </nav>
      </header>
      <main className="flex-1 px-4 py-6 container mx-auto">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout
