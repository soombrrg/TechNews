<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-narrow">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">Change Password</h1>

      <BaseCard>
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <!-- Old Password -->
            <BaseInput v-model="form.old_password" label="Current Password" type="password"
              placeholder="Enter your current password" :error="errors.old_password" required />

            <!-- New Password -->
            <div class="mt-4">
              <BaseInput v-model="form.new_password" label="New Password" type="password"
                placeholder="Enter new password" :error="errors.new_password" help-text="At least 8 characters"
                required />
            </div>

            <!-- Confirm New Password -->
            <div class="mt-4">
              <BaseInput v-model="form.new_password_confirmation" label="Confirm New Password" type="password"
                placeholder="Confirm new password" :error="errors.new_password_confirmation" required />
            </div>

            <!-- Error message -->
            <div v-if="errors.general" class="mt-4 p-3 bg-error-500/10 border border-error-500/30 rounded-lg">
              <p class="text-error-400 text-sm">{{ errors.general }}</p>
            </div>

            <!-- Submit button -->
            <div class="mt-6 flex space-x-4">
              <BaseButton type="submit" variant="primary" :loading="loading">
                Update Password
              </BaseButton>
              <router-link to="/profile" class="btn btn-outline"> Cancel </router-link>
            </div>
          </form>
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
  old_password: '',
  new_password: '',
  new_password_confirmation: '',
})

const errors = reactive({
  old_password: '',
  new_password: '',
  new_password_confirmation: '',
  general: '',
})

const handleSubmit = async () => {
  // Reset errors
  Object.keys(errors).forEach((key) => {
    errors[key as keyof typeof errors] = ''
  })

  // Validate
  if (!form.old_password) {
    errors.old_password = 'Current password is required'
    return
  }
  if (!form.new_password) {
    errors.new_password = 'New password is required'
    return
  }
  if (form.new_password.length < 8) {
    errors.new_password = 'Password must be at least 8 characters'
    return
  }
  if (form.new_password !== form.new_password_confirmation) {
    errors.new_password_confirmation = 'Passwords do not match'
    return
  }

  loading.value = true

  try {
    await authStore.changePassword(form)
    toast.success('Password changed successfully!')
    router.push('/profile')
  } catch (error: unknown) {
    console.error('Password change error:', error)
    const err = error as { response?: { data?: Record<string, string | string[]> } }

    if (err.response?.data) {
      const data = err.response.data
      if (data.old_password) {
        errors.old_password = Array.isArray(data.old_password)
          ? data.old_password[0]
          : data.old_password
      }
      if (data.new_password) {
        errors.new_password = Array.isArray(data.new_password)
          ? data.new_password[0]
          : data.new_password
      }
      if (!errors.old_password && !errors.new_password) {
        errors.general = (data.detail as string) || 'Password change failed'
      }
    } else {
      errors.general = 'Password change failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
