<template>
    <div class="card">
        <div class="card-header">
            <h2 class="text-2xl font-bold text-dark-100">
                Comments ({{ commentsCount || 0 }})
            </h2>
        </div>

        <div class="card-body">
            <!-- Comment Form (if authenticated) -->
            <div v-if="authStore.isAuthenticated" class="mb-8">
                <form @submit.prevent="handleCommentSubmit">
                    <textarea v-model="commentForm.content" placeholder="Write a comment..." rows="3"
                        class="form-input form-textarea" required></textarea>
                    <div class="mt-3">
                        <BaseButton type="submit" variant="primary" :loading="submittingComment">
                            Post Comment
                        </BaseButton>
                    </div>
                </form>
            </div>
            <div v-else class="mb-8 p-4 bg-dark-800 rounded-lg border border-dark-700">
                <p class="text-dark-300 text-center">
                    <router-link to="/login" class="text-primary-500 hover:text-primary-400">
                        Sign in
                    </router-link>
                    to leave a comment
                </p>
            </div>

            <!-- Comments List -->
            <div v-if="loadingComments" class="py-8">
                <LoadingSpinner text="Loading comments..." />
            </div>
            <div v-else-if="comments.length > 0" class="space-y-4">
                <CommentItem v-for="comment in comments" :key="comment.id" :comment="comment" :postId="props.postId" />
            </div>
            <div v-else class="text-center py-8 text-dark-400">
                No comments yet. Be the first to comment!
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import { useCommentsStore } from '@/stores/comments'
import BaseButton from '@/components/ui/BaseButton.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import CommentItem from '@/components/posts/CommentItem.vue'

interface Props {
    postId: number
    commentsCount?: number
    loadingComments?: boolean
}

interface Emits {
    (e: 'commentAdded'): void
    (e: 'replyAdded'): void
}

const props = withDefaults(defineProps<Props>(), {
    commentsCount: 0,
    loadingComments: false
})

const emit = defineEmits<Emits>()

const toast = useToast()
const authStore = useAuthStore()
const commentsStore = useCommentsStore()

const comments = computed(() => {
    return commentsStore.comments || []
})

const commentForm = reactive({
    content: '',
})
const submittingComment = ref(false)


const handleCommentSubmit = async () => {
    if (!commentForm.content.trim()) return

    submittingComment.value = true
    try {
        await commentsStore.createComment({
            post_id: props.postId,
            content: commentForm.content,
        })
        commentForm.content = ''
        toast.success('Comment posted successfully!')
        emit('commentAdded')
    } catch (error) {
        console.error('Failed to post comment:', error)
        toast.error('Failed to post comment')
    } finally {
        submittingComment.value = false
    }
}

</script>
