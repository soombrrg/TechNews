<template>
  <footer class="bg-dark-800 border-t border-dark-700 mt-auto">
    <div class="container-content py-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- About -->
        <div>
          <h3 class="text-lg font-semibold text-dark-100 mb-4">TechNews</h3>
          <p class="text-dark-400 text-sm">
            Your source for the latest tech news and articles. Stay informed with our comprehensive
            coverage.
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <h4 class="text-sm font-semibold text-dark-100 mb-4">Quick Links</h4>
          <ul class="space-y-2">
            <li>
              <router-link to="/" class="text-dark-400 hover:text-primary-500 text-sm transition-colors">
                Home
              </router-link>
            </li>
            <li>
              <router-link to="/posts" class="text-dark-400 hover:text-primary-500 text-sm transition-colors">
                Posts
              </router-link>
            </li>
            <li>
              <router-link to="/categories" class="text-dark-400 hover:text-primary-500 text-sm transition-colors">
                Categories
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Account -->
        <div>
          <h4 class="text-sm font-semibold text-dark-100 mb-4">Account</h4>
          <ul class="space-y-2">
            <li v-if="!authStore.isAuthenticated">
              <router-link to="/login" class="text-dark-400 hover:text-primary-500 text-sm transition-colors">
                Login
              </router-link>
            </li>
            <li v-if="!authStore.isAuthenticated">
              <router-link to="/register" class="text-dark-400 hover:text-primary-500 text-sm transition-colors">
                Register
              </router-link>
            </li>
            <li v-if="authStore.isAuthenticated">
              <router-link to="/profile" class="text-dark-400 hover:text-primary-500 text-sm transition-colors">
                Profile
              </router-link>
            </li>
            <li>
              <router-link to="/subscriptions" class="text-dark-400 hover:text-primary-500 text-sm transition-colors">
                Subscriptions
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h4 class="text-sm font-semibold text-dark-100 mb-4">Contact</h4>
          <ul class="space-y-2">
            <li class="text-dark-400 text-sm">Email: info@technews.com</li>
            <li class="text-dark-400 text-sm">Phone: +1 234 567 890</li>
          </ul>
        </div>
      </div>

      <div class="mt-8 pt-8 border-t border-dark-700">
        <p class="text-center text-dark-400 text-sm">
          &copy; {{ currentYear }} TechNews. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const currentYear = computed(() => new Date().getFullYear())
</script>
