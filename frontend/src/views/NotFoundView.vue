<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-950 px-4">
    <div class="text-center max-w-md">
      <div class="mb-8">
        <h1 class="text-9xl font-bold text-primary-500">404</h1>
        <h2 class="text-3xl font-bold text-dark-100 mt-4 mb-2">Page Not Found</h2>
        <p class="text-dark-400">The page you're looking for doesn't exist or has been moved.</p>
      </div>

      <div class="flex justify-center space-x-4">
        <router-link to="/" class="btn btn-primary"> Go Home </router-link>
        <button @click="$router.back()" class="btn btn-outline">Go Back</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Template-only component
</script>
