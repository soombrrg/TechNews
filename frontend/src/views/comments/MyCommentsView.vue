<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-content">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">My Comments</h1>

      <!-- Filters -->
      <div class="card mb-8">
        <div class="card-body">
          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1">
              <BaseInput v-model="filters.search" placeholder="Search comments..." @input="handleSearch" />
            </div>
            <div class="w-full md:w-48">
              <select v-model="filters.ordering" class="form-select w-full" @change="handleFilterChange">
                <option value="-created">Newest First</option>
                <option value="created">Oldest First</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12">
        <LoadingSpinner size="lg" text="Loading your comments..." />
      </div>

      <!-- Comments List -->
      <div v-else-if="comments.length > 0">
        <div class="space-y-4">
          <div v-for="comment in comments" :key="comment.id" class="card">
            <div class="card-body">
              <!-- Post Info & Reply Status -->
              <div class="flex items-center justify-between mb-3">
                <router-link v-if="comment.post" :to="`/posts/${comment.post}`"
                  class="text-primary-500 hover:text-primary-400 font-medium text-sm">
                  On Post: {{ comment.post }}
                </router-link>
                <div class="flex items-center space-x-2">
                  <span v-if="comment.is_reply" class="text-xs bg-dark-700 text-dark-300 px-2 py-1 rounded-full">
                    Reply
                  </span>
                  <span v-if="!comment.is_active" class="text-xs bg-error-900 text-error-200 px-2 py-1 rounded-full">
                    Deleted
                  </span>
                </div>
              </div>

              <!-- Comment Content -->
              <p class="text-dark-200 mb-3">{{ comment.content }}</p>

              <!-- Meta Info -->
              <div class="flex items-center justify-between text-sm text-dark-500">
                <div class="flex items-center space-x-4">
                  <span :title="comment.created">{{ formatDate(comment.created) }}</span>
                  <span v-if="comment.modified" class="text-dark-400" :title="formatDate(comment.modified)">
                    (Edited)
                  </span>
                  <span v-if="comment.replies_count !== undefined && comment.replies_count > 0">
                    {{ comment.replies_count }}
                    {{ comment.replies_count === 1 ? 'reply' : 'replies' }}
                  </span>
                </div>

                <!-- Actions -->
                <div class="flex items-center space-x-2">
                  <button @click="handleEdit(comment)" class="text-primary-500 hover:text-primary-400">
                    Edit
                  </button>
                  <button @click="handleDelete(comment.id)" class="text-error-500 hover:text-error-400"
                    :disabled="deleting === comment.id">
                    {{ deleting === comment.id ? 'Deleting...' : 'Delete' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.count > 10" class="flex justify-center items-center space-x-4 mt-8">
          <button :disabled="!pagination.previous" @click="goToPage(currentPage - 1)" class="btn btn-outline btn-sm">
            Previous
          </button>
          <span class="text-dark-300"> Page {{ currentPage }} of {{ totalPages }} </span>
          <button :disabled="!pagination.next" @click="goToPage(currentPage + 1)" class="btn btn-outline btn-sm">
            Next
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">💬</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">No comments yet</h3>
        <p class="text-dark-400 mb-6">Start engaging with posts by leaving comments</p>
        <router-link to="/posts" class="btn btn-primary"> Browse Posts </router-link>
      </div>

      <!-- Edit Modal -->
      <div v-if="editingComment" class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4"
        @click.self="editingComment = null">
        <div class="card max-w-2xl w-full">
          <div class="card-header">
            <h3 class="text-xl font-bold text-dark-100">Edit Comment</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleUpdate">
              <textarea v-model="editForm.content" rows="4" class="form-input form-textarea" required></textarea>
              <div class="mt-4 flex space-x-4">
                <BaseButton type="submit" variant="primary" :loading="updating">
                  Update Comment
                </BaseButton>
                <button type="button" @click="editingComment = null" class="btn btn-outline">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useCommentsStore } from '@/stores/comments'
import type { Comment, MyCommentsQueryParams } from '@/services/comments'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { debounce } from 'lodash'

const toast = useToast()
const commentsStore = useCommentsStore()
const loading = ref(false)
const deleting = ref<number | null>(null)
const updating = ref(false)
const currentPage = ref(1)
const editingComment = ref<Comment | null>(null)
const pagination = computed(() => commentsStore.pagination)
const comments = computed(() => commentsStore.comments)

const editForm = reactive({
  content: '',
})

const filters = reactive<MyCommentsQueryParams>({
  search: '',
  ordering: '-created',
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.count / 10)
})

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const handleEdit = (comment: Comment) => {
  editingComment.value = comment
  editForm.content = comment.content
}

const handleUpdate = async () => {
  if (!editForm.content.trim() || !editingComment.value) return

  updating.value = true
  try {
    await commentsStore.updateComment(editingComment.value.id, {
      content: editForm.content,
    })
    toast.success('Comment updated successfully')
    editingComment.value = null
    await loadComments()
  } catch (error) {
    console.error('Failed to update comment:', error)
    toast.error('Failed to update comment')
  } finally {
    updating.value = false
  }
}

const handleDelete = async (commentId: number) => {
  if (!confirm('Are you sure you want to delete this comment?')) return

  deleting.value = commentId
  try {
    await commentsStore.deleteComment(commentId)
    toast.success('Comment deleted successfully')
    await loadComments()
  } catch (error) {
    console.error('Failed to delete comment:', error)
    toast.error('Failed to delete comment')
  } finally {
    deleting.value = null
  }
}

const loadComments = async (page = 1) => {
  loading.value = true
  try {
    const params: MyCommentsQueryParams = {
      page,
      ordering: filters.ordering,
    }
    if (filters.search) params.search = filters.search

    await Promise.all([
      commentsStore.fetchMyComments(params) || Promise.resolve(),
    ])
  } catch (error) {
    console.error('Failed to load comments:', error)
    toast.error('Failed to load comments')
  } finally {
    loading.value = false
  }
}

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  await loadComments(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleSearch = debounce(() => {
  currentPage.value = 1
  loadComments()
}, 300)

const handleFilterChange = () => {
  currentPage.value = 1
  loadComments()
}

onMounted(() => {
  loadComments()
})
</script>
