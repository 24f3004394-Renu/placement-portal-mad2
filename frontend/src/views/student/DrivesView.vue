<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import AlertMessage from '../../components/AlertMessage.vue'

const drives = ref([])
const search = ref('')
const error = ref('')
const message = ref('')

async function load() {
  try { drives.value = await api.get(`/api/student/drives?search=${encodeURIComponent(search.value)}`) }
  catch (e) { error.value = e.message }
}

async function apply(id) {
  error.value = ''; message.value = ''
  try {
    const res = await api.post(`/api/student/drives/${id}/apply`)
    message.value = res.message
    await load()
  } catch (e) { error.value = e.message }
}

onMounted(load)
</script>

<template>
  <h2 class="mb-4">Open Placement Drives</h2>
  <AlertMessage :message="error" />
  <AlertMessage :message="message" type="success" />
  <form class="d-flex mb-3" @submit.prevent="load">
    <input v-model="search" class="form-control me-2" placeholder="Search by title, skills, location or company">
    <button class="btn btn-outline-primary">Search</button>
  </form>
  <div class="row g-3">
    <div v-for="d in drives" :key="d.id" class="col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h5 class="card-title">{{ d.title }}</h5>
          <h6 class="card-subtitle text-muted mb-2">{{ d.company_name }}</h6>
          <p class="card-text mb-1"><strong>CTC:</strong> {{ d.ctc ? '₹' + d.ctc.toLocaleString() : '—' }}</p>
          <p class="card-text mb-1"><strong>Location:</strong> {{ d.location || '—' }}</p>
          <p class="card-text mb-1"><strong>Min CGPA:</strong> {{ d.min_cgpa ?? '—' }}</p>
          <p class="card-text mb-2"><strong>Deadline:</strong> {{ d.deadline || '—' }}</p>
          <router-link :to="`/student/drives/${d.id}`" class="btn btn-sm btn-outline-secondary me-2">Details</router-link>
          <button v-if="!d.already_applied" class="btn btn-sm btn-primary" @click="apply(d.id)">Apply</button>
          <span v-else class="badge bg-success align-middle">Applied ✓</span>
        </div>
      </div>
    </div>
    <p v-if="!drives.length" class="text-center text-muted">No open drives found.</p>
  </div>
</template>