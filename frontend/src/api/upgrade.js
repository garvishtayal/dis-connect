import { request } from './client.js'
import { getStoredUserId } from '../lib/session'

export async function submitUpgradeFeedback({ upgraded, feedback, willing_to_pay }) {
  const user_id = getStoredUserId()
  if (!user_id) throw new Error('Not authenticated')

  return request('/api/upgrade', {
    method: 'POST',
    auth: true,
    body: JSON.stringify({
      user_id,
      upgraded: Boolean(upgraded),
      feedback: feedback || '',
      willing_to_pay: willing_to_pay || '',
    }),
  })
}

export async function getUpgradeFeedback() {
  const user_id = getStoredUserId()
  if (!user_id) throw new Error('Not authenticated')
  return request(`/api/upgrade?user_id=${encodeURIComponent(user_id)}`, { auth: true })
}
