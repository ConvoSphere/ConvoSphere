import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from '../layout/AppLayout'
import LoginPage from '../pages/Login'
import DashboardPage from '../pages/Dashboard'
import ChatPage from '../pages/Chat'
import ProtectedRoute from '../components/ProtectedRoute'

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'login', element: <LoginPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'dashboard', element: <DashboardPage /> },
          { path: 'chat', element: <ChatPage /> },
        ],
      },
    ],
  },
])

export default router
