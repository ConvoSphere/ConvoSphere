import { Outlet, Link } from 'react-router-dom'

const AppLayout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg)] text-[var(--text)]">
      <header className="flex items-center justify-between px-6 py-4 shadow bg-indigo text-smoke dark:bg-indigo dark:text-smoke">
        <Link to="/dashboard" className="text-xl font-semibold">
          ConvoSphere
        </Link>
        <nav className="space-x-4">
          <Link to="/dashboard" className="hover:underline">
            Dashboard
          </Link>
          <Link to="/chat" className="hover:underline">
            Chat
          </Link>
        </nav>
      </header>
      <main className="flex-1 px-4 py-6 container mx-auto">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout
