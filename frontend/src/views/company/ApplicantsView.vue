<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const route = useRoute()
const drive = ref(null)
const applications = ref([])
const error = ref('')
const message = ref('')

const interviewFor = ref(null)
const interviewForm = ref({ scheduled_at: '', mode: 'online', notes: '' })
const interviewsByApp = ref({})
const feedbackDraft = ref({})

async function load() {
  try {
    const data = await api.get(`/api/company/drives/${route.params.id}/applicants`)
    drive.value = data.drive
    applications.value = data.applications
  } catch (e) { error.value = e.message }
}

async function setStatus(app, status) {
  error.value = ''; message.value = ''
  try {
    const res = await api.patch(`/api/company/applications/${app.id}`, { status })
    message.value = res.message
    await load()
  } catch (e) { error.value = e.message }
}

async function scheduleInterview() {
  error.value = ''; message.value = ''
  try {
    const res = await api.post(`/api/company/applications/${interviewFor.value.id}/interview`, interviewForm.value)
    message.value = res.message
    interviewFor.value = null
    interviewForm.value = { scheduled_at: '', mode: 'online', notes: '' }
  } catch (e) { error.value = e.message }
}

async function toggleInterviews(app) {
  if (interviewsByApp.value[app.id]) { delete interviewsByApp.value[app.id]; return }
  try { interviewsByApp.value[app.id] = await api.get(`/api/company/applications/${app.id}/interviews`) }
  catch (e) { error.value = e.message }
}

async function saveFeedback(interviewId, appId) {
  error.value = ''; message.value = ''
  try {
    const res = await api.patch(`/api/company/interviews/${interviewId}/feedback`, { feedback: feedbackDraft.value[interviewId] })
    message.value = res.message
    interviewsByApp.value[appId] = await api.get(`/api/company/applications/${appId}/interviews`)
  } catch (e) { error.value = e.message }
}

onMounted(load)
</script>

<template>
  <div v-if="drive">
    <h2 class="mb-1">Applicants — {{ drive.title }}</h2>
    <p class="text-muted">Status: {{ drive.status }} · Deadline: {{ drive.deadline || '—' }}</p>
  </div>
  <AlertMessage :message="error" />
  <AlertMessage :message="message" type="success" />

  <table class="table table-hover align-middle">
    <thead><tr><th>Student</th><th>CGPA</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
      <template v-for="a in applications" :key="a.id">
        <tr>
          <td><router-link :to="`/company/students/${a.student_id}`">{{ a.student_name }}</router-link></td>
          <td>{{ a.student_cgpa ?? '—' }}</td>
          <td><span class="badge bg-secondary">{{ a.status }}</span></td>
          <td>
            <select class="form-select form-select-sm d-inline w-auto me-2" :value="a.status" @change="e => setStatus(a, e.target.value)">
              <option value="applied">applied</option>
              <option value="shortlisted">shortlisted</option>
              <option value="rejected">rejected</option>
              <option value="selected">selected</option>
            </select>
            <button class="btn btn-sm btn-outline-primary me-1" @click="interviewFor = a">Schedule Interview</button>
            <button class="btn btn-sm btn-outline-secondary" @click="toggleInterviews(a)">
              {{ interviewsByApp[a.id] ? 'Hide' : 'Show' }} Interviews
            </button>
          </td>
        </tr>
        <tr v-if="interviewsByApp[a.id]">
          <td colspan="4" class="bg-light">
            <div v-if="!interviewsByApp[a.id].length" class="text-muted">No interviews scheduled.</div>
            <div v-for="iv in interviewsByApp[a.id]" :key="iv.id" class="border rounded p-2 mb-2">
              <strong>{{ iv.scheduled_at?.replace('T', ' ') }}</strong> · {{ iv.mode }}
              <span v-if="iv.notes"> · {{ iv.notes }}</span>
              <div class="mt-1">
                <em v-if="iv.feedback">Feedback: {{ iv.feedback }}</em>
                <div class="input-group input-group-sm mt-1" style="max-width: 480px">
                  <input v-model="feedbackDraft[iv.id]" class="form-control" placeholder="Add/update feedback">
                  <button class="btn btn-outline-primary" @click="saveFeedback(iv.id, a.id)">Save</button>
                </div>
              </div>
            </div>
          </td>
        </tr>
      </template>
      <tr v-if="!applications.length"><td colspan="4" class="text-center text-muted">No applicants yet.</td></tr>
    </tbody>
  </table>

  <div v-if="interviewFor" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
       style="background: rgba(0,0,0,.5); z-index: 1050">
    <div class="card p-4" style="min-width: 380px">
      <h5>Schedule interview — {{ interviewFor.student_name }}</h5>
      <div class="mb-2"><label class="form-label">Date &amp; time *</label><input v-model="interviewForm.scheduled_at" type="datetime-local" class="form-control"></div>
      <div class="mb-2">
        <label class="form-label">Mode *</label>
        <select v-model="interviewForm.mode" class="form-select">
          <option value="online">Online</option>
          <option value="in-person">In person</option>
          <option value="phone">Phone</option>
        </select>
      </div>
      <div class="mb-3"><label class="form-label">Notes</label><input v-model="interviewForm.notes" class="form-control"></div>
      <div class="d-flex gap-2">
        <button class="btn btn-primary" @click="scheduleInterview">Schedule</button>
        <button class="btn btn-secondary" @click="interviewFor = null">Cancel</button>
      </div>
    </div>
  </div>
</template>