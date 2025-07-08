import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from '../layout/AppLayout'
import LoginPage from '../pages/Login'
import DashboardPage from '../pages/Dashboard'
import ChatPage from '../pages/Chat'
import AssistantsPage from '../pages/Assistants'
import KnowledgePage from '../pages/Knowledge'
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
          { path: 'assistants', element: <AssistantsPage /> },
          { path: 'knowledge', element: <KnowledgePage /> },
        ],
      },
    ],
  },
])

export default router
