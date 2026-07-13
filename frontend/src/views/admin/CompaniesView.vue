<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const companies = ref([])
const search = ref('')
const error = ref('')
const message = ref('')

async function load() {
  try { companies.value = await api.get(`/api/admin/companies?search=${encodeURIComponent(search.value)}`) }
  catch (e) { error.value = e.message }
}

async function action(id, verb) {
  error.value = ''; message.value = ''
  try {
    const res = await api.patch(`/api/admin/companies/${id}/${verb}`)
    message.value = res.message
    await load()
  } catch (e) { error.value = e.message }
}

onMounted(load)
</script>

<template>
  <h2 class="mb-4">Companies</h2>
  <AlertMessage :message="error" />
  <AlertMessage :message="message" type="success" />
  <form class="d-flex mb-3" @submit.prevent="load">
    <input v-model="search" class="form-control me-2" placeholder="Search by name or industry">
    <button class="btn btn-outline-primary">Search</button>
  </form>
  <table class="table table-hover align-middle">
    <thead><tr><th>Name</th><th>Industry</th><th>Status</th><th>Blacklisted</th><th>Actions</th></tr></thead>
    <tbody>
      <tr v-for="c in companies" :key="c.id">
        <td>{{ c.name }}</td>
        <td>{{ c.industry || '—' }}</td>
        <td><span :class="`badge bg-${c.status === 'approved' ? 'success' : c.status === 'rejected' ? 'danger' : 'warning'}`">{{ c.status }}</span></td>
        <td>{{ c.is_blacklisted ? 'Yes' : 'No' }}</td>
        <td>
          <button v-if="c.status !== 'approved'" class="btn btn-sm btn-success me-1" @click="action(c.id, 'approve')">Approve</button>
          <button v-if="c.status !== 'rejected'" class="btn btn-sm btn-danger me-1" @click="action(c.id, 'reject')">Reject</button>
          <button class="btn btn-sm btn-warning" @click="action(c.id, 'blacklist')">{{ c.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
        </td>
      </tr>
      <tr v-if="!companies.length"><td colspan="5" class="text-center text-muted">No companies found.</td></tr>
    </tbody>
  </table>
</template>