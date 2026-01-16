<template>
    <div class="min-h-screen bg-dark-950 py-12">
        <div class="container-content">
            <h1 class="text-3xl font-bold text-dark-100 mb-8">Refunds Management</h1>

            <!-- Loading State -->
            <div v-if="loading" class="py-12">
                <LoadingSpinner size="lg" text="Loading refunds..." />
            </div>

            <!-- Refunds List -->
            <div v-else-if="refunds.length > 0" class="space-y-4">
                <BaseCard v-for="refund in refunds" :key="refund.id">
                    <div class="card-body">
                        <div class="flex justify-between items-start">
                            <div>
                                <div class="flex items-center space-x-3 mb-2">
                                    <span class="font-semibold text-dark-100">Refund #{{ refund.id }}</span>
                                    <BaseBadge :variant="getRefundStatusVariant(refund.status)">
                                        {{ refund.status }}
                                    </BaseBadge>
                                </div>
                                <p class="text-sm text-dark-400">
                                    Payment ID: {{ refund.payment }}
                                </p>
                                <p class="text-sm text-dark-400">
                                    Reason: {{ refund.reason || 'No reason provided' }}
                                </p>
                            </div>
                            <div class="text-right">
                                <p class="text-lg font-bold text-dark-100">
                                    ${{ formatCurrency(refund.amount) }}
                                </p>
                                <p class="text-sm text-dark-400">
                                    {{ formatDate(refund.created) }}
                                </p>
                            </div>
                        </div>
                    </div>
                </BaseCard>

                <!-- Pagination -->
                <div v-if="totalPages > 1" class="flex justify-center space-x-2 mt-8">
                    <BaseButton :disabled="currentPage === 1" @click="changePage(currentPage - 1)" variant="outline"
                        size="sm">
                        Previous
                    </BaseButton>
                    <span class="px-4 py-2 text-dark-300">
                        Page {{ currentPage }} of {{ totalPages }}
                    </span>
                    <BaseButton :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)"
                        variant="outline" size="sm">
                        Next
                    </BaseButton>
                </div>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-16 bg-dark-800 rounded-lg border border-dark-700">
                <div class="text-4xl mb-4">💸</div>
                <h3 class="text-xl font-semibold text-dark-100 mb-2">No refunds found</h3>
                <p class="text-dark-400">There are no refund records to display.</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { paymentsService, type Refund } from '@/services/payments'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const toast = useToast()
const loading = ref(true)
const refunds = ref<Refund[]>([])
const currentPage = ref(1)
const totalPages = ref(1)

const formatCurrency = (value?: string | number) => {
    return Number(value || 0).toFixed(2)
}

const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    })
}

const getRefundStatusVariant = (status?: string) => {
    switch (status) {
        case 'succeeded':
            return 'success'
        case 'pending':
            return 'warning'
        case 'failed':
            return 'error'
        default:
            return 'gray'
    }
}

const loadRefunds = async (page = 1) => {
    loading.value = true
    try {
        const data = await paymentsService.getRefunds({ page })
        refunds.value = data.results || []
        currentPage.value = page
        totalPages.value = Math.ceil((data.count || 0) / 20) // Assuming 20 per page
    } catch (error) {
        console.error('Failed to load refunds:', error)
        toast.error('Failed to load refunds')
    } finally {
        loading.value = false
    }
}

const changePage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
        loadRefunds(page)
    }
}

onMounted(() => {
    loadRefunds()
})
</script>
