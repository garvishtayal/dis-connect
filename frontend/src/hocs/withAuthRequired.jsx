import { Navigate } from 'react-router-dom'
import { useAuthState } from '../hooks/useAuthState'

/**
 * HOC — wraps a component so it's only accessible when the user IS logged in.
 * If the user is NOT logged in → redirect to /login.
 * While Firebase is restoring the session, renders nothing (avoids flash).
 */
export function withAuthRequired(Component) {
  return function AuthRequiredWrapper(props) {
    const { user, loading } = useAuthState()

    if (loading) return null

    if (!user) {
      return <Navigate to="/login" replace />
    }

    return <Component {...props} />
  }
}
