<template>
    <div class="px-4 bg-dark-800 rounded">
        <!-- Comment Header -->
        <div class="flex items-start justify-between mb-2 relative">
            <div class="flex items-center space-x-2">
                <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                    <span class="text-dark-900 font-medium text-xs">
                        {{ comment.author_info?.username?.charAt(0).toUpperCase() }}
                    </span>
                </div>
                <div>
                    <p class="font-medium text-dark-100">{{ comment.author_info?.username }}
                        <span class="text-xs text-dark-400">{{ formatDate(comment.created) }}</span>
                    </p>

                </div>
            </div>

            <!-- Options Button -->
            <div class="relative" ref="optionsMenuRef">
                <button @click="toggleOptions" class="text-dark-400 hover:text-dark-200 transition-colors p-1">
                    <IconCommentOptions />
                </button>

                <!-- Options Dropdown -->
                <div v-if="showOptions"
                    class="absolute right-0 mt-1 w-32 bg-dark-700 rounded shadow-lg py-1 z-10 border border-dark-600">
                    <template v-if="isAuthor">
                        <button @click="handleEdit"
                            class="block w-full text-left px-4 py-2 text-sm text-dark-200 hover:bg-dark-600 hover:text-primary-400">
                            Edit
                        </button>
                        <button @click="handleDelete"
                            class="block w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-dark-600 hover:text-red-400">
                            Delete
                        </button>
                    </template>
                    <template v-else>
                        <button @click="handleReport"
                            class="block w-full text-left px-4 py-2 text-sm text-dark-200 hover:bg-dark-600 hover:text-primary-400">
                            Report
                        </button>
                    </template>
                </div>
            </div>
        </div>

        <!-- Comment Content -->
        <div v-if="isEditing" class="mb-3">
            <textarea v-model="editContent" rows="3" class="form-input form-textarea mb-2 w-full"
                ref="editInputRef"></textarea>
            <div class="flex space-x-2">
                <BaseButton @click="saveEdit" size="sm" variant="primary" :loading="submittingEdit">
                    Save
                </BaseButton>
                <BaseButton @click="cancelEdit" size="sm" variant="secondary" :disabled="submittingEdit">
                    Cancel
                </BaseButton>
            </div>
        </div>
        <p v-else class="text-dark-200 mb-3">{{ comment.content }}</p>

        <!-- Comment Actions -->
        <div class="flex items-center space-x-4 text-sm">
            <!-- Reply Button -->
            <button v-if="authStore.isAuthenticated" @click="toggleReplyForm"
                class="text-primary-400 hover:text-primary-300 transition-colors">
                Reply
            </button>

            <!-- View Replies Button -->
            <button v-if="comment.replies_count > 0" @click="toggleReplies"
                class="text-primary-400 hover:text-primary-300 transition-colors">
                {{ showReplies ? 'Hide' : 'View' }}
                {{ comment.replies_count }}
                {{ comment.replies_count === 1 ? 'reply' : 'replies' }}
            </button>
        </div>

        <!-- Reply Form -->
        <CommentReplyForm v-if="showReplyForm" :loading="submittingReply" v-model:replyContent="replyContent"
            @cancel="toggleReplyForm()" @submit="handleReplySubmit()" />

        <!-- Nested Replies -->
        <div v-if="showReplies && commentReplies" class="mt-4 pl-8 space-y-3">
            <div v-if="loadingReplies" class="py-4">
                <LoadingSpinner text="Loading replies..." size="sm" />
            </div>
            <CommentItem v-else v-for="reply in commentReplies" :key="reply.id" :comment="reply"
                :postId="props.postId" />

        </div>

    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import CommentReplyForm from '@/components/posts/CommentReplyForm.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import type { CommentCreate, Comment as CommentType } from '@/services/comments'
import { useCommentsStore } from '@/stores/comments'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import IconCommentOptions from '@/components/icons/IconCommentOptions.vue'
import { formatDate } from '@/services/utils'

interface Props {
    comment: CommentType
    postId: number
}

const toast = useToast()
const authStore = useAuthStore()
const commentsStore = useCommentsStore()

const props = defineProps<Props>()

// Reply state
const showReplies = ref<boolean>(false)
const loadingReplies = ref<boolean>(false)
const commentReplies = ref<CommentType[]>([])


// Reply creation state
const showReplyForm = ref<boolean>(false)
const submittingReply = ref<boolean>(false)
const replyForms = ref<string>('')
const replyContent = ref<CommentCreate['content']>('')

// Options Menu states
const showOptions = ref<boolean>(false)
const optionsMenuRef = ref<HTMLElement | null>(null)

// Author check
const isAuthor = computed(() => {
    return authStore.user?.username &&
        props.comment.author_info?.username &&
        authStore.user.username === props.comment.author_info.username
})

// Comment edit states
const isEditing = ref<boolean>(false)
const editContent = ref<string>('')
const submittingEdit = ref<boolean>(false)
const editInputRef = ref<HTMLTextAreaElement | null>(null)

// Comment edit logic
const handleEdit = async () => {
    editContent.value = props.comment.content
    isEditing.value = true
    showOptions.value = false
    await nextTick()
    editInputRef.value?.focus()
}

const cancelEdit = () => {
    isEditing.value = false
    editContent.value = ''
}

const saveEdit = async () => {
    if (!editContent.value.trim()) return

    submittingEdit.value = true
    try {
        await commentsStore.updateComment(props.comment.id, {
            content: editContent.value
        })

        toast.success('Comment updated successfully')

        isEditing.value = false
        editContent.value = ''
    } catch (error) {
        console.error('Failed to update comment:', error)
        toast.error('Failed to update comment')
    } finally {
        submittingEdit.value = false
    }
}

// Comment delete logic
const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this comment?')) return

    try {
        await commentsStore.deleteComment(props.comment.id)
        toast.success('Comment deleted successfully')
    } catch (error) {
        console.error('Failed to delete comment:', error)
        toast.error('Failed to delete comment')
    }
    showOptions.value = false
}

// Comment report logic
const handleReport = () => {
    // TODO: Implement report functionality
    console.log('Report clicked')
    toast.info('Report submitted')
    showOptions.value = false
}

// Toggle replies visibility and fetch if needed
const toggleReplies = async () => {
    showReplies.value = !showReplies.value

    // Fetch replies if showing and not already loaded
    if (showReplies.value && commentReplies.value.length == 0) {
        loadingReplies.value = true
        try {
            const parentAndReplies = await commentsStore.fetchCommentReplies(props.comment.id)
            commentReplies.value = parentAndReplies.replies
        } catch (error) {
            console.error('Failed to load replies:', error)
            toast.error('Failed to load replies')
        } finally {
            loadingReplies.value = false
        }
    }
}

// Toggle reply form visibility
const toggleReplyForm = () => {
    showReplyForm.value = !showReplyForm.value
    if (!replyForms.value) {
        replyForms.value = ''
    }
}

async function handleReplySubmit() {
    if (!replyContent.value.trim()) return

    submittingReply.value = true
    try {
        const reply = await commentsStore.createComment({
            post_id: props.postId,
            content: replyContent.value,
            parent: props.comment.id,
        })
        commentReplies.value.unshift(reply)
        replyContent.value = ''
        toast.success('Reply posted successfully!')
    } catch (error) {
        console.error('Failed to post reply:', error)
        toast.error('Failed to post reply')
    } finally {
        submittingReply.value = false
    }
}

async function refreshReplies() {
    // Reload replies for this comment
    commentReplies.value = null
    if (showReplies.value) {
        await toggleReplies() // Hide
        await toggleReplies() // Show (reload)
    }
}

// Options menu logic
const handleClickOutside = (event: MouseEvent) => {
    if (showOptions.value && optionsMenuRef.value && !optionsMenuRef.value.contains(event.target as Node)) {
        showOptions.value = false
    }
}
const toggleOptions = () => {
    showOptions.value = !showOptions.value
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})


</script>
