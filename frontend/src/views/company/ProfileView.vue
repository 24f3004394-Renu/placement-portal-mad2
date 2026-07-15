<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const form = ref({ hr_contact: '', website: '', industry: '', description: '' })
const name = ref('')
const email = ref('')
const error = ref('')
const message = ref('')

onMounted(async () => {
  try {
    const p = await api.get('/api/company/profile')
    name.value = p.name
    email.value = p.email
    form.value = {
      hr_contact: p.hr_contact || '', website: p.website || '',
      industry: p.industry || '', description: p.description || ''
    }
  } catch (e) { error.value = e.message }
})

async function submit() {
  error.value = ''; message.value = ''
  try {
    const res = await api.put('/api/company/profile', form.value)
    message.value = res.message
  } catch (e) { error.value = e.message }
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h2 class="mb-4">Company Profile</h2>
      <AlertMessage :message="error" />
      <AlertMessage :message="message" type="success" />
      <p class="text-muted">{{ name }} · {{ email }}</p>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">HR Contact *</label>
          <input v-model="form.hr_contact" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Website</label>
          <input v-model="form.website" class="form-control" placeholder="https://example.com">
        </div>
        <div class="mb-3">
          <label class="form-label">Industry</label>
          <input v-model="form.industry" class="form-control" placeholder="e.g. Tech, Finance, Manufacturing">
        </div>
        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea v-model="form.description" class="form-control" rows="4"></textarea>
        </div>
        <button class="btn btn-primary">Save Profile</button>
      </form>
    </div>
  </div>
</template>