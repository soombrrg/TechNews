<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-content">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">Payment History</h1>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading payment history..." />
      </div>

      <!-- Payments List -->
      <div v-else-if="payments.length > 0">
        <div class="space-y-4">
          <div v-for="payment in payments" :key="payment.id" class="card">
            <div class="card-body">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h3 class="text-lg font-semibold text-dark-100">
                      {{ payment.subscription_info?.plan_name || 'Subscription Payment' }}
                    </h3>
                    <BaseBadge
                      :variant="(getStatusVariant(payment.status) as 'primary' | 'success' | 'warning' | 'error' | 'gray')">
                      {{ getStatusLabel(payment.status) }}
                    </BaseBadge>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span class="text-dark-500">Amount:</span>
                      <span class="text-dark-200 ml-2 font-medium">${{ payment.amount }}</span>
                    </div>
                    <div>
                      <span class="text-dark-500">Date:</span>
                      <span class="text-dark-200 ml-2">{{ formatDate(payment.created) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div v-if="payment.status === 'pending'" class="ml-4">
                  <button @click="handleRetry(payment.id)" class="btn btn-outline btn-sm"
                    :disabled="retrying === payment.id">
                    {{ retrying === payment.id ? 'Retrying...' : 'Retry Payment' }}
                  </button>
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
        <div class="text-6xl mb-4">💳</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No payment history</h3>
        <p class="text-dark-400 mb-6">Your payment transactions will appear here</p>
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
import paymentsService, { type Payment, type PaymentStatusEnum, type PaymentListQueryParams } from '@/services/payments'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'


const toast = useToast()
const loading = ref(false)
const retrying = ref<string | null>(null)
const currentPage = ref(1)
const payments = ref<Payment[]>([])
const pagination = ref({
  count: 0,
  next: null as string | null,
  previous: null as string | null,
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.count / 10)
})

const getStatusVariant = (status?: PaymentStatusEnum) => {
  const variants: Record<string, string> = {
    completed: 'success',
    pending: 'warning',
    failed: 'error',
    refunded: 'gray',
  }
  return status ? variants[status] || 'gray' : 'gray'
}

const getStatusLabel = (status?: PaymentStatusEnum) => {
  const labels: Record<string, string> = {
    completed: 'Completed',
    pending: 'Pending',
    failed: 'Failed',
    refunded: 'Refunded',
  }
  return status ? labels[status] || status : 'Unknown'
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const handleRetry = async (paymentId: string) => {
  retrying.value = paymentId
  try {
    await paymentsService.retryPayment(paymentId)
    toast.success('Payment retry initiated')
    await loadPayments()
  } catch (error) {
    console.error('Failed to retry payment:', error)
    toast.error('Failed to retry payment')
  } finally {
    retrying.value = null
  }
}

const loadPayments = async (page = 1, params: Omit<PaymentListQueryParams, 'page'> = {}) => {
  loading.value = true
  try {
    const data = await paymentsService.getPayments({ page, ...params })
    payments.value = data.results || []
    pagination.value = {
      count: data.count || 0,
      next: data.next,
      previous: data.previous,
    }
  } catch (error) {
    console.error('Failed to load payments:', error)
    toast.error('Failed to load payment history')
  } finally {
    loading.value = false
  }
}

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  await loadPayments(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  loadPayments()
})
</script>
