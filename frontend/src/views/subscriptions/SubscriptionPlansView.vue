<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-content">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-dark-100 mb-4">Choose Your Plan</h1>
        <p class="text-xl text-dark-400">Unlock premium features with our subscription plans</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading plans..." />
      </div>

      <!-- Plans Grid -->
      <div v-else-if="plans.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
        <div v-for="plan in plans" :key="plan.id" class="card hover:border-primary-500 transition-all duration-200">

          <div class="card-body">
            <!-- Plan Name -->
            <h3 class="text-2xl font-bold text-dark-100 mb-2">{{ plan.name }}</h3>

            <!-- Status Badge -->
            <div v-if="!plan.is_active" class="mb-4">
              <BaseBadge variant="warning">Inactive</BaseBadge>
            </div>

            <!-- Price -->
            <div class="mb-6">
              <div class="flex items-baseline">
                <span class="text-4xl font-bold text-primary-500">${{ plan.price }}</span>
                <span class="text-dark-400 ml-2">/ {{ plan.duration_days }} days</span>
              </div>
            </div>

            <!-- Features -->
            <div class="mb-6 space-y-3">
              <div class="flex items-center space-x-2 text-dark-300">
                <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span>{{ plan.duration_days }} days access</span>
              </div>
              <template v-if="plan.features && typeof plan.features === 'object'">
                <div v-for="(value, key) in plan.features" :key="key" class="flex items-center space-x-2 text-dark-300">
                  <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>{{ formatFeature(key, value) }}</span>
                </div>
              </template>
            </div>

            <!-- Subscribe Button -->
            <BaseButton v-if="authStore.isAuthenticated" variant="primary" full-width @click="handleSubscribe(plan)"
              :loading="subscribing === plan.id">
              Subscribe Now
            </BaseButton>
            <router-link v-else to="/login" class="btn btn-primary w-full">
              Sign in to Subscribe
            </router-link>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">💳</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No plans available</h3>
        <p class="text-dark-400">Subscription plans will appear here once they are created</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import { useSubscriptionsStore } from '@/stores/subscriptions'
import paymentsService from '@/services/payments'
import { type PlansQueryParams, type SubscriptionPlan } from '@/services/subscriptions'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'


const toast = useToast()
const authStore = useAuthStore()
const subscriptionsStore = useSubscriptionsStore()
const loading = ref(false)
const subscribing = ref<number | null>(null)
const plans = computed<SubscriptionPlan[]>(() => subscriptionsStore.plans || [])

const formatFeature = (key: string, value: unknown): string => {
  const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  if (typeof value === 'boolean') {
    return formattedKey
  }
  return `${formattedKey}: ${value}`
}

const handleSubscribe = async (plan: SubscriptionPlan) => {
  subscribing.value = plan.id
  try {
    const baseUrl = window.location.origin
    const data = await paymentsService.createCheckoutSession({
      subscription_plan_id: plan.id,
      payment_method: 'stripe',
      success_url: `${baseUrl}/payment/success`,
      cancel_url: `${baseUrl}/payment/cancel`,
    })

    // Redirect to Stripe checkout
    if (data.checkout_url) {
      window.location.href = data.checkout_url
    } else {
      toast.error('Failed to create checkout session')
    }
  } catch (error: unknown) {
    console.error('Failed to subscribe:', error)
    const err = error as { response?: { data?: { error?: string } } }
    toast.error(err.response?.data?.error || 'Failed to start subscription process')
  } finally {
    subscribing.value = null
  }
}

const loadPlans = async (params: PlansQueryParams = {}) => {
  loading.value = true
  try {
    await Promise.all([
      subscriptionsStore.fetchPlans?.(params) || Promise.resolve(),
    ])
  } catch (error) {
    console.error('Failed to load plans:', error)
    toast.error('Failed to load subscription plans')
  } finally {
    loading.value = false
  }
}


onMounted(async () => {
  await loadPlans()
})
</script>
