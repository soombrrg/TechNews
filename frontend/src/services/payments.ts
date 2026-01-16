import api from './api'
import type { components, operations } from '@/types/api'

// Type aliases from OpenAPI schema
export type Payment = components['schemas']['Payment']
export type PaymentStatusEnum = components['schemas']['PaymentStatusEnum']
export type PaymentCreate = components['schemas']['PaymentCreate']
export type PaymentAnalytics = components['schemas']['PaymentAnalytics']
export type PaginatedPaymentList = components['schemas']['PaginatedPaymentList']
export type PaymentStatus = components['schemas']['PaymentStatus']
export type UserPaymentHistory = components['schemas']['UserPaymentHistory']

export type Refund = components['schemas']['Refund']
export type RefundCreate = components['schemas']['RefundCreate']
export type PaginatedRefundList = components['schemas']['PaginatedRefundList']

export type StripeCheckoutSession = components['schemas']['StripeCheckoutSession']
// Types from operations of OpenAPI schema
export type PaymentListQueryParams = operations['payments_list']['parameters']['query']
export type RefundListQueryParams = operations['payments_refunds_list']['parameters']['query']
export type PaymentCancel = operations['payments_cancel_create']['responses'][200]['content']['application/json']


export const paymentsService = {
  // Get payments list
  async getPayments(params: PaymentListQueryParams = {}): Promise<PaginatedPaymentList> {
    const response = await api.get<PaginatedPaymentList>('/api/v1/payments/', { params })
    return response.data
  },

  // Get single payment
  async getPayment(id: string): Promise<Payment> {
    const response = await api.get<Payment>(`/api/v1/payments/${id}/`)
    return response.data
  },

  // Create checkout session
  async createCheckoutSession(
    data: PaymentCreate,
  ): Promise<StripeCheckoutSession> {
    const response = await api.post<StripeCheckoutSession>(
      '/api/v1/payments/create-checkout-session/',
      data,
    )
    return response.data
  },

  // Get payment history
  async getPaymentHistory(): Promise<UserPaymentHistory> {
    const response = await api.get<UserPaymentHistory>('/api/v1/payments/history/')
    return response.data
  },

  // Get payment status
  async getPaymentStatus(paymentId: string): Promise<PaymentStatus> {
    const response = await api.get<PaymentStatus>(`/api/v1/payments/${paymentId}/status/`)
    return response.data
  },

  // Retry payment
  async retryPayment(paymentId: string): Promise<StripeCheckoutSession> {
    const response = await api.post<StripeCheckoutSession>(`/api/v1/payments/${paymentId}/retry/`)
    return response.data
  },

  // Cancel payment
  async cancelPayment(paymentId: string): Promise<PaymentCancel> {
    const response = await api.post<PaymentCancel>(`/api/v1/payments/${paymentId}/cancel/`)
    return response.data
  },

  // Refund payment
  async refundPayment(paymentId: string, data: RefundCreate): Promise<PaymentStatus> {
    const response = await api.post<PaymentStatus>(`/api/v1/payments/${paymentId}/refund/`, data)
    return response.data
  },

  // Get refunds (admin only)
  async getRefunds(params: RefundListQueryParams = {}): Promise<PaginatedRefundList> {
    const response = await api.get<PaginatedRefundList>('/api/v1/payments/refunds/', { params })
    return response.data
  },

  // Get single refund (admin only)
  async getRefund(id: string): Promise<Refund> {
    const response = await api.get<Refund>(`/api/v1/payments/refunds/${id}/`)
    return response.data
  },

  // Get payment analytics (admin only)
  async getPaymentAnalytics(): Promise<PaymentAnalytics> {
    const response = await api.get<PaymentAnalytics>('/api/v1/payments/analytics/')
    return response.data
  },
}

export default paymentsService
