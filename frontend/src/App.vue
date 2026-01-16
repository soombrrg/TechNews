<template>
  <div id="app" class="min-h-screen bg-dark-950">
    <!-- Header -->
    <AppHeader />

    <!-- Main content -->
    <main class="min-h-screen">
      <router-view v-slot="{ Component, route }">
        <transition :name="getTransitionName(route)" mode="out-in" appear>
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <AppFooter />

    <!-- Global loading overlay -->
    <div v-if="isGlobalLoading" class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
      <div class="bg-dark-800 rounded-lg p-6 flex items-center space-x-3 border border-dark-700">
        <div class="loading-spinner text-primary-500"></div>
        <span class="text-dark-100">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSubscriptionsStore } from '@/stores/subscriptions'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import type { RouteLocationNormalized } from 'vue-router'

const authStore = useAuthStore()
const subscriptionsStore = useSubscriptionsStore()
const isInitializing = ref(true)

const isGlobalLoading = computed(() => {
  return isInitializing.value && !authStore.isInitialized
})

const getTransitionName = (route: RouteLocationNormalized) => {
  if (route.meta?.transition) {
    return route.meta.transition as string
  }

  if (route.name === 'PostDetail') {
    return 'slide-up'
  }

  if (route.name === 'Login' || route.name === 'Register') {
    return 'fade'
  }

  return 'fade'
}

onMounted(async () => {
  try {
    await authStore.initializeAuth()

    // If user authenticated, fetch subscription status
    if (authStore.isAuthenticated) {
      subscriptionsStore.fetchSubscriptionStatus()
    }
  } catch (error) {
    console.error('App initialization error:', error)
  } finally {
    isInitializing.value = false
  }
})
</script>

<style scoped>
/* Page transitions are defined in main.css */
</style>
