import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  try {
    const { isAuthenticated, loading } = useAuth()

    if (loading) {
      return (
        <div className="min-h-screen bg-dark-bg flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-dark-accent"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      return <Navigate to="/login" replace />
    }

    return children
  } catch (error) {
    console.error('ProtectedRoute error:', error)
    return <Navigate to="/login" replace />
  }
}
