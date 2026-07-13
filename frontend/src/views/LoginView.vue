<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import AlertMessage from '../components/AlertMessage.vue'

const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  try { await auth.login(email.value, password.value) }
  catch (e) { error.value = e.message }
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-5">
      <h2 class="mb-4">Login</h2>
      <AlertMessage :message="error" />
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">Email (or admin username)</label>
          <input v-model="email" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="password" type="password" class="form-control" required>
        </div>
        <button class="btn btn-primary w-100">Login</button>
      </form>
      <p class="mt-3 text-center">
        New here? Register as a
        <router-link to="/register/student">Student</router-link> or
        <router-link to="/register/company">Company</router-link>
      </p>
    </div>
  </div>
</template>