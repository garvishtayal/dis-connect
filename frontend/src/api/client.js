import { auth } from '../lib/firebase'

const getApiUrl = () => import.meta.env.VITE_API_URL || 'http://localhost:8080'

export async function request(path, { auth: withAuth = false, ...options } = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers }

  if (withAuth) {
    const user = auth.currentUser
    if (user) {
      const token = await user.getIdToken()   // auto-refreshed by Firebase if expired
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const url = path.startsWith('http') ? path : `${getApiUrl()}${path}`
  const res = await fetch(url, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || 'Request failed')
  return data
}
