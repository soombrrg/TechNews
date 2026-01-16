<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-narrow">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">My Subscription</h1>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading subscription..." />
      </div>

      <!-- Subscription Info -->
      <div v-else-if="subscription">
        <BaseCard>
          <div class="card-body">
            <!-- Status Badge -->
            <div class="mb-6">
              <BaseBadge :variant="subscription.is_active ? 'success' : 'gray'">
                {{ subscription.is_active ? 'Active' : 'Inactive' }}
              </BaseBadge>
            </div>

            <!-- Plan Details -->
            <div class="space-y-4 mb-8">
              <div>
                <label class="form-label">Plan</label>
                <p class="text-dark-100 text-lg font-semibold">
                  {{ subscription.plan_info?.name || 'N/A' }}
                </p>
              </div>

              <div v-if="subscription.start_date">
                <label class="form-label">Start Date</label>
                <p class="text-dark-100">{{ formatDate(subscription.start_date) }}</p>
              </div>

              <div v-if="subscription.end_date">
                <label class="form-label">End Date</label>
                <p class="text-dark-100">{{ formatDate(subscription.end_date) }}</p>
              </div>

            </div>

            <!-- Actions -->
            <div v-if="subscription.is_active" class="pt-6 border-t border-dark-700">
              <BaseButton variant="danger" @click="handleCancel" :loading="cancelling">
                Cancel Subscription
              </BaseButton>
            </div>
            <div v-else class="pt-6 border-t border-dark-700">
              <router-link to="/subscriptions" class="btn btn-primary"> View Plans </router-link>
            </div>
          </div>
        </BaseCard>

        <!-- Pinned Posts Management -->
        <div class="mt-8">
          <h2 class="text-2xl font-bold text-dark-100 mb-4">Pinned Posts</h2>

          <div v-if="pinnedPosts.length > 0" class="space-y-4">
            <BaseCard v-for="pinned in pinnedPosts" :key="pinned.id">
              <div class="card-body flex justify-between items-center">
                <div>
                  <h3 class="text-lg font-semibold text-dark-100">
                    <router-link :to="`/posts/${pinned.slug}`" class="hover:text-primary-500">
                      {{ pinned.title }}
                    </router-link>
                  </h3>
                  <p class="text-sm text-dark-400">
                    Pinned on {{ formatDate(pinned.pinned_at) }}
                  </p>
                </div>
                <BaseButton variant="danger" size="sm" @click="handleUnpin(pinned.slug)"
                  :loading="unpinning === pinned.slug">
                  Unpin
                </BaseButton>
              </div>
            </BaseCard>
          </div>

          <div v-else class="text-center py-8 bg-dark-800 rounded-lg border border-dark-700">
            <p class="text-dark-400">You haven't pinned any posts yet.</p>
            <p class="text-sm text-dark-500 mt-2">
              Pin your favorite posts to access them quickly.
            </p>
          </div>
        </div>

        <!-- Subscription History Link -->
        <div class="mt-6 text-center">
          <router-link to="/subscription-history" class="text-primary-500 hover:text-primary-400">
            View Subscription History →
          </router-link>
        </div>
      </div>

      <!-- No Subscription State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">💳</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No Active Subscription</h3>
        <p class="text-dark-400 mb-6">Subscribe to unlock premium features</p>
        <router-link to="/subscriptions" class="btn btn-primary"> View Plans </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { useSubscriptionsStore } from '@/stores/subscriptions'
import { usePostsStore } from '@/stores/posts'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import type { Subscription } from '@/services/subscriptions'


const toast = useToast()
const subscriptionsStore = useSubscriptionsStore()
const postsStore = usePostsStore()
const loading = ref(false)
const cancelling = ref(false)
const unpinning = ref<string | null>(null)
const subscription = computed<Subscription | null>(() => subscriptionsStore.currentSubscription)
const pinnedPosts = computed(() => subscriptionsStore.pinnedPosts)

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const handleCancel = async () => {
  if (!confirm('Are you sure you want to cancel your subscription?')) return

  cancelling.value = true
  try {
    const response = await subscriptionsStore.cancelSubscription()
    toast.success(response.msg || 'Subscription cancelled successfully')
    await loadSubscription()
  } catch (error: unknown) {
    console.error('Failed to cancel subscription:', error)
    const err = error as { response?: { data?: { error?: string } } }
    toast.error(err.response?.data?.error || 'Failed to cancel subscription')
  } finally {
    cancelling.value = false
  }
}

const loadSubscription = async () => {
  loading.value = true
  try {
    await Promise.all([
      subscriptionsStore.fetchMySubscription() || Promise.resolve(),
      subscriptionsStore.fetchPinnedPosts() || Promise.resolve(),
    ])
  } catch (error) {
    console.error('Failed to load subscription:', error)
  } finally {
    loading.value = false
  }
}

const handleUnpin = async (postSlug: string) => {
  if (!postSlug) return

  unpinning.value = postSlug
  try {
    await postsStore.togglePinStatus(postSlug)
    toast.success('Post unpinned successfully')
  } catch (error) {
    console.error('Failed to unpin post:', error)
    toast.error('Failed to unpin post')
  } finally {
    unpinning.value = null
  }
}

onMounted(() => {
  loadSubscription()
})
</script>
