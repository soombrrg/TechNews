<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-950 px-4">
    <div class="max-w-md w-full text-center">
      <div class="mb-8">
        <div class="w-20 h-20 bg-error-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-error-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-dark-100 mb-2">Payment Cancelled</h1>
        <p class="text-dark-400">Your payment was cancelled. No charges were made.</p>
      </div>

      <div class="card mb-6">
        <div class="card-body">
          <p class="text-dark-300">
            If you experienced any issues during checkout, please try again or contact our support
            team.
          </p>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link to="/subscriptions" class="btn btn-primary"> Try Again </router-link>
        <router-link to="/" class="btn btn-outline"> Go to Home </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Template-only component
</script>
