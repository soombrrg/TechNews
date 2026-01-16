<template>
    <div class="sidebar-section">
        <h3 class="sidebar-title">Categories</h3>

        <div v-if="loading" class="text-center py-4">
            <div class="loading-spinner"></div>
        </div>

        <ul v-else-if="categories.length > 0" class="categories-list">
            <li v-for="category in categories.slice(0, 5)" :key="category.id">
                <router-link :to="`/categories/${category.slug}`">
                    <span>{{ category.name }}</span>
                    <span class="category-count">{{ category.posts_count || 0 }}</span>
                </router-link>
            </li>
        </ul>

        <div v-else class="text-dark-500 text-sm text-center py-4">
            No categories yet
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePostsStore } from '@/stores/posts'

const postsStore = usePostsStore()
const loading = ref(false)

const categories = computed(() => postsStore.categories || [])

onMounted(async () => {
    if (categories.value.length === 0) {
        loading.value = true
        try {
            await postsStore.fetchCategories()
        } catch (error) {
            console.error('Failed to load categories:', error)
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
    border-radius: 0;
}

.sidebar-title {
    font-family: 'Merriweather', serif;
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
    font-weight: 700;
    color: #e4e6eb;
}

.categories-list {
    list-style: none;
}

.categories-list li {
    margin-bottom: 0.75rem;
}

.categories-list a {
    color: #C8C3BC;
    text-decoration: none;
    display: flex;
    justify-content: space-between;
    padding: 0.5rem;
    border-radius: 0.25rem;
    transition: all 0.3s;
}

.categories-list a:hover {
    background: #16213e;
    color: #EA4F69;
}

.category-count {
    color: #A8A095;
}
</style>
