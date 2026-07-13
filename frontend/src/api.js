
import { useAuthStore } from './stores/auth'

async function request(path, { method = 'GET', body } = {}) {
  const auth = useAuthStore()
  const headers = {}
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
  if (body) headers['Content-Type'] = 'application/json'

  const res = await fetch(path, { method, headers, body: body ? JSON.stringify(body) : undefined })

  if (res.status === 401) {
    auth.logout()
    throw new Error('Session expired. Please log in again.')
  }
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`)
  return data
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body }),
  patch: (path, body) => request(path, { method: 'PATCH', body }),
  put: (path, body) => request(path, { method: 'PUT', body }),
  delete: (path) => request(path, { method: 'DELETE' }),
}