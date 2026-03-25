import { request } from './client.js'

export async function fetchContent({ userId, limit = 100, offset = 0 }) {
  const params = new URLSearchParams({
    user_id: userId,
    limit: String(limit),
    offset: String(offset),
  })

  return request(`/api/content?${params.toString()}`, { auth: true })
}

