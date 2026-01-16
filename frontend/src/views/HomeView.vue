<template>
  <div class="min-h-screen">
    <div class="main-container">
      <!-- Main Content -->
      <main class="main-content">
        <!-- Featured Post Slider -->
        <FeaturedPostSlider :posts="sliderPosts" />

        <!-- Latest Articles -->
        <h2 class="section-title">Latest Articles</h2>

        <div v-if="loading" class="py-12 text-center">
          <LoadingSpinner size="lg" text="Loading posts..." />
        </div>

        <div v-else-if="recentPosts.length > 0" class="posts-list">
          <PostRow v-for="post in recentPosts" :key="post.id" :post="post" />
        </div>

        <div v-else class="py-12 text-center text-dark-400">
          No posts found.
        </div>
      </main>

      <!-- Sidebar -->
      <AppSidebar />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePostsStore } from '@/stores/posts'
import PostRow from '@/components/posts/PostRow.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import FeaturedPostSlider from '@/components/posts/FeaturedPostSlider.vue'
import type { PostList, FeaturedPosts } from '@/services/posts'


const postsStore = usePostsStore()
const loading = ref<boolean>(true)

const recentPosts = computed<PostList[]>(() => postsStore.recentPosts || [])
const featuredPosts = computed<FeaturedPosts>(() => postsStore.featuredPosts || {})

const sliderPosts = computed<PostList[]>(() => {
  const featuredData = featuredPosts.value

  const pinned = featuredData.pinned || []
  const popular = featuredData.popular || []

  return [...pinned, ...popular]
})

const loadData = async () => {
  try {
    await Promise.all([
      postsStore.fetchRecentPosts() || Promise.resolve(),
      postsStore.fetchFeaturedPosts() || Promise.resolve()
    ])
  } catch (error) {
    console.error('Failed to load home page data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loadData()
})
</script>

<style scoped>
.main-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 3rem 2rem;
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 3rem;
}

.main-content {
  min-width: 0;
}

.section-title {
  font-family: 'Merriweather', serif;
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 3px solid #931127;
  color: #e4e6eb;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

@media (max-width: 1024px) {
  .main-container {
    grid-template-columns: 1fr;
    padding: 2rem 1rem;
  }

  .featured-post {
    min-height: auto;
  }

  .slider-controls {
    position: relative;
    bottom: auto;
    right: auto;
    margin-top: 1.5rem;
    justify-content: center;
  }
}
</style>
