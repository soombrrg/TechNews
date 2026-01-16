import api from './api'
import type { components, operations } from '@/types/api'

// Type aliases from OpenAPI schema
export type UserRegistration = components['schemas']['UserRegistration']
export type UserLogin = components['schemas']['UserLogin']
export type UserProfile = components['schemas']['UserProfile']
export type UserUpdate = components['schemas']['UserUpdate']
export type ChangePassword = components['schemas']['ChangePassword']
export type TokenRefresh = components['schemas']['TokenRefresh']
export type TokenVerify = components['schemas']['TokenVerify']
export type UserRegistrationLoginResponse = components['schemas']['UserRegistrationLoginResponse']

// Using operation response types from API
export type LogoutResponse = operations['auth_logout_create']['responses'][200]['content']['application/json']
export type ChangePasswordResponse = operations['auth_change_password_update']['responses'][200]['content']['application/json']
export type TokenRefreshResponse = operations['auth_token_refresh_create']['responses'][200]['content']['application/json']
export type TokenVerifyResponse = operations['auth_token_verify_create']['responses'][200]['content']['application/json']

export const authService = {
  // Login
  async login(credentials: UserLogin): Promise<UserRegistrationLoginResponse> {
    const response = await api.post<UserRegistrationLoginResponse>('/api/v1/auth/login/', credentials)
    return response.data
  },

  // Register
  async register(userData: UserRegistration): Promise<UserRegistrationLoginResponse> {
    const response = await api.post<UserRegistrationLoginResponse>('/api/v1/auth/register/', userData)
    return response.data
  },

  // Logout
  async logout(refreshToken: string): Promise<LogoutResponse> {
    const response = await api.post<LogoutResponse>('/api/v1/auth/logout/', {
      refresh: refreshToken,
    })
    return response.data
  },

  // Get user profile
  async getProfile(): Promise<UserProfile> {
    const response = await api.get<UserProfile>('/api/v1/auth/profile/')
    return response.data
  },

  // Update user profile
  async updateProfile(userData: UserUpdate): Promise<UserProfile> {
    const response = await api.put<UserProfile>('/api/v1/auth/profile/', userData)
    return response.data
  },

  // Partial update user profile
  async patchProfile(userData: Partial<UserUpdate>): Promise<UserProfile> {
    const response = await api.patch<UserProfile>('/api/v1/auth/profile/', userData)
    return response.data
  },

  // Change password
  async changePassword(passwordData: ChangePassword): Promise<ChangePasswordResponse> {
    const response = await api.put<ChangePasswordResponse>(
      '/api/v1/auth/change-password/',
      passwordData,
    )
    return response.data
  },

  // Refresh token
  async refreshToken(refreshToken: TokenRefresh): Promise<TokenRefreshResponse> {
    const response = await api.post<TokenRefreshResponse>('/api/v1/auth/token/refresh/', refreshToken)
    return response.data
  },

  // Verify token
  async verifyToken(token: TokenVerify): Promise<TokenVerifyResponse> {
    const response = await api.post<TokenVerifyResponse>('/api/v1/auth/token/verify/', token)
    return response.data
  },
}

export default authService
