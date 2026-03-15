import { request } from './client.js'

/**
 * POST /api/users — create user (onboarding).
 * Requires Bearer token. Body: { initial_prompt }.
 * Returns { user_id, soul, onboarding_completed }.
 */
export async function createUser(initialPrompt) {
  return request('/api/users', {
    method: 'POST',
    auth: true,
    body: JSON.stringify({ initial_prompt: initialPrompt }),
  })
}
