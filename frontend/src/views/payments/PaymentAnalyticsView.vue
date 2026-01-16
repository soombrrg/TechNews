<template>
    <div class="min-h-screen bg-dark-950 py-12">
        <div class="container-content">
            <h1 class="text-3xl font-bold text-dark-100 mb-8">Payment Analytics</h1>

            <!-- Loading State -->
            <div v-if="loading" class="py-12">
                <LoadingSpinner size="lg" text="Loading analytics..." />
            </div>

            <!-- Analytics Content -->
            <div v-else-if="analytics" class="space-y-8">
                <!-- Key Metrics -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <BaseCard>
                        <div class="card-body text-center">
                            <p class="text-dark-400 mb-2">Total Revenue</p>
                            <p class="text-3xl font-bold text-primary-500">
                                ${{ formatCurrency(analytics.total_revenue) }}
                            </p>
                        </div>
                    </BaseCard>

                    <BaseCard>
                        <div class="card-body text-center">
                            <p class="text-dark-400 mb-2">Monthly Revenue</p>
                            <p class="text-3xl font-bold text-success-500">
                                ${{ formatCurrency(analytics.monthly_revenue) }}
                            </p>
                        </div>
                    </BaseCard>

                    <BaseCard>
                        <div class="card-body text-center">
                            <p class="text-dark-400 mb-2">Total Payments</p>
                            <p class="text-3xl font-bold text-dark-100">
                                {{ analytics.total_payments }}
                            </p>
                        </div>
                    </BaseCard>

                    <BaseCard>
                        <div class="card-body text-center">
                            <p class="text-dark-400 mb-2">Success Rate</p>
                            <p class="text-3xl font-bold text-info-500">
                                {{ formatPercent(analytics.success_rate) }}%
                            </p>
                        </div>
                    </BaseCard>
                </div>

                <!-- Additional Stats -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <BaseCard>
                        <div class="card-body">
                            <h3 class="text-lg font-semibold text-dark-100 mb-4">Subscription Stats</h3>
                            <div class="space-y-4">
                                <div class="flex justify-between items-center">
                                    <span class="text-dark-300">Active Subscriptions</span>
                                    <span class="font-medium text-primary-500">{{ analytics.active_subscriptions
                                        }}</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-dark-300">Monthly Payments</span>
                                    <span class="font-medium text-dark-100">{{ analytics.monthly_payments }}</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-dark-300">Avg. Payment</span>
                                    <span class="font-medium text-success-500">${{ formatCurrency(analytics.avg_payment)
                                        }}</span>
                                </div>
                            </div>
                        </div>
                    </BaseCard>
                </div>
            </div>

            <!-- Error State -->
            <div v-else class="text-center py-12">
                <p class="text-error-400">Failed to load analytics data.</p>
                <button @click="loadAnalytics" class="btn btn-outline mt-4">Retry</button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { paymentsService, type PaymentAnalytics } from '@/services/payments'
import BaseCard from '@/components/ui/BaseCard.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const toast = useToast()
const loading = ref(true)
const analytics = ref<PaymentAnalytics | null>(null)

const formatCurrency = (value?: string | number) => {
    return Number(value || 0).toFixed(2)
}

const formatPercent = (value?: string | number) => {
    return Number(value || 0).toFixed(1)
}

const loadAnalytics = async () => {
    loading.value = true
    try {
        analytics.value = await paymentsService.getPaymentAnalytics()
    } catch (error) {
        console.error('Failed to load analytics:', error)
        toast.error('Failed to load analytics data')
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadAnalytics()
})
</script>
