import { Navigate } from 'react-router-dom'
import { useAuthState } from '../hooks/useAuthState'

/**
 * HOC — only require that the user is logged in.
 * /initial is also used for "update profile", so we do NOT gate by onboarding completion.
 *
 * Redirects:
 * - not logged in → /login
 */
export function withOnboardingPendingRequired(Component) {
  return function OnboardingPendingRequiredWrapper(props) {
    const { user, loading } = useAuthState()

    if (loading) return null

    if (!user) {
      return <Navigate to="/login" replace />
    }

    return <Component {...props} />
  }
}

