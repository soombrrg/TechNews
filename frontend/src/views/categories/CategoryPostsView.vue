<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-content">
      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading category..." />
      </div>

      <!-- Category Content -->
      <div v-else-if="categoryData">
        <!-- Category Header -->
        <div class="card mb-8">
          <div class="card-body">
            <h1 class="text-2xl font-bold text-dark-100 mb-4">📁 {{ categoryData.category.name }}</h1>

            <hr class="border-dark-700 mb-4" />

            <p v-if="categoryData.category.description" class="text-dark-300 text-lg mb-4">
              {{ categoryData.category.description }}
            </p>

            <hr class="border-dark-700 mb-4" />

            <p class="text-dark-500 text-sm">
              {{ categoryData.category.posts_count }} {{ categoryData.category.posts_count === 1 ? 'post' : 'posts' }}
            </p>
          </div>
        </div>

        <!-- Posts Grid -->
        <div v-if="categoryData.posts && categoryData.posts.length > 0">
          <h2 class="text-2xl font-bold text-dark-100 mb-6">Posts in this category</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <PostCard v-for="post in categoryData.posts" :key="post.id" :post="post" />
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-16">
          <div class="text-6xl mb-4">📝</div>
          <h3 class="text-xl font-semibold text-dark-100 mb-2">No posts in this category yet</h3>
          <p class="text-dark-400 mb-6">Be the first to create a post in this category</p>
          <router-link v-if="authStore.isAuthenticated" to="/posts/create" class="btn btn-primary">
            Create Post
          </router-link>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">😕</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">Category not found</h3>
        <p class="text-dark-400 mb-6">The category you're looking for doesn't exist</p>
        <router-link to="/categories" class="btn btn-primary"> Browse Categories </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import postsService from '@/services/posts'
import PostCard from '@/components/posts/PostCard.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import type { components } from '@/types/api'

type PostsByCategory = components['schemas']['PostsByCategory']

const route = useRoute()
const authStore = useAuthStore()
const loading = ref(true)
const categoryData = ref<PostsByCategory | null>(null)

onMounted(async () => {
  const slug = route.params.slug as string
  try {
    const data = await postsService.getCategoryPosts(slug)
    categoryData.value = data
  } catch (error) {
    console.error('Failed to load category:', error)
  } finally {
    loading.value = false
  }
})
</script>
