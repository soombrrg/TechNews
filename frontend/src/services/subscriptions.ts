import api from './api'
import type { components, operations } from '@/types/api'

// Type aliases from OpenAPI schema
export type Subscription = components['schemas']['Subscription']
export type SubscriptionPlan = components['schemas']['SubscriptionPlan']
export type SubscriptionHistory = components['schemas']['SubscriptionHistory']
export type SubscriptionHistoryActionEnum = components['schemas']['ActionEnum']
export type UserSubscriptionStatus = components['schemas']['UserSubscriptionStatus']

export type PaginatedSubscriptionHistoryList = components['schemas']['PaginatedSubscriptionHistoryList']
export type PaginatedSubscriptionPlanList = components['schemas']['PaginatedSubscriptionPlanList']

export type PinnedPost = components['schemas']['PinnedPost']
export type PinnedPostData = components['schemas']['PinnedPostData']
export type PinnedPostsList = components['schemas']['PinnedPostsList']

// Type aliases from OpenAPI operations
export type PlansQueryParams = operations['subscribe_plans_list']['parameters']['query']
export type SubscriptionHistoryQueryParams = operations['subscribe_history_list']['parameters']['query']
export type CanPinPost = operations['subscribe_can_pin_retrieve']['responses'][200]['content']['application/json']

export const subscriptionsService = {
  // Get subscription plans
  async getPlans(params: PlansQueryParams = {}): Promise<PaginatedSubscriptionPlanList> {
    const response = await api.get<PaginatedSubscriptionPlanList>('/api/v1/subscribe/plans/', { params })
    return response.data
  },

  // Get single plan
  async getPlan(id: number): Promise<SubscriptionPlan> {
    const response = await api.get<SubscriptionPlan>(`/api/v1/subscribe/plans/${id}/`)
    return response.data
  },

  // Get my subscription
  async getMySubscription(): Promise<Subscription> {
    const response = await api.get<Subscription>('/api/v1/subscribe/my-subscription/')
    return response.data
  },

  // Get subscription status
  async getSubscriptionStatus(): Promise<UserSubscriptionStatus> {
    const response = await api.get<UserSubscriptionStatus>('/api/v1/subscribe/status/')
    return response.data
  },

  // Get subscription history
  async getSubscriptionHistory(params: SubscriptionHistoryQueryParams = {}): Promise<PaginatedSubscriptionHistoryList> {
    const response = await api.get<PaginatedSubscriptionHistoryList>(
      '/api/v1/subscribe/history/',
      { params }
    )
    return response.data
  },

  // Cancel subscription
  async cancelSubscription(): Promise<{ msg: string }> {
    const response = await api.post<{ msg: string }>('/api/v1/subscribe/cancel/')
    return response.data
  },

  // Check if can pin post
  async canPinPost(postId: number): Promise<CanPinPost> {
    const response = await api.get<CanPinPost>(`/api/v1/subscribe/can-pin/${postId}/`)
    return response.data
  },

  // Get pinned posts
  async getPinnedPosts(): Promise<PinnedPostsList> {
    const response = await api.get<PinnedPostsList>('/api/v1/subscribe/pinned-posts/')
    return response.data
  },

  // Get my pinned post
  async getMyPinnedPost(): Promise<PinnedPost> {
    const response = await api.get<PinnedPost>('/api/v1/subscribe/my-pinned-post/')
    return response.data
  },

  // Delete my pinned post
  async deleteMyPinnedPost(): Promise<void> {
    await api.delete('/api/v1/subscribe/my-pinned-post/')
  },
}

export default subscriptionsService
