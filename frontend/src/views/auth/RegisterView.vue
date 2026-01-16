<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-950 py-12 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-dark-100 mb-2">Create Account</h2>
        <p class="text-dark-400">Join our community today</p>
      </div>

      <BaseCard>
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <!-- Username -->
            <BaseInput v-model="form.username" label="Username" type="text" placeholder="Choose a username"
              :error="errors.username" required />

            <!-- Name Fields -->
            <div class="grid grid-cols-2 gap-4 mt-4">
              <BaseInput v-model="form.first_name" label="First Name" type="text" placeholder="First Name"
                :error="errors.first_name" />
              <BaseInput v-model="form.last_name" label="Last Name" type="text" placeholder="Last Name"
                :error="errors.last_name" />
            </div>

            <!-- Email -->
            <div class="mt-4">
              <BaseInput v-model="form.email" label="Email" type="email" placeholder="Enter your email"
                :error="errors.email" required />
            </div>

            <!-- Password -->
            <div class="mt-4">
              <BaseInput v-model="form.password" label="Password" type="password" placeholder="Create a password"
                :error="errors.password" help-text="At least 8 characters" required />
            </div>

            <!-- Confirm Password -->
            <div class="mt-4">
              <BaseInput v-model="form.password2" label="Confirm Password" type="password"
                placeholder="Confirm your password" :error="errors.password2" required />
            </div>

            <!-- Error message -->
            <div v-if="errors.general" class="mt-4 p-3 bg-error-500/10 border border-error-500/30 rounded-lg">
              <p class="text-error-400 text-sm">{{ errors.general }}</p>
            </div>

            <!-- Submit button -->
            <div class="mt-6">
              <BaseButton type="submit" variant="primary" :loading="loading" full-width size="lg">
                Create Account
              </BaseButton>
            </div>
          </form>

          <!-- Login link -->
          <div class="mt-6 text-center">
            <p class="text-dark-400 text-sm">
              Already have an account?
              <router-link to="/login" class="text-primary-500 hover:text-primary-400 font-medium">
                Sign in
              </router-link>
            </p>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  password2: '',
})

const errors = reactive({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  password2: '',
  general: '',
})

interface ApiErrorResponse {
  response?: {
    data?: {
      username?: string | string[]
      first_name?: string | string[]
      last_name?: string | string[]
      email?: string | string[]
      password?: string | string[]
      detail?: string
    }
  }
}

const handleSubmit = async () => {
  // Reset errors
  Object.keys(errors).forEach((key) => {
    errors[key as keyof typeof errors] = ''
  })

  // Validate
  if (!form.username) {
    errors.username = 'Username is required'
    return
  }
  if (!form.email) {
    errors.email = 'Email is required'
    return
  }
  if (!form.password) {
    errors.password = 'Password is required'
    return
  }
  if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    return
  }
  if (form.password !== form.password2) {
    errors.password2 = 'Passwords do not match'
    return
  }

  loading.value = true

  try {
    await authStore.register({
      username: form.username,
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      password: form.password,
      password_confirmation: form.password2,
    })

    toast.success('Account created successfully!')
    router.push('/')
  } catch (error: unknown) {
    console.error('Registration error:', error)
    const err = error as ApiErrorResponse

    // Handle field-specific errors
    if (err.response?.data) {
      const data = err.response.data
      if (data.username) {
        errors.username = Array.isArray(data.username) ? data.username[0] : data.username
      }
      if (data.first_name) {
        errors.first_name = Array.isArray(data.first_name) ? data.first_name[0] : data.first_name
      }
      if (data.last_name) {
        errors.last_name = Array.isArray(data.last_name) ? data.last_name[0] : data.last_name
      }
      if (data.email) {
        errors.email = Array.isArray(data.email) ? data.email[0] : data.email
      }
      if (data.password) {
        errors.password = Array.isArray(data.password) ? data.password[0] : data.password
      }
      if (!errors.username && !errors.email && !errors.password) {
        errors.general = data.detail || 'Registration failed'
      }
    } else {
      errors.general = 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
