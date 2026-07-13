<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AlertMessage from '../components/AlertMessage.vue'

const router = useRouter()
const form = ref({ name: '', email: '', password: '', hr_contact: '' })
const error = ref('')
const success = ref('')

async function submit() {
  error.value = ''
  const res = await fetch('/api/auth/register/company', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  })
  const data = await res.json()
  if (!res.ok) { error.value = data.error || 'Registration failed.'; return }
  success.value = data.message
  setTimeout(() => router.push('/login'), 1200)
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-5">
      <h2 class="mb-4">Company Registration</h2>
      <AlertMessage :message="error" />
      <AlertMessage :message="success" type="success" />
      <form @submit.prevent="submit">
        <div class="mb-3"><label class="form-label">Company Name *</label><input v-model="form.name" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">Email *</label><input v-model="form.email" type="email" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">Password *</label><input v-model="form.password" type="password" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">HR Contact *</label><input v-model="form.hr_contact" class="form-control" required></div>
        <button class="btn btn-primary w-100">Register</button>
      </form>
      <p class="mt-3 text-center"><router-link to="/login">Back to login</router-link></p>
    </div>
  </div>
</template>