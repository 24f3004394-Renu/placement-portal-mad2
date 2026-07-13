import { defineStore } from 'pinia'
import router from '../router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
    name: localStorage.getItem('name') || null
  }),
  getters: {
    isLoggedIn: (s) => !!s.token
  },
  actions: {
    async login(email, password) {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Login failed.')

      this.token = data.access_token
      this.role = data.role
      this.name = data.name || 'Admin'
      localStorage.setItem('token', this.token)
      localStorage.setItem('role', this.role)
      localStorage.setItem('name', this.name)

      router.push(`/${this.role}/dashboard`)
    },
    logout() {
      this.token = null; this.role = null; this.name = null
      localStorage.removeItem('token'); localStorage.removeItem('role'); localStorage.removeItem('name')
      router.push('/login')
    }
  }
})