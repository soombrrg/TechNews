<template>
    <div class="min-h-screen bg-dark-950 py-12">
        <div class="container-narrow">
            <!-- Loading State -->
            <div v-if="loading" class="py-12">
                <LoadingSpinner size="lg" text="Loading post..." />
            </div>

            <!-- Post Content -->
            <div v-else-if="post">
                <!-- Back Button -->
                <button @click="$router.back()" class="btn btn-outline btn-sm mb-6">← Back</button>

                <!-- Post Section -->
                <PostDetail :post="post" :deleting="deleting" :toggling-pin="togglingPin" @delete="handleDelete"
                    @toggle-pin="handleTogglePin" />

                <!-- Comments Section -->
                <PostComments v-if="post.id" :post-id="post.id" :comments-count="post.comments_count"
                    :loading-comments="loadingComments" />
            </div>

            <!-- Error State -->
            <PostNotFound v-else />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { usePostsStore } from '@/stores/posts'
import { useCommentsStore } from '@/stores/comments'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PostDetail from '@/components/posts/PostDetail.vue'
import PostComments from '@/components/posts/PostComments.vue'
import PostNotFound from '@/components/posts/PostNotFound.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const postsStore = usePostsStore()
const commentsStore = useCommentsStore()

const loading = ref(true)
const loadingComments = ref(false)
const deleting = ref(false)
const togglingPin = ref(false)

const post = computed(() => postsStore.currentPost)

const handleTogglePin = async () => {
    if (!post.value?.slug) return

    togglingPin.value = true
    try {
        const result = await postsStore.togglePinStatus(post.value.slug)
        toast.success(result.msg || (result.is_pinned ? 'Post pinned successfully' : 'Post unpinned successfully'))
    } catch (error: unknown) {
        console.error('Failed to toggle pin status:', error)
        const err = error as { response?: { data?: { error?: string } } }
        toast.error(err.response?.data?.error || 'Failed to toggle pin status')
    } finally {
        togglingPin.value = false
    }
}

const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this post?')) return

    deleting.value = true
    try {
        if (!post.value?.slug) throw new Error('No post slug')

        await postsStore.deletePost(post.value.slug)
        toast.success('Post deleted successfully!')
        router.push('/posts')
    } catch (error) {
        console.error('Failed to delete post:', error)
        toast.error('Failed to delete post')
    } finally {
        deleting.value = false
    }
}

const loadComments = async () => {
    loadingComments.value = true
    try {
        if (!post.value?.id) return
        await commentsStore.fetchPostComments(post.value.id)
    } catch (error) {
        console.error('Failed to load comments:', error)
    } finally {
        loadingComments.value = false
    }
}

onMounted(async () => {
    const slug = route.params.slug as string
    try {
        await postsStore.fetchPost(slug)
        // console.log(post.value)
        if (post.value) {
            await loadComments()
        }
    } catch (error) {
        console.error('Failed to load post:', error)
        toast.error('Failed to load post')
    } finally {
        loading.value = false
    }
})
</script>
```
