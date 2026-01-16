<template>
    <article class="post-item">
        <!-- Thumbnail -->
        <router-link :to="`/posts/${post.slug}`" class="post-thumbnail">
            <img v-if="post.image" :src="post.image" :alt="post.title" class="w-full h-full object-cover" />
            <div v-else class="thumbnail-placeholder"></div>
        </router-link>

        <!-- Content -->
        <div class="post-info">
            <PostBadges :post="post" />
            <div v-if="post.category" class="post-category">{{ post.category }}</div>
            <h3>
                <router-link :to="`/posts/${post.slug}`">{{ post.title }}</router-link>
            </h3>
            <p class="post-excerpt">{{ excerpt }}</p>
            <div class="post-meta">
                <span v-if="post.author">By {{ post.author }}</span>
                <span v-if="post.created">{{ formatDate(post.created) }}</span>
                <span v-if="post.views_count"> • {{ post.views_count }} views</span>
                <span v-if="post.comments_count"> • {{ post.comments_count }} comments</span>
            </div>
        </div>
    </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PostList } from '@/services/posts'
import PostBadges from './PostBadges.vue'
import { formatDate } from '@/services/utils'

interface Props {
    post: PostList
}

const props = defineProps<Props>()


const excerpt = computed(() => {
    return props.post.content || ''
})


</script>

<style scoped>
.post-item {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 1.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #333;
    margin-bottom: 2rem;
}

.post-item:last-child {
    border-bottom: none;
}

.post-thumbnail {
    height: 180px;
    overflow: hidden;
    border-radius: 0;
}

.post-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.post-item:hover .post-thumbnail img {
    transform: scale(1.05);
}


.post-category {
    color: #EA4F69;
    font-size: 0.875rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.post-info h3 {
    font-family: 'Merriweather', serif;
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
    line-height: 1.3;
}

.post-info h3 a {
    color: #e4e6eb;
    text-decoration: none;
    transition: color 0.3s;
}

.post-info h3 a:hover {
    color: #9D1329;
}

.post-excerpt {
    color: #a19e9e;
    line-height: 1.6;
    margin-bottom: 1rem;
}

.post-meta {
    color: #a8a095e1;
    font-size: 0.9rem;
}

.thumbnail-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

@media (max-width: 1024px) {
    .post-item {
        grid-template-columns: 1fr;
    }
}
</style>
