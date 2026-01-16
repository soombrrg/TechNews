<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-content">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">Categories</h1>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading categories..." />
      </div>

      <!-- Categories Grid -->
      <div v-else-if="categories.length > 0">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <router-link v-for="category in categories" :key="category.id" :to="`/categories/${category.slug}`"
            class="card hover:border-primary-500 transition-all duration-200 hover-glow-primary group cursor-pointer">
            <div class="card-body text-center">
              <div class="text-4xl mb-3">📁</div>
              <h3 class="text-xl font-semibold text-dark-100 mb-2 group-hover:text-primary-500 transition-colors">
                {{ category.name }}
              </h3>
              <p v-if="category.description" class="text-dark-400 text-sm mb-3 line-clamp-2">
                {{ category.description }}
              </p>
              <div class="flex items-center justify-center space-x-4 text-sm text-dark-500">
                <span>{{ category.posts_count || 0 }} posts</span>
              </div>
            </div>
          </router-link>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.count > 10" class="flex justify-center items-center space-x-4 mt-8">
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
        <div class="text-6xl mb-4">📂</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No categories found</h3>
        <p class="text-dark-400">Categories will appear here once they are created</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePostsStore } from '@/stores/posts'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import type { Category } from '@/services/posts'


const postsStore = usePostsStore()
const loading = ref(false)
const currentPage = ref(1)
const categories = ref<Category[]>([])
const pagination = ref({
  count: 0,
  next: null as string | null,
  previous: null as string | null,
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.count / 10)
})

const loadCategories = async (page = 1) => {
  loading.value = true
  try {
    const data = await postsStore.fetchCategories({ page })
    categories.value = data.results
    if (data.count !== undefined) {
      pagination.value = {
        count: data.count,
        next: data.next,
        previous: data.previous,
      }
    }
  } catch (error) {
    console.error('Failed to load categories:', error)
  } finally {
    loading.value = false
  }
}

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  await loadCategories(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
