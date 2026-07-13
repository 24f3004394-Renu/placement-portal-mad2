<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const students = ref([])
const search = ref('')
const error = ref('')
const message = ref('')

async function load() {
  try { students.value = await api.get(`/api/admin/students?search=${encodeURIComponent(search.value)}`) }
  catch (e) { error.value = e.message }
}

async function blacklist(id) {
  error.value = ''; message.value = ''
  try {
    const res = await api.patch(`/api/admin/students/${id}/blacklist`)
    message.value = res.message
    await load()
  } catch (e) { error.value = e.message }
}

onMounted(load)
</script>

<template>
  <h2 class="mb-4">Students</h2>
  <AlertMessage :message="error" />
  <AlertMessage :message="message" type="success" />
  <form class="d-flex mb-3" @submit.prevent="load">
    <input v-model="search" class="form-control me-2" placeholder="Search by name, email, phone or ID">
    <button class="btn btn-outline-primary">Search</button>
  </form>
  <table class="table table-hover align-middle">
    <thead><tr><th>Name</th><th>Email</th><th>Branch</th><th>CGPA</th><th>Blacklisted</th><th>Actions</th></tr></thead>
    <tbody>
      <tr v-for="s in students" :key="s.id">
        <td><router-link :to="`/admin/students/${s.id}`">{{ s.name }}</router-link></td>
        <td>{{ s.email }}</td>
        <td>{{ s.branch || '—' }}</td>
        <td>{{ s.cgpa ?? '—' }}</td>
        <td>{{ s.is_blacklisted ? 'Yes' : 'No' }}</td>
        <td><button class="btn btn-sm btn-warning" @click="blacklist(s.id)">{{ s.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button></td>
      </tr>
      <tr v-if="!students.length"><td colspan="6" class="text-center text-muted">No students found.</td></tr>
    </tbody>
  </table>
</template>