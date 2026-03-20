import { Navigate } from 'react-router-dom'
import { useAuthState } from '../hooks/useAuthState'
import { useOnboardingCompleted } from '../hooks/useOnboardingCompleted'

/**
 * HOC — only allow access when:
 * - user is logged in
 * - onboarding is completed
 *
 * Redirects:
 * - not logged in → /login
 * - onboarding pending → /initial
 */
export function withOnboardingDoneRequired(Component) {
  return function OnboardingDoneRequiredWrapper(props) {
    const { user, loading } = useAuthState()
    const { completed, loading: onboardingLoading } = useOnboardingCompleted({ user })

    if (loading) return null

    if (!user) {
      return <Navigate to="/login" replace />
    }

    if (onboardingLoading || completed === null) return null
    if (!completed) return <Navigate to="/initial" replace />

    return <Component {...props} />
  }
}

