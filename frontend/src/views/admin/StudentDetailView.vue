<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api'

const route = useRoute()
const data = ref(null)
const error = ref('')

onMounted(async () => {
  try { data.value = await api.get(`/api/admin/students/${route.params.id}`) }
  catch (e) { error.value = e.message }
})
</script>

<template>
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <div v-if="data">
    <h2 class="mb-3">{{ data.student.name }}</h2>
    <dl class="row">
      <dt class="col-sm-3">Email</dt><dd class="col-sm-9">{{ data.student.email }}</dd>
      <dt class="col-sm-3">Phone</dt><dd class="col-sm-9">{{ data.student.phone }}</dd>
      <dt class="col-sm-3">Branch</dt><dd class="col-sm-9">{{ data.student.branch || '—' }}</dd>
      <dt class="col-sm-3">CGPA</dt><dd class="col-sm-9">{{ data.student.cgpa ?? '—' }}</dd>
    </dl>
    <h4 class="mt-4">Applications</h4>
    <table class="table">
      <thead><tr><th>Drive</th><th>Company</th><th>Status</th><th>Applied</th></tr></thead>
      <tbody>
        <tr v-for="a in data.applications" :key="a.id">
          <td>{{ a.drive_title }}</td><td>{{ a.company_name }}</td>
          <td><span class="badge bg-secondary">{{ a.status }}</span></td>
          <td>{{ a.applied_at?.slice(0, 10) }}</td>
        </tr>
        <tr v-if="!data.applications.length"><td colspan="4" class="text-center text-muted">No applications.</td></tr>
      </tbody>
    </table>
  </div>
</template>