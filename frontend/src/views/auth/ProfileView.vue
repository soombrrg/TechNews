<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-narrow">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">My Profile</h1>

      <BaseCard>
        <div class="card-body">
          <div v-if="loading" class="text-center py-8">
            <LoadingSpinner />
          </div>

          <div v-else-if="authStore.user">
            <!-- Avatar and Header -->
            <div class="flex items-start space-x-6 mb-8 pb-8 border-b border-dark-700">
              <div class="flex-shrink-0">
                <div v-if="authStore.user.avatar"
                  class="w-24 h-24 rounded-full overflow-hidden border-2 border-primary-500">
                  <img :src="authStore.user.avatar" :alt="authStore.user.username" class="w-full h-full object-cover" />
                </div>
                <div v-else
                  class="w-24 h-24 rounded-full bg-primary-500 flex items-center justify-center border-2 border-primary-600">
                  <span class="text-4xl font-bold text-dark-900">
                    {{ authStore.user.username.charAt(0).toUpperCase() }}
                  </span>
                </div>
              </div>
              <div class="flex-1">
                <h2 class="text-2xl font-bold text-dark-100 mb-1">{{ authStore.user.full_name || authStore.user.username
                  }}</h2>
                <p class="text-dark-400 mb-4">@{{ authStore.user.username }}</p>

                <!-- User Stats -->
                <div class="flex space-x-6 text-sm">
                  <div>
                    <span class="text-dark-500">Posts:</span>
                    <span class="text-primary-500 font-semibold ml-1">{{ authStore.user.posts_count || 0 }}</span>
                  </div>
                  <div>
                    <span class="text-dark-500">Comments:</span>
                    <span class="text-primary-500 font-semibold ml-1">{{ authStore.user.comments_count || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bio Section -->
            <div v-if="authStore.user.bio" class="mb-8 pb-8 border-b border-dark-700">
              <label class="form-label">Bio</label>
              <p class="text-dark-200 whitespace-pre-wrap">{{ authStore.user.bio }}</p>
            </div>

            <!-- Profile Details -->
            <div class="space-y-4 mb-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="form-label">Username</label>
                  <p class="text-dark-100">{{ authStore.user.username }}</p>
                </div>

                <div>
                  <label class="form-label">Email</label>
                  <p class="text-dark-100">{{ authStore.user.email }}</p>
                </div>

                <div v-if="authStore.user.first_name">
                  <label class="form-label">First Name</label>
                  <p class="text-dark-100">{{ authStore.user.first_name }}</p>
                </div>

                <div v-if="authStore.user.last_name">
                  <label class="form-label">Last Name</label>
                  <p class="text-dark-100">{{ authStore.user.last_name }}</p>
                </div>

                <div>
                  <label class="form-label">Member Since</label>
                  <p class="text-dark-100">{{ formatDate(authStore.user.created) }}</p>
                </div>

                <div v-if="authStore.user.modified">
                  <label class="form-label">Last Updated</label>
                  <p class="text-dark-100">{{ formatDate(authStore.user.modified) }}</p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex flex-wrap gap-4">
              <router-link to="/change-password" class="btn btn-outline">
                Change Password
              </router-link>
              <router-link to="/my-posts" class="btn btn-outline">
                My Posts ({{ authStore.user.posts_count || 0 }})
              </router-link>
              <router-link to="/my-comments" class="btn btn-outline">
                My Comments ({{ authStore.user.comments_count || 0 }})
              </router-link>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BaseCard from '@/components/ui/BaseCard.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const authStore = useAuthStore()
const loading = ref(false)

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(async () => {
  if (!authStore.user) {
    loading.value = true
    try {
      await authStore.fetchProfile()
    } catch (error) {
      console.error('Failed to fetch profile:', error)
    } finally {
      loading.value = false
    }
  }
})
</script>
