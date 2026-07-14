<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const route = useRoute()
const drive = ref(null)
const error = ref('')
const message = ref('')
const profileComplete = ref(true)

onMounted(async () => {
  try { drive.value = await api.get(`/api/student/drives/${route.params.id}`) }
  catch (e) { error.value = e.message }
  try {
    const p = await api.get('/api/student/profile')
    profileComplete.value = p.cgpa != null && p.resume != null
  } catch (e) { /* let apply() surface the real error if this check fails */ }
})

async function apply() {
  error.value = ''; message.value = ''
  try {
    const res = await api.post(`/api/student/drives/${drive.value.id}/apply`)
    message.value = res.message
    drive.value.already_applied = true
  } catch (e) { error.value = e.message }
}
</script>

<template>
  <AlertMessage :message="error" />
  <AlertMessage :message="message" type="success" />
  <div v-if="!profileComplete" class="alert alert-warning">
    Your profile is incomplete (CGPA and/or resume missing).
    <router-link to="/student/profile">Complete your profile</router-link> before applying.
  </div>
  <div v-if="drive">
    <h2>{{ drive.title }}</h2>
    <h5 class="text-muted mb-3">{{ drive.company_name }}</h5>
    <dl class="row">
      <dt class="col-sm-3">Description</dt><dd class="col-sm-9">{{ drive.description || '—' }}</dd>
      <dt class="col-sm-3">Eligibility</dt><dd class="col-sm-9">{{ drive.eligibility_criteria || '—' }}</dd>
      <dt class="col-sm-3">Required Skills</dt><dd class="col-sm-9">{{ drive.required_skills || '—' }}</dd>
      <dt class="col-sm-3">Min CGPA</dt><dd class="col-sm-9">{{ drive.min_cgpa ?? '—' }}</dd>
      <dt class="col-sm-3">CTC</dt><dd class="col-sm-9">{{ drive.ctc ? '₹' + drive.ctc.toLocaleString() : '—' }}</dd>
      <dt class="col-sm-3">Location</dt><dd class="col-sm-9">{{ drive.location || '—' }}</dd>
      <dt class="col-sm-3">Deadline</dt><dd class="col-sm-9">{{ drive.deadline || '—' }}</dd>
    </dl>
    <button v-if="!drive.already_applied" class="btn btn-primary" :disabled="!profileComplete" @click="apply">Apply</button>
    <span v-else class="badge bg-success fs-6">Applied ✓</span>
  </div>
</template>