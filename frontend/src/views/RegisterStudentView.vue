<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AlertMessage from '../components/AlertMessage.vue'

const router = useRouter()
const form = ref({ name: '', email: '', password: '', phone: '' })
const error = ref('')

async function submit() {
  error.value = ''
  const res = await fetch('/api/auth/register/student', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  })
  const data = await res.json()
  if (!res.ok) { error.value = data.error || 'Registration failed.'; return }
  router.push('/login')
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-5">
      <h2 class="mb-4">Student Registration</h2>
      <AlertMessage :message="error" />
      <form @submit.prevent="submit">
        <div class="mb-3"><label class="form-label">Name *</label><input v-model="form.name" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">Email *</label><input v-model="form.email" type="email" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">Password *</label><input v-model="form.password" type="password" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">Phone *</label><input v-model="form.phone" class="form-control" required></div>
        <button class="btn btn-primary w-100">Register</button>
      </form>
      <p class="mt-3 text-center"><router-link to="/login">Back to login</router-link></p>
    </div>
  </div>
</template>