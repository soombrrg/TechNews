<template>
    <article class="featured-post">
        <span class="featured-badge">Featured Story</span>
        <h1>
            <router-link :to="`/posts/${post.slug}`">{{ post.title }}</router-link>
        </h1>
        <div class="featured-meta">
            <span v-if="post.author">By {{ post.author }}</span>
            <span v-if="post.created"> • {{ formatDate(post.created) }}</span>
            <span v-if="readTime"> • {{ readTime }} min read</span>
        </div>
        <p class="featured-excerpt">{{ excerpt }}</p>
        <router-link :to="`/posts/${post.slug}`" class="read-more-btn">
            Read Full Story
        </router-link>
    </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PostList } from '@/services/posts';


interface Props {
    post: PostList
}

const props = defineProps<Props>()

const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    })
}

const excerpt = computed(() => {
    const content = props.post.content || ''
    return content.length > 200 ? content.substring(0, 200) + '...' : content
})

const readTime = computed(() => {
    const content = props.post.content || ''
    const wordsPerMinute = 200
    const words = content.split(/\s+/).length
    return Math.ceil(words / wordsPerMinute)
})
</script>

<style scoped>
.featured-post {
    background: #1e2a3a;
    border-left: 4px solid #e94560;
    padding: 2rem;
    margin-bottom: 3rem;
    border-radius: 0.5rem;
}

.featured-badge {
    background: #e94560;
    color: white;
    padding: 0.375rem 0.875rem;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-block;
    margin-bottom: 1rem;
    border-radius: 0.25rem;
}

.featured-post h1 {
    font-family: 'Merriweather', serif;
    font-size: 2.5rem;
    margin-bottom: 1rem;
    line-height: 1.2;
}

.featured-post h1 a {
    color: #e4e6eb;
    text-decoration: none;
    transition: color 0.3s;
}

.featured-post h1 a:hover {
    color: #e94560;
}

.featured-meta {
    color: #9ca3af;
    margin-bottom: 1.5rem;
    font-size: 0.875rem;
}

.featured-excerpt {
    font-size: 1.125rem;
    line-height: 1.7;
    color: #d1d5db;
    margin-bottom: 1.5rem;
}

.read-more-btn {
    display: inline-block;
    background: #16213e;
    color: white;
    padding: 0.875rem 2rem;
    text-decoration: none;
    font-weight: 700;
    transition: background 0.3s;
    border-radius: 0.25rem;
}

.read-more-btn:hover {
    background: #e94560;
}
</style>
