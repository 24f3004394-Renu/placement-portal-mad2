<script setup>
import { computed } from 'vue'
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
  company: [
    { to: '/company/dashboard', label: 'Dashboard' },
    { to: '/company/drives/new', label: 'New Drive' },
    { to: '/company/profile', label: 'Profile' }
  ],
  student: [
    { to: '/student/dashboard', label: 'Dashboard' },
    { to: '/student/drives', label: 'Browse Drives' },
    { to: '/student/profile', label: 'Profile' }
  ]
}

const roleBadgeClass = computed(() => ({
  admin: 'badge-role-admin',
  company: 'badge-role-company',
  student: 'badge-role-student'
}[auth.role] || 'badge-role-student'))

const initial = computed(() => (auth.name || '?').charAt(0).toUpperCase())
</script>

<template>
  <nav class="app-navbar navbar navbar-expand px-4">
    <router-link class="navbar-brand d-flex align-items-center gap-2" :to="`/${auth.role}/dashboard`">
      <span class="brand-mark">PP</span>
      <span class="brand-text">Placement Portal</span>
    </router-link>

    <ul class="navbar-nav mx-auto gap-1">
      <li v-for="l in links[auth.role] || []" :key="l.to" class="nav-item">
        <router-link class="nav-link" active-class="nav-link-active" :to="l.to">
          {{ l.label }}
        </router-link>
      </li>
    </ul>

    <div class="d-flex align-items-center gap-3">
      <span class="role-badge" :class="roleBadgeClass">{{ auth.role }}</span>
      <div class="d-flex align-items-center gap-2">
        <span class="user-avatar">{{ initial }}</span>
        <span class="user-name d-none d-md-inline">{{ auth.name }}</span>
      </div>
      <button class="btn btn-sm logout-btn" @click="auth.logout()">Logout</button>
    </div>
  </nav>
</template>

<style scoped>
.app-navbar {
  height: 68px;
  background-color: #1E1408;
  border-bottom: 1px solid rgba(240, 192, 144, 0.15);
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #B05020, #D07840);
  color: #FFF6EC;
  font-weight: 700;
  font-size: 0.85rem;
}

.brand-text {
  color: #F5EDE0;
  font-weight: 600;
  font-size: 1.05rem;
}

.nav-link {
  color: #D0B090 !important;
  font-weight: 500;
  padding: 8px 14px !important;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.nav-link:hover {
  color: #F0C090 !important;
  background-color: rgba(240, 192, 144, 0.08);
}

.nav-link-active {
  color: #FFF6EC !important;
  background-color: rgba(176, 80, 32, 0.35) !important;
}

.role-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border-radius: 999px;
}

.badge-role-admin    { background-color: #4A1E00; color: #F0C090; }
.badge-role-company  { background-color: #D07840; color: #1E1408; }
.badge-role-student  { background-color: #5C7A5C; color: #FFF6EC; }

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #B05020;
  color: #FFF6EC;
  font-weight: 600;
  font-size: 0.8rem;
}

.user-name { color: #D0B090; font-size: 0.9rem; }

.logout-btn {
  color: #D0B090;
  border: 1px solid rgba(240, 192, 144, 0.25);
  background: transparent;
}
.logout-btn:hover {
  color: #F0C090;
  border-color: #F0C090;
  background-color: rgba(240, 192, 144, 0.08);
}
</style>