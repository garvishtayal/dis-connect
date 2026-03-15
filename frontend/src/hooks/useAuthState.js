import { useState, useEffect } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../lib/firebase'

/**
 * Listens to Firebase auth state.
 * Returns { user, loading }
 *   user    = Firebase user object (or null if not logged in)
 *   loading = true while Firebase is restoring the persisted session
 */
export function useAuthState() {
  const [state, setState] = useState({ user: null, loading: true })

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (user) => {
      setState({ user, loading: false })
    })
    return unsub
  }, [])

  return state
}
