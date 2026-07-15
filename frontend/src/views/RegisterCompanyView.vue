<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AlertMessage from '../components/AlertMessage.vue'

const router = useRouter()
const form = ref({ name: '', email: '', password: '', hr_contact: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/register/company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    const data = await res.json()
    if (!res.ok) { error.value = data.error || 'Registration failed.'; return }
    success.value = data.message
    setTimeout(() => router.push('/login'), 1200)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page d-flex align-items-center justify-content-center">
    <div class="login-card">
      <div class="text-center mb-4">
        
        <h2 class="brand-title mt-3 mb-1">Company Registration</h2>
        <p class="brand-subtitle">Register to start posting placement drives</p>
      </div>

      <AlertMessage :message="error" />
      <AlertMessage :message="success" type="success" />

      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">Company Name *</label>
          <input v-model="form.name" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Email *</label>
          <input v-model="form.email" type="email" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Password *</label>
          <input v-model="form.password" type="password" class="form-control" required>
        </div>
        <div class="mb-4">
          <label class="form-label">HR Contact *</label>
          <input v-model="form.hr_contact" class="form-control" required>
        </div>
        <button class="btn btn-primary w-100 py-2" :disabled="loading">
          {{ loading ? 'Registering…' : 'Register' }}
        </button>
      </form>

      <p class="mt-4 text-center back-link">
        <router-link to="/login">← Back to login</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: calc(100vh - 68px);
  background: linear-gradient(160deg, #F5EDE0 0%, #E8D8C0 100%);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #FFF6EC;
  border-radius: 16px;
  padding: 40px 36px;
  box-shadow: 0 4px 24px rgba(16, 10, 4, 0.10);
  border: 1px solid #D0B090;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #B05020, #D07840);
  color: #FFF6EC;
  font-weight: 700;
  font-size: 1.1rem;
}

.brand-title { color: #100A04; font-weight: 700; font-size: 1.5rem; }
.brand-subtitle { color: #504030; font-size: 0.9rem; margin-bottom: 0; }

.form-label { font-weight: 500; color: #302010; font-size: 0.9rem; }

.form-control { border-color: #D0B090; padding: 10px 14px; }
.form-control:focus {
  border-color: #B05020;
  box-shadow: 0 0 0 3px rgba(176, 80, 32, 0.12);
}

.btn-primary {
  background-color: #B05020;
  border-color: #B05020;
  font-weight: 600;
  border-radius: 8px;
}
.btn-primary:hover { background-color: #7A3010; border-color: #7A3010; }

.divider { display: flex; align-items: center; text-align: center; margin: 24px 0 16px; color: #907060; font-size: 0.8rem; }
.divider::before, .divider::after { content: ''; flex: 1; border-bottom: 1px solid #D0B090; }
.divider span { padding: 0 12px; }

.register-choice {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px 8px; border: 1px solid #D0B090; border-radius: 10px;
  text-decoration: none; color: #302010; font-size: 0.85rem; font-weight: 500;
  transition: all 0.15s ease;
}
.register-choice:hover { border-color: #B05020; background-color: #F0C090; color: #4A1E00; }
.register-icon { font-size: 1.4rem; }

.back-link a { color: #504030; text-decoration: none; font-size: 0.9rem; }
.back-link a:hover { color: #B05020; }
</style>