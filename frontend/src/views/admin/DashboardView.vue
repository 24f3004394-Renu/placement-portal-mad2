<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'

const stats = ref(null)
const error = ref('')

onMounted(async () => {
  try { stats.value = await api.get('/api/admin/dashboard') }
  catch (e) { error.value = e.message }
})

const cards = [
  ['total_students', 'Students', 'primary'],
  ['total_companies', 'Companies', 'success'],
  ['total_drives', 'Drives', 'info'],
  ['total_applications', 'Applications', 'secondary'],
  ['pending_companies', 'Pending Companies', 'warning'],
  ['pending_drives', 'Pending Drives', 'danger']
]
</script>

<template>
  <h2 class="mb-4">Admin Dashboard</h2>
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <div v-if="stats" class="row g-3">
    <div v-for="[key, label, color] in cards" :key="key" class="col-md-4 col-6">
      <div :class="`card text-bg-${color}`">
        <div class="card-body text-center">
          <div class="fs-2 fw-bold">{{ stats[key] }}</div>
          <div>{{ label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>