import { defineStore } from 'pinia'
import { ref } from 'vue'
import subscriptionsService, { type Subscription, type SubscriptionPlan, type UserSubscriptionStatus, type SubscriptionHistory, type PlansQueryParams, type SubscriptionHistoryQueryParams, type PinnedPostData } from '@/services/subscriptions'

export const useSubscriptionsStore = defineStore('subscriptions', () => {
  const plans = ref<SubscriptionPlan[]>([])
  const currentSubscription = ref<Subscription | null>(null)
  const subscriptionStatus = ref<UserSubscriptionStatus | null>(null)
  const history = ref<SubscriptionHistory[]>([])
  const pinnedPosts = ref<PinnedPostData[]>([])
  const loading = ref<boolean>(false)
  const error = ref<string | Record<string, unknown> | null>(null)

  // Fetch subscription plans
  async function fetchPlans(params: PlansQueryParams = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await subscriptionsService.getPlans(params)
      plans.value = data.results || []
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch subscription plans'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch my subscription
  async function fetchMySubscription() {
    loading.value = true
    error.value = null
    try {
      const data = await subscriptionsService.getMySubscription()
      currentSubscription.value = data
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch subscription'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch subscription status
  async function fetchSubscriptionStatus() {
    try {
      const data = await subscriptionsService.getSubscriptionStatus()
      subscriptionStatus.value = data
      return data
    } catch (err) {
      console.error('Failed to fetch subscription status:', err)
      throw err
    }
  }

  // Fetch subscription history
  async function fetchSubscriptionHistory(params: SubscriptionHistoryQueryParams = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await subscriptionsService.getSubscriptionHistory(params)
      history.value = data.results || []
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch subscription history'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Cancel subscription
  async function cancelSubscription() {
    loading.value = true
    error.value = null
    try {
      const data = await subscriptionsService.cancelSubscription()
      currentSubscription.value = null
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to cancel subscription'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch pinned posts
  async function fetchPinnedPosts() {
    loading.value = true
    error.value = null
    try {
      const data = await subscriptionsService.getPinnedPosts()
      pinnedPosts.value = data.results || []
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch pinned posts'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    plans,
    currentSubscription,
    subscriptionStatus,
    history,
    loading,
    error,
    fetchPlans,
    fetchMySubscription,
    fetchSubscriptionStatus,
    fetchSubscriptionHistory,
    cancelSubscription,
    pinnedPosts,
    fetchPinnedPosts,
  }
})
