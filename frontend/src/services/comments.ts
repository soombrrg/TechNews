import api from './api'
import type { components, operations } from '@/types/api'

export type CommentCreate = components['schemas']['CommentCreate']
export type CommentUpdate = components['schemas']['CommentUpdate']
export type CommentReplies = components['schemas']['CommentReplies']
export type PostComments = components['schemas']['PostComments']
export type PaginatedCommentList = components['schemas']['PaginatedCommentList']
export type CommentDetail = components['schemas']['CommentDetail']
export type Comment = components['schemas']['Comment']

// Query params from operations
export type CommentsQueryParams = operations['comments_list']['parameters']['query']
export type MyCommentsQueryParams = operations['comments_my_comments_list']['parameters']['query']

export const commentsService = {
  // Get comments list
  async getComments(params: CommentsQueryParams = {}): Promise<PaginatedCommentList> {
    const response = await api.get<PaginatedCommentList>('/api/v1/comments/', { params })
    return response.data
  },

  // Get single comment
  async getComment(id: number): Promise<CommentDetail> {
    const response = await api.get<CommentDetail>(`/api/v1/comments/${id}/`)
    return response.data
  },

  // Create comment
  async createComment(commentData: CommentCreate): Promise<CommentCreate> {
    const response = await api.post<CommentCreate>('/api/v1/comments/', commentData)
    return response.data
  },

  // Update comment
  async updateComment(id: number, commentData: CommentUpdate): Promise<CommentUpdate> {
    const response = await api.put<CommentUpdate>(`/api/v1/comments/${id}/`, commentData)
    return response.data
  },

  // Partial update comment
  async patchComment(id: number, commentData: Partial<CommentUpdate>): Promise<CommentUpdate> {
    const response = await api.patch<CommentUpdate>(`/api/v1/comments/${id}/`, commentData)
    return response.data
  },

  // Delete comment
  async deleteComment(id: number): Promise<void> {
    await api.delete(`/api/v1/comments/${id}/`)
  },

  // Get my comments
  async getMyComments(params: MyCommentsQueryParams = {}): Promise<PaginatedCommentList> {
    const response = await api.get<PaginatedCommentList>('/api/v1/comments/my-comments/', {
      params,
    })
    return response.data
  },

  // Get post comments
  async getPostComments(postId: number): Promise<PostComments> {
    const response = await api.get<PostComments>(`/api/v1/comments/post/${postId}/`)
    return response.data
  },

  // Get comment replies
  async getCommentReplies(commentId: number): Promise<CommentReplies> {
    const response = await api.get<CommentReplies>(`/api/v1/comments/${commentId}/replies/`)
    return response.data
  },
}

export default commentsService
