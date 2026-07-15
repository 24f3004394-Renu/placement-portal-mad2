<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'
import ExportCsvButton from '../../components/ExportCsvButton.vue'

const drives = ref([])
const totalApplications = ref(0)
const error = ref('')
const message = ref('')
const blocked = ref(false)      
const blockedReason = ref('')

async function load() {
  blocked.value = false
  try {
    const data = await api.get('/api/company/dashboard')
    drives.value = data.drives
    totalApplications.value = data.total_applications
  } catch (e) {

    blocked.value = true
    blockedReason.value = e.message
  }
}

async function closeDrive(id) {
  error.value = ''; message.value = ''
  try {
    const res = await api.patch(`/api/company/drives/${id}/close`)
    message.value = res.message
    await load()
  } catch (e) { error.value = e.message }
}

onMounted(load)
</script>

<template>
  <div v-if="blocked" class="row justify-content-center">
    <div class="col-md-6 text-center mt-5">
      <h2 class="mb-3">Dashboard Unavailable</h2>
      <div class="alert alert-warning">{{ blockedReason }}</div>
      <p class="text-muted">
        Your company account needs admin approval before you can access the
        dashboard. You'll be able to sign in and view this page once approved —
        no further action is needed from you right now.
      </p>
    </div>
  </div>

  <div v-else>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Company Dashboard</h2>
      <span>
        <span class="badge text-bg-primary fs-6 me-2">Total applications: {{ totalApplications }}</span>
        <ExportCsvButton base="/api/company" />
      </span>
    </div>
    <AlertMessage :message="error" />
    <AlertMessage :message="message" type="success" />
    <router-link to="/company/drives/new" class="btn btn-primary mb-3">+ New Drive</router-link>
    <table class="table table-hover align-middle">
      <thead><tr><th>Title</th><th>CTC</th><th>Deadline</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-for="d in drives" :key="d.id">
          <td>{{ d.title }}</td>
          <td>{{ d.ctc ? '₹' + d.ctc.toLocaleString() : '—' }}</td>
          <td>{{ d.deadline || '—' }}</td>
          <td><span :class="`badge bg-${d.status === 'approved' ? 'success' : d.status === 'rejected' ? 'danger' : d.status === 'closed' ? 'secondary' : 'warning'}`">{{ d.status }}</span></td>
          <td>
            <router-link :to="`/company/drives/${d.id}/applicants`" class="btn btn-sm btn-info me-1">Applicants</router-link>
            <router-link :to="`/company/drives/${d.id}/edit`" class="btn btn-sm btn-outline-primary me-1">Edit</router-link>
            <button v-if="d.status === 'approved'" class="btn btn-sm btn-outline-secondary" @click="closeDrive(d.id)">Close</button>
          </td>
        </tr>
        <tr v-if="!drives.length"><td colspan="5" class="text-center text-muted">No drives yet.</td></tr>
      </tbody>
    </table>
  </div>
</template>