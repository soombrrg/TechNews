<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-950 py-12 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-dark-100 mb-2">Welcome Back</h2>
        <p class="text-dark-400">Sign in to your account to continue</p>
      </div>

      <BaseCard>
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <!-- Email -->
            <BaseInput v-model="form.email" label="Email" type="email" placeholder="Enter your email"
              :error="errors.email" required />

            <!-- Password -->
            <div class="mt-4">
              <BaseInput v-model="form.password" label="Password" type="password" placeholder="Enter your password"
                :error="errors.password" required />
            </div>

            <!-- Error message -->
            <div v-if="errors.general" class="mt-4 p-3 bg-error-500/10 border border-error-500/30 rounded-lg">
              <p class="text-error-400 text-sm">{{ errors.general }}</p>
            </div>

            <!-- Submit button -->
            <div class="mt-6">
              <BaseButton type="submit" variant="primary" :loading="loading" full-width size="lg">
                Sign In
              </BaseButton>
            </div>
          </form>

          <!-- Register link -->
          <div class="mt-6 text-center">
            <p class="text-dark-400 text-sm">
              Don't have an account?
              <router-link to="/register" class="text-primary-500 hover:text-primary-400 font-medium">
                Sign up
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
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
})

const errors = reactive({
  email: '',
  password: '',
  general: '',
})

const handleSubmit = async () => {
  // Reset errors
  errors.email = ''
  errors.password = ''
  errors.general = ''

  // Validate
  if (!form.email) {
    errors.email = 'Username is required'
    return
  }
  if (!form.password) {
    errors.password = 'Password is required'
    return
  }

  loading.value = true

  try {
    await authStore.login({
      email: form.email,
      password: form.password,
    })

    toast.success('Logged in successfully!')

    // Redirect to intended page or home
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (error: unknown) {
    console.error('Login error:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    errors.general = err.response?.data?.detail || 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>
