import { request } from './client.js'

export async function signInWithGoogle(idToken) {
  return request('/api/auth/google', {
    method: 'POST',
    body: JSON.stringify({ id_token: idToken }),
  })
}
