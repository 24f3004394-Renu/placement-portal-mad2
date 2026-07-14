<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import { useAuthStore } from '../../stores/auth'
import AlertMessage from '../../components/AlertMessage.vue'
import ExportCsvButton from '../../components/ExportCsvButton.vue'

const auth = useAuthStore()
const applications = ref([])
const notifications = ref([])
const interviewsByApp = ref({})
const error = ref('')

async function load() {
  try {
    const data = await api.get('/api/student/dashboard')
    applications.value = data.applications
    notifications.value = data.notifications
  } catch (e) { error.value = e.message }
}

async function toggleInterviews(app) {
  if (interviewsByApp.value[app.id]) { delete interviewsByApp.value[app.id]; return }
  try { interviewsByApp.value[app.id] = await api.get(`/api/student/applications/${app.id}/interview`) }
  catch (e) { error.value = e.message }
}

async function openOfferLetter(app) {
  error.value = ''
  try {
    const res = await fetch(`/api/student/placements/${app.placement_id}/offer-letter`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.error || 'Could not load offer letter.')
    }
    const html = await res.text()
    const win = window.open('', '_blank')
    win.document.write(html)
    win.document.close()
  } catch (e) { error.value = e.message }
}

const badgeColor = (s) => ({ applied: 'secondary', shortlisted: 'info', rejected: 'danger', selected: 'success' }[s] || 'secondary')

onMounted(load)
</script>

<template>
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h2>My Applications</h2>
    <ExportCsvButton base="/api/student" />
  </div>
  <AlertMessage :message="error" />

  <div v-if="notifications.length" class="alert alert-info">
    <strong>Updates:</strong>
    <ul class="mb-0">
      <li v-for="n in notifications" :key="n.id">
        {{ n.drive_title }} ({{ n.company_name }}) — status changed to <strong>{{ n.status }}</strong>
      </li>
    </ul>
  </div>

  <table class="table table-hover align-middle">
    <thead><tr><th>Drive</th><th>Company</th><th>Status</th><th>Applied</th><th>Actions</th></tr></thead>
    <tbody>
      <template v-for="a in applications" :key="a.id">
        <tr>
          <td>{{ a.drive_title }}</td>
          <td>{{ a.company_name }}</td>
          <td><span :class="`badge bg-${badgeColor(a.status)}`">{{ a.status }}</span></td>
          <td>{{ a.applied_at?.slice(0, 10) }}</td>
          <td>
            <button class="btn btn-sm btn-outline-secondary me-1" @click="toggleInterviews(a)">
              {{ interviewsByApp[a.id] ? 'Hide' : 'Show' }} Interviews
            </button>
            <button v-if="a.status === 'selected' && a.placement_id" class="btn btn-sm btn-success" @click="openOfferLetter(a)">
              Offer Letter
            </button>
          </td>
        </tr>
        <tr v-if="interviewsByApp[a.id]">
          <td colspan="5" class="bg-light">
            <div v-if="!interviewsByApp[a.id].length" class="text-muted">No interviews scheduled yet.</div>
            <div v-for="iv in interviewsByApp[a.id]" :key="iv.id" class="border rounded p-2 mb-2">
              <strong>{{ iv.scheduled_at?.replace('T', ' ') }}</strong> · {{ iv.mode }}
              <span v-if="iv.notes"> · {{ iv.notes }}</span>
              <div v-if="iv.feedback" class="mt-1"><em>Feedback: {{ iv.feedback }}</em></div>
            </div>
          </td>
        </tr>
      </template>
      <tr v-if="!applications.length"><td colspan="5" class="text-center text-muted">
        You haven't applied to any drives yet. <router-link to="/student/drives">Browse drives</router-link>.
      </td></tr>
    </tbody>
  </table>
</template>