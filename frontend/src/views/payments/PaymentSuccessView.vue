<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-950 px-4">
    <div class="max-w-md w-full text-center">
      <div class="mb-8">
        <div class="w-20 h-20 bg-success-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-dark-100 mb-2">Payment Successful!</h1>
        <p class="text-dark-400">Your subscription has been activated successfully.</p>
      </div>

      <div class="card mb-6">
        <div class="card-body">
          <p class="text-dark-300 mb-4">
            Thank you for subscribing! You now have access to all premium features.
          </p>
          <div class="space-y-2 text-sm text-dark-400">
            <div class="flex items-center justify-center space-x-2">
              <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span>Pin your posts</span>
            </div>
            <div class="flex items-center justify-center space-x-2">
              <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span>Priority support</span>
            </div>
            <div class="flex items-center justify-center space-x-2">
              <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span>Exclusive features</span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link to="/my-subscription" class="btn btn-primary">
          View My Subscription
        </router-link>
        <router-link to="/" class="btn btn-outline"> Go to Home </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Template-only component
</script>
