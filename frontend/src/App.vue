<script setup>
import NavBar from './components/NavBar.vue'
import { useAuthStore } from './stores/auth'
const auth = useAuthStore()
</script>

<template>
  <NavBar v-if="auth.isLoggedIn" />
  <main class="container py-4">
    <router-view />
  </main>
</template>