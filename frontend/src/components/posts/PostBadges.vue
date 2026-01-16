<template>
    <div class="post-badges">
        <span v-if="isPinnedPost" class="badge badge-pinned">Pinned</span>
        <span v-if="isOwnPost" class="badge badge-yours">My</span>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PostList } from '@/services/posts'
import { useAuthStore } from '@/stores/auth'

interface Props {
    post: PostList
}

const props = defineProps<Props>()
const authStore = useAuthStore()

const isOwnPost = computed(() => {
    return authStore.user?.id === props.post.author
})

const isPinnedPost = computed(() => {
    return props.post.is_pinned
})
</script>

<style scoped>
.post-badges {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    border-radius: 0.25rem;
    letter-spacing: 0.5px;
}

.badge-pinned {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
}

.badge-yours {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: #ffffff;
}
</style>
