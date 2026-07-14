<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const form = ref({ name: '', phone: '', degree: '', branch: '', cgpa: '', grad_year: '', skills: '' })
const email = ref('')
const currentResume = ref(null)
const resume = ref(null)
const error = ref('')
const message = ref('')

onMounted(async () => {
  try {
    const p = await api.get('/api/student/profile')
    email.value = p.email
    currentResume.value = p.resume
    form.value = {
      name: p.name, phone: p.phone, degree: p.degree || '', branch: p.branch || '',
      cgpa: p.cgpa ?? '', grad_year: p.grad_year ?? '', skills: p.skills || ''
    }
  } catch (e) { error.value = e.message }
})

async function submit() {
  error.value = ''; message.value = ''
  try {
    const fd = new FormData()
    Object.entries(form.value).forEach(([k, v]) => { if (v !== '' && v != null) fd.append(k, v) })
    if (resume.value) fd.append('resume', resume.value)
    const res = await api.put('/api/student/profile', fd)
    message.value = res.message
  } catch (e) { error.value = e.message }
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h2 class="mb-4">My Profile</h2>
      <AlertMessage :message="error" />
      <AlertMessage :message="message" type="success" />
      <p class="text-muted">Email: {{ email }}</p>
      <form @submit.prevent="submit">
        <div class="row">
          <div class="col-md-6 mb-3"><label class="form-label">Name *</label><input v-model="form.name" class="form-control" required></div>
          <div class="col-md-6 mb-3"><label class="form-label">Phone *</label><input v-model="form.phone" class="form-control" required></div>
          <div class="col-md-6 mb-3"><label class="form-label">Degree</label><input v-model="form.degree" class="form-control"></div>
          <div class="col-md-6 mb-3"><label class="form-label">Branch</label><input v-model="form.branch" class="form-control"></div>
          <div class="col-md-6 mb-3"><label class="form-label">CGPA</label><input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control"></div>
          <div class="col-md-6 mb-3"><label class="form-label">Graduation Year</label><input v-model="form.grad_year" type="number" class="form-control"></div>
          <div class="col-12 mb-3"><label class="form-label">Skills</label><input v-model="form.skills" class="form-control"></div>
          <div class="col-12 mb-3">
            <label class="form-label">Resume (PDF)</label>
            <input type="file" accept=".pdf" class="form-control" @change="e => resume = e.target.files[0]">
            <small v-if="currentResume" class="text-muted">Current: <a :href="'/' + currentResume" target="_blank">view</a></small>
          </div>
        </div>
        <button class="btn btn-primary">Save Profile</button>
      </form>
    </div>
  </div>
</template>