<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../api.js'
import AlertMessage from '../../components/AlertMessage.vue'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const form = ref({ job_title: '', description: '', eligibility: '', min_cgpa: '', ctc: '', location: '', deadline: '', required_skills: '', experience: '' })
const error = ref('')

onMounted(async () => {
  if (!isEdit.value) return
  try {
    const data = await api.get('/api/company/dashboard')
    const d = data.drives.find(x => x.id === Number(route.params.id))
    if (!d) { error.value = 'Drive not found.'; return }
    form.value = {
      job_title: d.title, description: d.description || '', eligibility: d.eligibility_criteria || '',
      min_cgpa: d.min_cgpa ?? '', ctc: d.ctc ?? '', location: d.location || '',
      deadline: d.deadline || '', required_skills: d.required_skills || '', experience: d.experience || ''
    }
  } catch (e) { error.value = e.message }
})

async function submit() {
  error.value = ''
  try {
    if (isEdit.value) await api.put(`/api/company/drives/${route.params.id}`, form.value)
    else await api.post('/api/company/drives', form.value)
    router.push('/company/dashboard')
  } catch (e) { error.value = e.message }
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-8">
      <h2 class="mb-4">{{ isEdit ? 'Edit' : 'Create' }} Placement Drive</h2>
      <AlertMessage :message="error" />
      <form @submit.prevent="submit">
        <div class="row">
          <div class="col-md-6 mb-3"><label class="form-label">Job Title *</label><input v-model="form.job_title" class="form-control" required></div>
          <div class="col-md-6 mb-3"><label class="form-label">Location</label><input v-model="form.location" class="form-control"></div>
          <div class="col-12 mb-3"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="3"></textarea></div>
          <div class="col-12 mb-3"><label class="form-label">Eligibility Criteria</label><textarea v-model="form.eligibility" class="form-control" rows="2"></textarea></div>
          <div class="col-md-4 mb-3"><label class="form-label">Min CGPA</label><input v-model="form.min_cgpa" type="number" step="0.01" min="0" max="10" class="form-control"></div>
          <div class="col-md-4 mb-3"><label class="form-label">CTC (₹/yr)</label><input v-model="form.ctc" type="number" min="1" class="form-control"></div>
          <div class="col-md-4 mb-3"><label class="form-label">Deadline</label><input v-model="form.deadline" type="date" class="form-control"></div>
          <div class="col-md-6 mb-3"><label class="form-label">Required Skills</label><input v-model="form.required_skills" class="form-control"></div>
          <div class="col-md-6 mb-3"><label class="form-label">Experience</label><input v-model="form.experience" class="form-control"></div>
        </div>
        <button class="btn btn-primary">{{ isEdit ? 'Save Changes' : 'Create Drive' }}</button>
        <p class="text-muted mt-2 small">Note: creating/editing a drive resets it to "pending" until admin re-approves.</p>
      </form>
    </div>
  </div>
</template>