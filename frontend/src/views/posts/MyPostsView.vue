<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-content">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-dark-100">My Posts</h1>
        <router-link to="/posts/create" class="btn btn-primary"> Create New Post </router-link>
      </div>

      <!-- Filters -->
      <div class="card mb-8">
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Search -->
            <div>
              <label class="form-label">Search</label>
              <input v-model="filters.search" type="text" placeholder="Search your posts..." class="form-input"
                @input="debouncedSearch" />
            </div>

            <!-- Status Filter -->
            <div>
              <label class="form-label">Status</label>
              <select v-model="filters.publication_status" class="form-select" @change="applyFilters">
                <option value="">All Status</option>
                <option value="p">Published</option>
                <option value="d">Draft</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading your posts..." />
      </div>

      <!-- Posts Grid -->
      <div v-else-if="posts.length > 0">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <PostCard v-for="post in posts" :key="post.id" :post="post" />
        </div>

        <!-- Pagination -->
        <div v-if="pagination.count > 0" class="flex justify-center items-center space-x-4">
          <button :disabled="!pagination.previous" @click="goToPage(currentPage - 1)" class="btn btn-outline btn-sm">
            Previous
          </button>
          <span class="text-dark-300"> Page {{ currentPage }} of {{ totalPages }} </span>
          <button :disabled="!pagination.next" @click="goToPage(currentPage + 1)" class="btn btn-outline btn-sm">
            Next
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">✍️</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No posts yet</h3>
        <p class="text-dark-400 mb-6">Start creating your first post</p>
        <router-link to="/posts/create" class="btn btn-primary"> Create Post </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import postsService from '@/services/posts'
import PostCard from '@/components/posts/PostCard.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import type { components } from '@/types/api'
import { debounce } from '@/services/utils'

type PostList = components['schemas']['PostList']

const loading = ref(false)
const currentPage = ref(1)
const posts = ref<PostList[]>([])
const pagination = ref({
  count: 0,
  next: null as string | null,
  previous: null as string | null,
})

const filters = reactive({
  search: '',
  publication_status: '',
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.count / 10)
})

let searchTimeout: number = 500

const debouncedSearch = debounce(() => {
  applyFilters()
}, searchTimeout)


const applyFilters = async () => {
  loading.value = true
  currentPage.value = 1
  try {
    const params: Record<string, string | number> = {
      page: currentPage.value,
    }
    if (filters.search) params.search = filters.search
    if (filters.publication_status) params.publication_status = filters.publication_status

    const data = await postsService.getMyPosts(params)
    posts.value = data.results || []
    pagination.value = {
      count: data.count || 0,
      next: data.next,
      previous: data.previous,
    }
  } catch (error) {
    console.error('Failed to fetch my posts:', error)
  } finally {
    loading.value = false
  }
}




const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      page: currentPage.value,
    }
    if (filters.search) params.search = filters.search
    if (filters.publication_status) params.publication_status = filters.publication_status

    const data = await postsService.getMyPosts(params)
    posts.value = data.results || []
    pagination.value = {
      count: data.count || 0,
      next: data.next,
      previous: data.previous,
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('Failed to fetch my posts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await applyFilters()
})
</script>
