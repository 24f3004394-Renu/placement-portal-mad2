<script setup>
import { ref, onUnmounted } from 'vue'
import { api } from '../api'

const props = defineProps({ base: String })  
const state = ref('idle')  
const fileUrl = ref('')
const rowCount = ref(0)
const error = ref('')
let timer = null

async function start() {
  state.value = 'running'; error.value = ''; fileUrl.value = ''
  try {
    const res = await api.post(`${props.base}/export`)
    poll(res.task_id)
  } catch (e) { state.value = 'error'; error.value = e.message }
}

function poll(taskId) {
  timer = setInterval(async () => {
    try {
      const s = await api.get(`${props.base}/export/status/${taskId}`)
      if (s.state === 'SUCCESS') {
        clearInterval(timer)
        fileUrl.value = '/' + s.file
        rowCount.value = s.row_count
        state.value = 'done'
      } else if (s.state === 'FAILURE') {
        clearInterval(timer)
        state.value = 'error'; error.value = 'Export failed.'
      }
    } catch (e) {
      clearInterval(timer)
      state.value = 'error'; error.value = e.message
    }
  }, 1000)
}

onUnmounted(() => timer && clearInterval(timer))
</script>

<template>
  <span>
    <button class="btn btn-sm btn-outline-success" :disabled="state === 'running'" @click="start">
      {{ state === 'running' ? 'Exporting…' : 'Export CSV' }}
    </button>
    <a v-if="state === 'done'" :href="fileUrl" class="btn btn-sm btn-success ms-2" download>
      Download ({{ rowCount }} rows)
    </a>
    <span v-if="state === 'error'" class="text-danger ms-2 small">{{ error }}</span>
  </span>
</template>