<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const drives = ref([])
const error = ref('')
const message = ref('')

async function load() {
  try { drives.value = await api.get('/api/admin/drives') }
  catch (e) { error.value = e.message }
}

async function action(id, verb) {
  error.value = ''; message.value = ''
  try {
    const res = await api.patch(`/api/admin/drives/${id}/${verb}`)
    message.value = res.message
    await load()
  } catch (e) { error.value = e.message }
}

onMounted(load)
</script>

<template>
  <h2 class="mb-4">Placement Drives</h2>
  <AlertMessage :message="error" />
  <AlertMessage :message="message" type="success" />
  <table class="table table-hover align-middle">
    <thead><tr><th>Title</th><th>Company</th><th>CTC</th><th>Deadline</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
      <tr v-for="d in drives" :key="d.id">
        <td>{{ d.title }}</td>
        <td>{{ d.company_name }}</td>
        <td>{{ d.ctc ? '₹' + d.ctc.toLocaleString() : '—' }}</td>
        <td>{{ d.deadline || '—' }}</td>
        <td><span :class="`badge bg-${d.status === 'approved' ? 'success' : d.status === 'rejected' ? 'danger' : 'warning'}`">{{ d.status }}</span></td>
        <td>
          <button v-if="d.status === 'pending'" class="btn btn-sm btn-success me-1" @click="action(d.id, 'approve')">Approve</button>
          <button v-if="d.status === 'pending'" class="btn btn-sm btn-danger" @click="action(d.id, 'reject')">Reject</button>
        </td>
      </tr>
      <tr v-if="!drives.length"><td colspan="6" class="text-center text-muted">No drives.</td></tr>
    </tbody>
  </table>
</template>