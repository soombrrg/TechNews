<template>
  <div class="min-h-screen py-12">
    <div class="container-content">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-dark-100">All Posts</h1>
        <router-link v-if="authStore.isAuthenticated" to="/posts/create" class="btn btn-primary">
          Create Post
        </router-link>
      </div>


      <!-- Filters -->
      <div class="card mb-8 bg-dark-900">
        <div class="card-body ">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Search -->
            <div class="md:col-span-2">
              <label class="form-label">Search</label>
              <input v-model="filters.search" type="text" placeholder="Search posts..." class="form-input"
                @input="debouncedSearch" />
            </div>

            <!-- Category Filter -->
            <div class="md:col-span-1">
              <label class="form-label">Category</label>
              <select v-model="filters.category" class="form-select" @change="applyFilters">
                <option :value="undefined">All Categories</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>

            <!-- View Toggle -->
            <div class="flex flex-row gap-4">
              <div class="flex items-center gap-2">
                <div class="flex items-center gap-2 bg-dark-800 rounded-lg p-1">
                  <button @click="viewMode = 'grid'"
                    :class="viewMode === 'grid' ? 'bg-primary-500 text-white' : 'text-dark-300 hover:text-white'"
                    class="px-3 py-2 rounded transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path
                        d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                    </svg>
                  </button>
                  <button @click="viewMode = 'list'"
                    :class="viewMode === 'list' ? 'bg-primary-500 text-white' : 'text-dark-300 hover:text-white'"
                    class="px-3 py-2 rounded transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd"
                        d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                        clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Sort By -->
            <div class="md:col-start-3 mb-3">
              <label class="form-label">Sort By</label>
              <select v-model="filters.ordering" class="form-select" @change="applyFilters">
                <option value="-created">Newest First</option>
                <option value="created">Oldest First</option>
                <option value="-views_count">Most Viewed</option>
                <option value="views_count">Least Viewed</option>
              </select>
            </div>

          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading posts..." />
      </div>

      <!-- Posts Display -->
      <div v-else-if="posts.length > 0">
        <transition name="fade" mode="out-in">
          <!-- Grid View -->
          <div v-if="viewMode === 'grid'" key="grid" class="posts-grid">
            <PostCard v-for="post in posts" :key="post.id" :post="post" />
          </div>

          <!-- List View -->
          <div v-else key="list" class="posts-list">
            <PostRow v-for="post in posts" :key="post.id" :post="post" />
          </div>
        </transition>

        <!-- Pagination -->
        <div v-if="pagination.count > 0" class="flex justify-center items-center space-x-4">
          <button :disabled="!pagination.previous" @click="goToPage(currentPage - 1)" class="btn btn-outline btn-sm">
            Previous
          </button>
          <span class="text-dark-300">Page {{ currentPage }} of {{ totalPages }} </span>
          <button :disabled="!pagination.next" @click="goToPage(currentPage + 1)" class="btn btn-outline btn-sm">
            Next
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">📝</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No posts found</h3>
        <p class="text-dark-400 mb-6">Try adjusting your filters or create a new post</p>
        <router-link v-if="authStore.isAuthenticated" to="/posts/create" class="btn btn-primary">
          Create Post
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePostsStore } from '@/stores/posts'
import PostCard from '@/components/posts/PostCard.vue'
import PostRow from '@/components/posts/PostRow.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import type { Category, PostList, PostsQueryParams } from '@/services/posts'
import { debounce } from 'lodash'


const authStore = useAuthStore()
const postsStore = usePostsStore()
const loading = ref(false)
const currentPage = ref(1)
const viewMode = ref<'grid' | 'list'>('grid')

const filters = reactive<PostsQueryParams>({
  search: '',
  category: undefined,
  ordering: '-created',
})

const categories = computed<Category[]>(() => postsStore.categories)
const posts = computed<PostList[]>(() => postsStore.posts)
const pagination = computed(() => postsStore.pagination)
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
    const params: PostsQueryParams = {
      page: currentPage.value,
      ordering: filters.ordering,
    }
    if (filters.search) params.search = filters.search
    if (filters.category) params.category = filters.category
    if (filters.publication_status) params.publication_status = filters.publication_status

    await postsStore.fetchPosts(params)
  } catch (error) {
    console.error('Failed to fetch posts:', error)
  } finally {
    loading.value = false
  }
}

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loading.value = true
  try {
    const params: PostsQueryParams = {
      page: currentPage.value,
      ordering: filters.ordering,
    }
    if (filters.search) params.search = filters.search
    if (filters.category) params.category = filters.category

    await postsStore.fetchPosts(params)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('Failed to fetch posts:', error)
  } finally {
    loading.value = false
  }
}


onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      postsStore.fetchCategories() || Promise.resolve(),
      postsStore.fetchPosts({ page: 1 }) || Promise.resolve(),
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
})

</script>

<style scoped>
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 2rem;

}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .posts-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .posts-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}


/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
