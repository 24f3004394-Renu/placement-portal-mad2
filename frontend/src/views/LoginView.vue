<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import AlertMessage from '../components/AlertMessage.vue'

const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try { await auth.login(email.value, password.value) }
  catch (e) { error.value = e.message }
  finally { loading.value = false }
}
</script>

<template>
  <div class="login-page d-flex align-items-center justify-content-center">
    <div class="login-card">
      <div class="text-center mb-4">
        <span class="brand-mark">PP</span>
        <h2 class="brand-title mt-3 mb-1">Welcome back</h2>
        <p class="brand-subtitle">Sign in to your Placement Portal account</p>
      </div>

      <AlertMessage :message="error" />

      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">Email <span class="text-muted small">(or admin username)</span></label>
          <input v-model="email" class="form-control" required autofocus>
        </div>
        <div class="mb-4">
          <label class="form-label">Password</label>
          <input v-model="password" type="password" class="form-control" required>
        </div>
        <button class="btn btn-primary w-100 py-2" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign In' }}
        </button>
      </form>

      <div class="divider"><span>New here?</span></div>

      <div class="d-flex gap-2">
        <router-link to="/register/student" class="register-choice flex-fill">
          
          <span>Register as Student</span>
        </router-link>
        <router-link to="/register/company" class="register-choice flex-fill">
          
          <span>Register as Company</span>
        </router-link>
      </div>
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