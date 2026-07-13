import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('../views/LoginView.vue') },
  { path: '/register/student', component: () => import('../views/RegisterStudentView.vue') },
  { path: '/register/company', component: () => import('../views/RegisterCompanyView.vue') },
 

  { path: '/admin/dashboard', component: () => import('../views/admin/DashboardView.vue'), meta: { role: 'admin' } },
  { path: '/admin/companies', component: () => import('../views/admin/CompaniesView.vue'), meta: { role: 'admin' } },
  { path: '/admin/students', component: () => import('../views/admin/StudentsView.vue'), meta: { role: 'admin' } },
  { path: '/admin/students/:id', component: () => import('../views/admin/StudentDetailView.vue'), meta: { role: 'admin' } },
  { path: '/admin/drives', component: () => import('../views/admin/DrivesView.vue'), meta: { role: 'admin' } },
  { path: '/admin/applications', component: () => import('../views/admin/ApplicationsView.vue'), meta: { role: 'admin' } },
  { path: '/company/dashboard', component: () => import('../views/company/DashboardView.vue'), meta: { role: 'company' } },
  { path: '/student/dashboard', component: () => import('../views/student/DashboardView.vue'), meta: { role: 'student' } }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.role) {
    if (!auth.isLoggedIn) return '/login'
    if (auth.role !== to.meta.role) return `/${auth.role}/dashboard`
  }
  if (!to.meta.role && auth.isLoggedIn && (to.path === '/login' || to.path.startsWith('/register'))) {
    return `/${auth.role}/dashboard`
  }
  return true
})

export default router