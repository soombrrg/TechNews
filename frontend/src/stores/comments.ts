import { defineStore } from 'pinia'
import { ref } from 'vue'
import commentsService, { type Comment, type CommentCreate, type CommentUpdate, type CommentsQueryParams } from '@/services/comments'

interface Pagination {
  count: number
  next: string | null
  previous: string | null
}

export const useCommentsStore = defineStore('comments', () => {
  const comments = ref<Comment[]>([])
  const loading = ref<boolean>(false)
  const error = ref<string | Record<string, unknown> | null>(null)
  const pagination = ref<Pagination>({
    count: 0,
    next: null,
    previous: null,
  })

  // Fetch comments
  async function fetchComments(params: CommentsQueryParams = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await commentsService.getComments(params)
      comments.value = data.results || []
      if (data.count !== undefined) {
        pagination.value = {
          count: data.count,
          next: data.next,
          previous: data.previous,
        }
      }
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch comments'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchMyComments(params: CommentsQueryParams = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await commentsService.getMyComments(params)
      comments.value = data.results || []
      if (data.count !== undefined) {
        pagination.value = {
          count: data.count,
          next: data.next,
          previous: data.previous,
        }
      }
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch comments'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch comments for a specific post
  async function fetchPostComments(postId: number) {
    loading.value = true
    error.value = null
    try {
      const data = await commentsService.getPostComments(postId)
      comments.value = data.comments || []
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch post comments'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create comment
  async function createComment(commentData: CommentCreate) {
    loading.value = true
    error.value = null
    try {
      const data = await commentsService.createComment(commentData)
      if (data.parent === null) {
        comments.value.unshift(data)
      }
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to create comment'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update comment
  async function updateComment(id: number, commentData: CommentUpdate) {
    loading.value = true
    error.value = null
    try {
      const data = await commentsService.updateComment(id, commentData)
      const index = comments.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        comments.value[index].content = data.content
      }
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to update comment'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete comment
  async function deleteComment(id: number): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await commentsService.deleteComment(id)
      comments.value = comments.value.filter((c) => c.id !== id)
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to delete comment'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch comment replies
  async function fetchCommentReplies(commentId: number) {
    try {
      const data = await commentsService.getCommentReplies(commentId)
      return data
    } catch (err) {
      console.error('Failed to fetch comment replies:', err)
      throw err
    }
  }

  async function fetchComment(commentId: number) {
    try {
      const data = await commentsService.getComment(commentId)
      return data
    } catch (err) {
      console.error('Failed to fetch comment:', err)
      throw err
    }
  }

  return {
    comments,
    loading,
    error,
    pagination,
    fetchComments,
    fetchComment,
    fetchPostComments,
    fetchMyComments,
    createComment,
    updateComment,
    deleteComment,
    fetchCommentReplies,
  }
})
