import { Navigate } from 'react-router-dom'
import { useAuthState } from '../hooks/useAuthState'
import { useOnboardingCompleted } from '../hooks/useOnboardingCompleted'

/**
 * HOC — wraps a component so it's only accessible when NOT logged in.
 * If the user IS logged in:
 *   → onboarding done   → redirect to /platform
 *   → onboarding pending → redirect to /initial
 * While Firebase is restoring the session, renders nothing (avoids flash).
 */
export function withGuestOnly(Component) {
  return function GuestOnlyWrapper(props) {
    const { user, loading } = useAuthState()
    const { completed, loading: onboardingLoading } = useOnboardingCompleted({ user })

    if (loading) return null   // Firebase restoring session — wait silently

    if (user) {
      if (onboardingLoading || completed === null) return null

      const destination = completed ? '/platform' : '/initial'
      return <Navigate to={destination} replace />
    }

    return <Component {...props} />
  }
}
