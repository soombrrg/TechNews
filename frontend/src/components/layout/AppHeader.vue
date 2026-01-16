<template>
  <!-- Top Bar -->
  <header>
    <div class="top-bar">
      <div class="date">{{ currentDate }}</div>
      <div class="social-links">
        <router-link to="/about">About</router-link>
        <router-link to="/subscriptions">Subscribe</router-link>
      </div>
    </div>
  </header>

  <!-- Main Navigation -->
  <nav>
    <div class="nav-container">
      <!-- Desktop Navigation -->
      <div class="logo"><router-link to="/">TechNews</router-link></div>
      <ul class="nav-links">
        <li><router-link to="/">Home</router-link></li>
        <li><router-link to="/posts">Posts</router-link></li>
        <li><router-link to="/categories">Categories</router-link></li>
        <li><router-link to="/about">About</router-link></li>
      </ul>

      <!-- User Menu / Auth Buttons -->
      <div class="flex items-center gap-3">
        <template v-if="authStore.isAuthenticated">
          <!-- User Dropdown -->
          <div class="relative" ref="userMenuRef">
            <button @click="toggleUserMenu"
              class="flex items-center gap-2 px-3 py-2 rounded hover:bg-dark-850 transition-colors">
              <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center overflow-hidden">
                <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" :alt="authStore.userFullName"
                  class="w-full h-full object-cover" />
                <span v-else class="text-white font-medium text-sm">{{ userInitials }}</span>
              </div>
              <span class="hidden md:block text-dark-100 text-sm font-semibold">{{ authStore.userFullName }}</span>
              <svg class="w-4 h-4 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <transition name="fade">
              <div v-if="showUserMenu"
                class="absolute right-0 mt-2 w-48 bg-dark-900 border border-dark-700 rounded-lg shadow-xl py-1 z-50">
                <router-link to="/profile" class="block px-4 py-2 text-sm text-dark-200 hover:bg-dark-850"
                  @click="showUserMenu = false">
                  Profile
                </router-link>
                <router-link to="/my-posts" class="block px-4 py-2 text-sm text-dark-200 hover:bg-dark-850"
                  @click="showUserMenu = false">
                  My Posts
                </router-link>
                <router-link to="/my-comments" class="block px-4 py-2 text-sm text-dark-200 hover:bg-dark-850"
                  @click="showUserMenu = false">
                  My Comments
                </router-link>
                <router-link to="/my-subscription" class="block px-4 py-2 text-sm text-dark-200 hover:bg-dark-850"
                  @click="showUserMenu = false">
                  My Subscription
                </router-link>
                <hr class="my-1 border-dark-700" />
                <button @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-error-400 hover:bg-dark-850">
                  Logout
                </button>
              </div>
            </transition>
          </div>
        </template>
        <template v-else>
          <router-link to="/login"
            class="text-dark-200 hover:text-primary-500 font-semibold text-sm transition-colors">Login</router-link>
          <router-link to="/register" class="subscribe-btn">Register</router-link>
        </template>

        <!-- Mobile Menu Button -->
        <button @click="toggleMobileMenu" class="md:hidden p-2 rounded hover:bg-dark-850">
          <svg v-if="!showMobileMenu" class="w-6 h-6 text-dark-100" fill="none" stroke="currentColor"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="w-6 h-6 text-dark-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <transition name="slide-down">
      <div v-if="showMobileMenu" class="md:hidden border-t border-dark-700 bg-dark-925">
        <div class="nav-container">
          <ul class="nav-links">
            <li><router-link to="/" @click="showMobileMenu = false">Home</router-link></li>
            <li><router-link to="/posts" @click="showMobileMenu = false">Posts</router-link></li>
            <li><router-link to="/categories" @click="showMobileMenu = false">Categories</router-link></li>
            <li><router-link to="/about" @click="showMobileMenu = false">About</router-link></li>
          </ul>
        </div>
      </div>
    </transition>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const userInitials = computed(() => {
  if (!authStore.user) return ''
  const name = authStore.user.full_name || authStore.user.username
  return name.charAt(0).toUpperCase()
})

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const handleLogout = async () => {
  showUserMenu.value = false
  try {
    await authStore.logout()
    toast.success('Logged out successfully')
    router.push('/')
  } catch (error) {
    console.error('Logout error:', error)
    toast.error('Failed to logout')
  }
}

const handleClickOutside = (event: MouseEvent) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
header {
  background: #151525;
  color: white;
  padding: 1rem 0;
}

.top-bar {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

nav {
  background: #121A32;
  border-bottom: 3px solid #931127;
  position: sticky;
  top: 0;
  z-index: 40;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date {
  color: #A8A095;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-links a {
  color: #A8A095;
  text-decoration: none;
}

.logo {
  font-family: 'Merriweather', serif;
  font-size: 2rem;
  font-weight: 900;
  color: white;
  padding: 0.5rem 0;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}


.nav-links {
  display: flex;
  gap: 0;
  list-style: none;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 1.5rem 1.5rem;
  display: block;
  font-weight: 600;
  transition: background 0.3s;
}

.nav-links a:hover {
  background: #9D1329;
}

.subscribe-btn {
  background: #9D1329;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 700;
}

.subscribe-btn:hover {
  background: #d63653;
}

.mobile-menu-btn {
  display: none;
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: block;
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
  }

  .nav-links {
    display: none;
  }

  .nav-links.mobile-open {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #121A32;
  }

  .subscribe-btn {
    display: none;
  }
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
