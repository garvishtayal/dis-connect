import { useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { signInWithPopup, signInWithRedirect, getRedirectResult } from 'firebase/auth'
import { toast } from 'sonner'
import { auth, googleProvider } from '../lib/firebase'
import { signInWithGoogle } from '../api/auth'
import { friendlyAuthError } from '../lib/authErrors'

async function signInWithGoogleFlow() {
  try {
    const result = await signInWithPopup(auth, googleProvider)
    const idToken = await result.user.getIdToken()
    return signInWithGoogle(idToken)
  } catch (err) {
    if (
      err.code === 'auth/popup-blocked' ||
      err.code === 'auth/popup-closed-by-user' ||
      err.message?.includes('Cross-Origin-Opener-Policy')
    ) {
      await signInWithRedirect(auth, googleProvider)
      return null
    }
    throw err
  }
}

export function useSignInWithGoogle() {
  return useMutation({
    mutationFn: signInWithGoogleFlow,
    onError: (err) => {
      const msg = friendlyAuthError(err)
      if (msg) toast.error(msg, { duration: 4000 })
    },
  })
}

export function useRedirectResult(onSuccess) {
  useEffect(() => {
    getRedirectResult(auth)
      .then(async (result) => {
        if (!result) return
        const idToken = await result.user.getIdToken()
        const data = await signInWithGoogle(idToken)
        onSuccess?.(data)
      })
      .catch((err) => {
        const msg = friendlyAuthError(err)
        if (msg) toast.error(msg, { duration: 4000 })
      })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}
