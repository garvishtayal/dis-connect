import { auth } from './firebase'

export function saveSession(data) {
  if (data?.user_id)             localStorage.setItem('user_id', data.user_id)
  if (data?.email)               localStorage.setItem('email', data.email)
  if (data?.onboarding_completed !== undefined)
    localStorage.setItem('onboarding_completed', String(data.onboarding_completed))
}

export function clearSession() {
  localStorage.removeItem('user_id')
  localStorage.removeItem('email')
  localStorage.removeItem('onboarding_completed')
}

export const getStoredUserId        = () => localStorage.getItem('user_id')
export const isOnboardingDone       = () => localStorage.getItem('onboarding_completed') === 'true'
export const setOnboardingDone      = () => localStorage.setItem('onboarding_completed', 'true')

/** Returns fresh Firebase ID token — never store this, Firebase auto-refreshes */
export async function getIdToken() {
  const user = auth.currentUser
  if (!user) throw new Error('Not authenticated')
  return user.getIdToken()
}
