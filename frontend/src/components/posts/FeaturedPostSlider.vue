<template>
    <div v-if="currentPost" class="featured-slider relative group">
        <article class="featured-post">
            <span class="featured-badge">Featured Story</span>
            <h1>
                <router-link :to="`/posts/${currentPost.slug}`">{{ currentPost.title }}</router-link>
            </h1>
            <div class="featured-meta">
                <span v-if="currentPost.author">By {{ currentPost.author }}</span>
                <span v-if="currentPost.created"> • {{ formatDate(currentPost.created) }} </span>
                <span v-if="currentPost.views_count"> • {{ currentPost.views_count }} views</span>
                <span v-if="currentPost.comments_count"> • {{ currentPost.comments_count }} comments</span>
                <span v-if="currentPost.content"> • {{ getReadTime(currentPost.content) }} min read</span>
            </div>
            <p class="featured-excerpt">{{ currentPost.content }}</p>
            <router-link :to="`/posts/${currentPost.slug}`" class="read-more-btn">Read Full Story</router-link>
        </article>

        <!-- Slider Controls -->
        <div v-if="posts.length > 1" class="slider-controls">
            <button @click="prevSlide" class="slider-btn prev-btn" aria-label="Previous slide">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
            </button>
            <button @click="nextSlide" class="slider-btn next-btn" aria-label="Next slide">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </button>

            <!-- Dots -->
            <div class="slider-dots">
                <button v-for="(_, index) in posts" :key="index" @click="goToSlide(index)"
                    :class="['slider-dot', { active: currentSlide === index }]"
                    :aria-label="`Go to slide ${index + 1}`"></button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { PostList } from '@/services/posts'

interface Props {
    posts: PostList[]
}

const props = defineProps<Props>()

const currentSlide = ref(0)

const currentPost = computed(() => {
    if (props.posts.length === 0) return null
    return props.posts[currentSlide.value]
})

const nextSlide = () => {
    currentSlide.value = (currentSlide.value + 1) % props.posts.length
}

const prevSlide = () => {
    currentSlide.value = (currentSlide.value - 1 + props.posts.length) % props.posts.length
}

const goToSlide = (index: number) => {
    currentSlide.value = index
}

// Reset slide when posts change
watch(() => props.posts, () => {
    currentSlide.value = 0
})

const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
    })
}

const getReadTime = (content?: string) => {
    if (!content) return 1
    const wordsPerMinute = 200
    const words = content.split(/\s+/).length
    return Math.ceil(words / wordsPerMinute)
}

</script>

<style scoped>
.featured-slider {
    position: relative;
    margin-bottom: 3rem;
}

.featured-post {
    background: #1B1E1F;
    border-left: 4px solid #931127;
    padding: 2rem;
    border-radius: 0;
    min-height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.featured-badge {
    background: #9D1329;
    color: white;
    padding: 0.375rem 0.875rem;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-block;
    margin-bottom: 1rem;
    border-radius: 0;
    align-self: flex-start;
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
    color: #9D1329;
}

.featured-meta {
    color: #A8A095;
    margin-bottom: 1.5rem;
    font-size: 0.875rem;
}

.featured-excerpt {
    font-size: 1.125rem;
    line-height: 1.7;
    color: #C8C3BC;
    margin-bottom: 1.5rem;
}

.read-more-btn {
    display: inline-block;
    background: #121A32;
    color: white;
    padding: 0.875rem 2rem;
    text-decoration: none;
    font-weight: 700;
    transition: background 0.3s;
    border-radius: 0;
    align-self: flex-start;
}

.read-more-btn:hover {
    background: #9D1329;
}

/* Slider Controls */
.slider-controls {
    position: absolute;
    bottom: 2rem;
    right: 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.slider-btn {
    background: #121A32;
    color: white;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;
}

.slider-btn:hover {
    background: #9D1329;
    border-color: #9D1329;
}

.slider-dots {
    display: flex;
    gap: 0.5rem;
    margin-left: 1rem;
}

.slider-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    cursor: pointer;
    transition: all 0.3s;
}

.slider-dot.active {
    background: #9D1329;
    transform: scale(1.2);
}

@media (max-width: 1024px) {
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
