import { defineStore } from 'pinia'
import { ref } from 'vue'
import paymentsService, { type Payment, type Refund, type PaymentCreate, type RefundCreate, type PaymentListQueryParams, type RefundListQueryParams } from '@/services/payments'

interface Pagination {
  count: number
  next: string | null
  previous: string | null
}

export const usePaymentsStore = defineStore('payments', () => {
  const payments = ref<Payment[]>([])
  const refunds = ref<Refund[]>([])
  const currentPayment = ref<Payment | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | Record<string, unknown> | null>(null)
  const pagination = ref<Pagination>({
    count: 0,
    next: null,
    previous: null,
  })

  // Fetch payments
  async function fetchPayments(params: PaymentListQueryParams = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsService.getPayments(params)
      payments.value = data.results || []
      if (data.count !== undefined) {
        pagination.value = {
          count: data.count,
          next: data.next,
          previous: data.previous,
        }
      }
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch payments'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch single payment
  async function fetchPayment(id: string) {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsService.getPayment(id)
      currentPayment.value = data
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create checkout session
  async function createCheckoutSession(paymentCreate: PaymentCreate) {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsService.createCheckoutSession(paymentCreate)
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to create checkout session'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Retry payment
  async function retryPayment(paymentId: string) {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsService.retryPayment(paymentId)
      // Just returning the checkout session
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to retry payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Cancel payment
  async function cancelPayment(paymentId: string) {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsService.cancelPayment(paymentId)
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to cancel payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch refunds
  async function fetchRefunds(params: RefundListQueryParams = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsService.getRefunds(params)
      refunds.value = data.results || []
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch refunds'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create refund for a payment
  async function refundPayment(paymentId: string, refundData: RefundCreate) {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsService.refundPayment(paymentId, refundData)
      // Add to refunds list if we have it
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to create refund'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    payments,
    refunds,
    currentPayment,
    loading,
    error,
    pagination,
    fetchPayments,
    fetchPayment,
    createCheckoutSession,
    retryPayment,
    cancelPayment,
    fetchRefunds,
    refundPayment,
  }
})
