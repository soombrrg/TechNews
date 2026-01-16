<template>

    <div v-if="loading" class="text-center py-4">
        <div class="loading-spinner"></div>
    </div>

    <div v-else-if="popularPosts.length > 0" class="sidebar-section">
        <h3 class="sidebar-title">Popular Posts</h3>
        <article v-for="post in popularPosts.slice(0, 5)" :key="post.id" class="sidebar-post">
            <h4><router-link :to="`/posts/${post.slug}`">{{ post.title }}</router-link></h4>
            <div class="sidebar-post-meta">{{ formatDate(post.created) }} • {{ post.views_count || 0 }} views • {{
                post.comments_count || 0 }} comments</div>
        </article>
    </div>

    <div v-else class="text-dark-500 text-sm text-center py-4">
        No popular posts yet
    </div>

</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePostsStore } from '@/stores/posts'

const postsStore = usePostsStore()
const loading = ref(false)

const popularPosts = computed(() => postsStore.popularPosts || [])

const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

onMounted(async () => {
    if (popularPosts.value.length === 0) {
        loading.value = true
        try {
            await postsStore.fetchPopularPosts()
        } catch (error) {
            console.error('Failed to load popular posts:', error)
        } finally {
            loading.value = false
        }
    }
})
</script>

<style scoped>
.sidebar-section {
    background: #1B1E1F;
    padding: 1.5rem;
    margin-bottom: 2rem;
    border-left: 4px solid #931127;
}

.sidebar-title {
    font-family: 'Merriweather', serif;
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
    font-weight: 700;
    color: #e4e6eb;
}

.sidebar-post {
    padding: 1rem 0;
    border-bottom: 1px solid #2d3748;
}

.sidebar-post:last-child {
    border-bottom: none;
}

.sidebar-post h4 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    line-height: 1.3;
}

.sidebar-post h4 a {
    color: #e4e6eb;
    text-decoration: none;
    transition: color 0.3s;
    font-weight: bold;
}

.sidebar-post h4 a:hover {
    color: #e94560;
}

.sidebar-post-meta {
    color: #A8A095;
    font-size: 0.75rem;
}
</style>
