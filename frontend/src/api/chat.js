import { request } from './client.js'
import { getStoredUserId } from '../lib/session'

/**
 * POST /api/chat — send a message and get assistant response.
 * Requires Bearer token. Body: { user_id, message }.
 * Returns { chat_response, needs_new_content, new_content? }.
 */
export async function sendChatMessage(message) {
  const user_id = getStoredUserId()
  if (!user_id) throw new Error('Not authenticated')
  return request('/api/chat', {
    method: 'POST',
    auth: true,
    body: JSON.stringify({ user_id, message }),
  })
}
