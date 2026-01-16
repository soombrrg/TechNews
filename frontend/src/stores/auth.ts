import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import authService, { type ChangePassword, type UserLogin, type UserProfile, type UserRegistration, type UserUpdate } from '@/services/auth'


export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserProfile | null>(null)
  const isInitialized = ref<boolean>(false)
  const loading = ref<boolean>(false)
  const error = ref<string | Record<string, unknown> | null>(null)

  const isAuthenticated = computed<boolean>(() => !!user.value)
  const userFullName = computed<string>(() => {
    if (!user.value) return ''
    return user.value.full_name || user.value.username || ''
  })

  // Initialize auth state from cookies
  async function initializeAuth(): Promise<void> {
    const accessToken = Cookies.get('access_token')
    if (accessToken) {
      try {
        await fetchProfile()
      } catch (err) {
        console.error('Failed to fetch profile:', err)
        clearAuth()
      }
    }
    isInitialized.value = true
  }

  // Login
  async function login(credentials: UserLogin) {
    loading.value = true
    error.value = null
    try {
      const data = await authService.login(credentials)

      // Store tokens
      Cookies.set('access_token', data.access, { expires: 1 })
      Cookies.set('refresh_token', data.refresh, { expires: 7 })

      // Fetch user profile
      await fetchProfile()

      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: { detail?: string } } }
      error.value = errData.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Register
  async function register(userData: UserRegistration) {
    loading.value = true
    error.value = null
    try {
      const data = await authService.register(userData)

      // Store tokens if returned
      if (data.access && data.refresh) {
        Cookies.set('access_token', data.access, { expires: 1 })
        Cookies.set('refresh_token', data.refresh, { expires: 7 })
        await fetchProfile()
      }

      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: unknown } }
      error.value = typeof errData.response?.data === 'string' ? errData.response.data : 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Logout
  async function logout(): Promise<{ msg?: string }> {
    loading.value = true
    let response: { msg?: string } = { msg: 'Logged out' }
    try {
      const refreshToken = Cookies.get('refresh_token')
      if (refreshToken) {
        response = await authService.logout(refreshToken)
      }
    } catch (err: unknown) {
      console.error('Logout error:', err)
    } finally {
      clearAuth()
      loading.value = false
    }
    return response
  }

  // Fetch user profile
  async function fetchProfile(): Promise<UserProfile> {
    try {
      const data = await authService.getProfile()
      user.value = data
      return data
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      throw err
    }
  }

  // Update profile
  async function updateProfile(userData: UserUpdate) {
    loading.value = true
    error.value = null
    try {
      const data = await authService.updateProfile(userData)
      user.value = data
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Profile update failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Change password
  async function changePassword(passwordData: ChangePassword) {
    loading.value = true
    error.value = null
    try {
      const data = await authService.changePassword(passwordData)
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Password change failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Clear auth state
  function clearAuth(): void {
    user.value = null
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
  }

  return {
    user,
    isInitialized,
    loading,
    error,
    isAuthenticated,
    userFullName,
    initializeAuth,
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    clearAuth,
  }
})
