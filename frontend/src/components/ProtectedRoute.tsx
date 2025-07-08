import { Navigate, Outlet } from 'react-router-dom'
import { useAppSelector } from '../hooks'

const ProtectedRoute = () => {
  const isAuthed = useAppSelector((s) => !!s.auth.accessToken)
  return isAuthed ? <Outlet /> : <Navigate to="/login" replace />
}

export default ProtectedRoute
