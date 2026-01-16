<template>
  <article class="post-card-grid">
    <router-link :to="`/posts/${post.slug}`" class="post-thumbnail-grid">
      <img v-if="post.image" :src="post.image" :alt="post.title" class="w-full h-full object-cover" />
      <div v-else class="thumbnail-placeholder"></div>
    </router-link>
    <div class="post-card-content">
      <PostBadges :post="post" />
      <div v-if="post.category" class="post-category">{{ post.category }}</div>
      <h3 class="post-title-grid">
        <router-link :to="`/posts/${post.slug}`">{{ post.title }}</router-link>
      </h3>
      <p class="post-excerpt-grid">{{ getExcerpt(post.content) }}</p>
      <div class="post-meta">
        <span v-if="post.author">By {{ post.author }}</span>
        <span v-if="post.created"> • {{ formatDate(post.created) }}</span>
      </div>
      <div class="post-meta">
        <span v-if="post.views_count">{{ post.views_count }} views</span>
        <span v-if="post.comments_count"> • {{ post.comments_count }} comments</span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { PostList } from '@/services/posts'
import PostBadges from './PostBadges.vue'
import { formatDate, getExcerpt } from '@/services/utils'

interface Props {
  post: PostList
}

defineProps<Props>()


</script>

<style scoped>
.post-card-grid {
  background: #1B1E1F;
  border-radius: 0.5rem;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.post-card-grid:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.post-thumbnail-grid {
  display: block;
  height: 200px;
  overflow: hidden;
}

.post-thumbnail-grid img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.post-card-grid:hover .post-thumbnail-grid img {
  transform: scale(1.05);
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.post-card-content {
  padding: 1.5rem;
}

.post-category {
  color: #EA4F69;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.post-title-grid {
  font-family: 'Merriweather', serif;
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  line-height: 1.3;
}

.post-title-grid a {
  color: #e4e6eb;
  text-decoration: none;
  transition: color 0.3s;
}

.post-title-grid a:hover {
  color: #9D1329;
}

.post-excerpt-grid {
  color: #a19e9e;
  line-height: 1.6;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.post-meta {
  color: #a8a095e1;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .post-thumbnail-grid {
    height: 180px;
  }
}
</style>
