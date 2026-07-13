<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'

const applications = ref([])
const error = ref('')

onMounted(async () => {
  try { applications.value = await api.get('/api/admin/applications') }
  catch (e) { error.value = e.message }
})
</script>

<template>
  <h2 class="mb-4">All Applications</h2>
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <table class="table table-hover">
    <thead><tr><th>Student</th><th>Drive</th><th>Company</th><th>Status</th><th>Applied</th></tr></thead>
    <tbody>
      <tr v-for="a in applications" :key="a.id">
        <td>{{ a.student_name }}</td>
        <td>{{ a.drive_title }}</td>
        <td>{{ a.company_name }}</td>
        <td><span class="badge bg-secondary">{{ a.status }}</span></td>
        <td>{{ a.applied_at?.slice(0, 10) }}</td>
      </tr>
      <tr v-if="!applications.length"><td colspan="5" class="text-center text-muted">No applications.</td></tr>
    </tbody>
  </table>
</template>