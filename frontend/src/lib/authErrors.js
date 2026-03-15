const messages = {
  'auth/invalid-credential':    'Sign-in failed. Try again in a moment.',
  'auth/popup-closed-by-user':  'Sign-in cancelled.',
  'auth/popup-blocked':         'Popup was blocked. Allow popups for this site.',
  'auth/network-request-failed':'No internet connection.',
  'auth/too-many-requests':     'Too many attempts. Wait a bit and try again.',
  'auth/user-disabled':         'This account has been disabled.',
  'auth/cancelled-popup-request': null, // silent — user opened another popup
}

export function friendlyAuthError(err) {
  if (!err) return 'Something went wrong.'
  const mapped = messages[err.code]
  if (mapped === null) return null          // return null = suppress toast
  if (mapped) return mapped
  // Backend API errors are already short strings
  if (err.message && err.message.length < 80) return err.message
  return 'Something went wrong. Please try again.'
}
