<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-content">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">Subscription History</h1>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading subscription history..." />
      </div>

      <!-- History List -->
      <div v-else-if="history.length > 0">
        <div class="space-y-4">
          <div v-for="item in history" :key="item.id" class="card">
            <div class="card-body">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-3">
                    <h3 class="text-lg font-semibold text-dark-100">
                      {{ getActionLabel(item.action) }}
                    </h3>
                    <BaseBadge
                      :variant="(getActionVariant(item.action) as 'primary' | 'success' | 'warning' | 'error' | 'gray')">
                      {{ item.action }}
                    </BaseBadge>
                  </div>

                  <div class="space-y-2 text-sm">
                    <div v-if="item.description">
                      <span class="text-dark-400">{{ item.description }}</span>
                    </div>
                    <div>
                      <span class="text-dark-500">Date:</span>
                      <span class="text-dark-200 ml-2">{{ formatDate(item.created) }}</span>
                    </div>
                    <div v-if="item.metadata && Object.keys(item.metadata).length > 0" class="mt-2">
                      <span class="text-dark-500">Details:</span>
                      <div class="text-dark-300 ml-2 space-y-1">
                        <div v-for="(value, key) in item.metadata" :key="String(key)">
                          <span class="capitalize">{{ String(key).replace(/_/g, ' ') }}:</span> {{ value }}
                        </div>
                      </div>
                    </div>
                  </div>


                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.count > 10" class="flex justify-center items-center space-x-4 mt-8">
          <button :disabled="!pagination.previous" @click="goToPage(currentPage - 1)" class="btn btn-outline btn-sm">
            Previous
          </button>
          <span class="text-dark-300"> Page {{ currentPage }} of {{ totalPages }} </span>
          <button :disabled="!pagination.next" @click="goToPage(currentPage + 1)" class="btn btn-outline btn-sm">
            Next
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">📜</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No subscription history</h3>
        <p class="text-dark-400 mb-6">Your subscription history will appear here</p>
        <router-link to="/subscriptions" class="btn btn-primary">
          View Subscription Plans
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { type SubscriptionHistory, type SubscriptionHistoryQueryParams, type SubscriptionHistoryActionEnum } from '@/services/subscriptions'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { useSubscriptionsStore } from '@/stores/subscriptions'

const subscriptionsStore = useSubscriptionsStore()
const toast = useToast()
const loading = ref(false)
const currentPage = ref(1)
const history = computed<SubscriptionHistory[]>(() => subscriptionsStore.history || [])


const pagination = ref({
  count: 0,
  next: null as string | null,
  previous: null as string | null,
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.count / 10)
})

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const getActionVariant = (action?: SubscriptionHistoryActionEnum) => {
  const variants: Record<string, string> = {
    created: 'success',
    activated: 'success',
    renewed: 'primary',
    cancelled: 'warning',
    expired: 'gray',
    failed: 'error',
  }
  return action ? variants[action] || 'gray' : 'gray'
}

const getActionLabel = (action?: SubscriptionHistoryActionEnum) => {
  const labels: Record<string, string> = {
    created: 'Subscription Created',
    activated: 'Subscription Activated',
    renewed: 'Subscription Renewed',
    cancelled: 'Subscription Cancelled',
    expired: 'Subscription Expired',
    failed: 'Subscription Failed',
  }
  return action ? labels[action] || action : 'Unknown'
}

const loadHistory = async (page = 1, params: SubscriptionHistoryQueryParams = {}) => {
  loading.value = true
  try {
    const data = await subscriptionsStore.fetchSubscriptionHistory({ page, ...params })
    pagination.value = {
      count: data.count || 0,
      next: data.next,
      previous: data.previous,
    }
  } catch (error) {
    console.error('Failed to load subscription history:', error)
    toast.error('Failed to load subscription history')
  } finally {
    loading.value = false
  }
}

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  await loadHistory(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  loadHistory()
})
</script>
