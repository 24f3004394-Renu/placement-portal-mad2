// Thin fetch wrapper: attaches the JWT, parses JSON, throws on error responses.
import { useAuthStore } from './stores/auth'
export const API_BASE = 'http://localhost:5000'

async function request(path, { method = 'GET', body } = {}) {
  const auth = useAuthStore()
  const headers = {}
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`

  const isFormData = body instanceof FormData
  if (body && !isFormData) headers['Content-Type'] = 'application/json'
  // FormData: no Content-Type header at all — fetch/the browser sets
  // "multipart/form-data; boundary=..." itself. Setting it manually breaks
  // the upload because the boundary would be missing.

  const res = await fetch(path, {
    method,
    headers,
    body: isFormData ? body : (body ? JSON.stringify(body) : undefined)
  })

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