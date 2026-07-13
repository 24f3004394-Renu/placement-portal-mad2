<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()

const links = {
  admin: [
    { to: '/admin/dashboard', label: 'Dashboard' },
    { to: '/admin/companies', label: 'Companies' },
    { to: '/admin/students', label: 'Students' },
    { to: '/admin/drives', label: 'Drives' },
    { to: '/admin/applications', label: 'Applications' }
  ],
  company: [{ to: '/company/dashboard', label: 'Dashboard' }],
  student: [{ to: '/student/dashboard', label: 'Dashboard' }]
}
</script>

<template>
  <nav class="navbar navbar-expand navbar-dark bg-dark px-3">
    <span class="navbar-brand">Placement Portal</span>
    <ul class="navbar-nav me-auto">
      <li v-for="l in links[auth.role] || []" :key="l.to" class="nav-item">
        <router-link class="nav-link" :to="l.to">{{ l.label }}</router-link>
      </li>
    </ul>
    <span class="navbar-text me-3 text-white">{{ auth.name }} ({{ auth.role }})</span>
    <button class="btn btn-outline-light btn-sm" @click="auth.logout()">Logout</button>
  </nav>
</template>