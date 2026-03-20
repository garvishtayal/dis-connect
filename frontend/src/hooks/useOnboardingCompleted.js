import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { signInWithGoogle } from '../api/auth'
import { saveSession } from '../lib/session'

/**
 * Returns onboarding completion status for the currently authenticated Firebase user.
 *
 * Priority:
 * 1) localStorage `onboarding_completed` if present
 * 2) otherwise fetch onboarding status from backend using the Firebase ID token
 */
export function useOnboardingCompleted({ user }) {
  const [completed, setCompleted] = useState(null)
  const [loading, setLoading] = useState(false)
  const didFetchForUserId = useRef(null)

  const storedValue = typeof window !== 'undefined'
    ? window.localStorage.getItem('onboarding_completed')
    : null

  useEffect(() => {
    if (!user) return

    // If localStorage already has a value, use it immediately.
    if (storedValue === 'true' || storedValue === 'false') {
      setCompleted(storedValue === 'true')
      return
    }

    // Avoid refetch loops for the same user.
    if (didFetchForUserId.current === user.uid) return
    didFetchForUserId.current = user.uid

    let cancelled = false
    setLoading(true)

    ;(async () => {
      try {
        const idToken = await user.getIdToken()
        const resp = await signInWithGoogle(idToken)
        if (cancelled) return

        const next = Boolean(resp?.onboarding_completed)
        setCompleted(next)

        // Populate localStorage so subsequent navigations are instant.
        saveSession(resp)
      } catch (err) {
        if (cancelled) return
        toast.error('Failed to verify onboarding status.', { duration: 4000 })
        setCompleted(false)
      } finally {
        if (cancelled) return
        setLoading(false)
      }
    })()

    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  return { completed, loading }
}

