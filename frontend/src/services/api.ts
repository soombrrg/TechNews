import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosError } from 'axios'
import Cookies from 'js-cookie'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = Cookies.get('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // If data is FormData, remove Content-Type header to let the browser set it with boundary
    if (config.data instanceof FormData && config.headers) {
      delete config.headers['Content-Type']
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  },
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = Cookies.get('refresh_token')
        if (refreshToken) {
          const response = await axios.post<{ access: string }>(
            `${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/token/refresh/`,
            { refresh: refreshToken },
          )

          const { access } = response.data
          Cookies.set('access_token', access, { expires: 1 })

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access}`
          }
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export default api
