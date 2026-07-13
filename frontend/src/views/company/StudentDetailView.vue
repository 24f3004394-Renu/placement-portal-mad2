<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api'

const route = useRoute()
const student = ref(null)
const error = ref('')

onMounted(async () => {
  try { student.value = await api.get(`/api/company/students/${route.params.id}`) }
  catch (e) { error.value = e.message }
})
</script>

<template>
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <div v-if="student">
    <h2 class="mb-3">{{ student.name }}</h2>
    <dl class="row">
      <dt class="col-sm-3">Email</dt><dd class="col-sm-9">{{ student.email }}</dd>
      <dt class="col-sm-3">Branch</dt><dd class="col-sm-9">{{ student.branch || '—' }}</dd>
      <dt class="col-sm-3">CGPA</dt><dd class="col-sm-9">{{ student.cgpa ?? '—' }}</dd>
    </dl>
  </div>
</template>