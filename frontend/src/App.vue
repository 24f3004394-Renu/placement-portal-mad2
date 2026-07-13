<script setup>
import { useAuthStore } from './stores/auth'
const auth = useAuthStore()
</script>

<template>
  <nav v-if="auth.isLoggedIn" class="navbar navbar-dark bg-dark px-3">
    <span class="navbar-text text-white">{{ auth.name }} ({{ auth.role }})</span>
    <button class="btn btn-outline-light btn-sm ms-auto" @click="auth.logout()">Logout</button>
  </nav>
  <main class="container py-4">
    <router-view />
  </main>
</template>