import api from './api'
import type { components, operations } from '@/types/api'

// Type aliases from OpenAPI schema
export type PostCreateUpdate = components['schemas']['PostCreateUpdate']
export type PostDetail = components['schemas']['PostDetail']
export type Category = components['schemas']['Category']
export type FeaturedPosts = components['schemas']['FeaturedPosts']
export type PinnedPostsOnly = components['schemas']['PinnedPostsOnly']
export type TogglePostPinStatus = components['schemas']['TogglePostPinStatus']
export type PaginatedPostListList = components['schemas']['PaginatedPostListList']
export type PostList = components["schemas"]["PostList"]
export type PaginatedCategoryList = components['schemas']['PaginatedCategoryList']
export type PostsByCategory = components['schemas']['PostsByCategory']

// Query params from operations
export type PostsQueryParams = operations['posts_list']['parameters']['query']
export type CategoriesQueryParams = operations['posts_categories_list']['parameters']['query']

export const postsService = {
  // Get posts list
  async getPosts(params: PostsQueryParams = {}): Promise<PaginatedPostListList> {
    const response = await api.get<PaginatedPostListList>('/api/v1/posts/', { params })
    return response.data
  },

  // Get single post by slug
  async getPost(slug: string): Promise<PostDetail> {
    const response = await api.get<PostDetail>(`/api/v1/posts/${slug}/`)
    return response.data
  },

  // Create post
  async createPost(postData: PostCreateUpdate): Promise<PostDetail> {
    const response = await api.post<PostDetail>('/api/v1/posts/', postData)
    return response.data
  },

  // Update post
  async updatePost(slug: string, postData: PostCreateUpdate): Promise<PostDetail> {
    const response = await api.put<PostDetail>(`/api/v1/posts/${slug}/`, postData)
    return response.data
  },

  // Partial update post
  async patchPost(slug: string, postData: Partial<PostCreateUpdate>): Promise<PostDetail> {
    const response = await api.patch<PostDetail>(`/api/v1/posts/${slug}/`, postData)
    return response.data
  },

  // Delete post
  async deletePost(slug: string): Promise<void> {
    await api.delete(`/api/v1/posts/${slug}/`)
  },

  // Get my posts
  async getMyPosts(params: PostsQueryParams = {}): Promise<PaginatedPostListList> {
    const response = await api.get<PaginatedPostListList>('/api/v1/posts/my-posts/', {
      params,
    })
    return response.data
  },

  // Get featured posts
  async getFeaturedPosts(): Promise<FeaturedPosts> {
    const response = await api.get<FeaturedPosts>('/api/v1/posts/featured/')
    return response.data
  },

  // Get popular posts
  async getPopularPosts(): Promise<PostList[]> {
    const response = await api.get<PostList[]>('/api/v1/posts/popular/')
    return response.data
  },

  // Get recent posts
  async getRecentPosts(): Promise<PostList[]> {
    const response = await api.get<PostList[]>('/api/v1/posts/recent/')
    return response.data
  },

  // Get pinned posts
  async getPinnedPosts(): Promise<PinnedPostsOnly> {
    const response = await api.get<PinnedPostsOnly>('/api/v1/posts/pinned/')
    return response.data
  },

  // Toggle pin status
  async togglePinStatus(slug: string): Promise<TogglePostPinStatus> {
    const response = await api.post<TogglePostPinStatus>(`/api/v1/posts/toggle-pin-status/${slug}`)
    return response.data
  },

  // Categories
  async getCategories(params: CategoriesQueryParams = {}): Promise<PaginatedCategoryList> {
    const response = await api.get<PaginatedCategoryList>('/api/v1/posts/categories/', {
      params,
    })
    return response.data
  },

  async getCategory(slug: string): Promise<Category> {
    const response = await api.get<Category>(`/api/v1/posts/categories/${slug}`)
    return response.data
  },

  async createCategory(
    categoryData: Omit<Category, 'id' | 'slug' | 'created' | 'posts_count'>,
  ): Promise<Category> {
    const response = await api.post<Category>('/api/v1/posts/categories/', categoryData)
    return response.data
  },

  async updateCategory(slug: string, categoryData: Partial<Category>): Promise<Category> {
    const response = await api.put<Category>(`/api/v1/posts/categories/${slug}`, categoryData)
    return response.data
  },

  async deleteCategory(slug: string): Promise<void> {
    await api.delete(`/api/v1/posts/categories/${slug}`)
  },

  async getCategoryPosts(categorySlug: string): Promise<PostsByCategory> {
    const response = await api.get<PostsByCategory>(
      `/api/v1/posts/categories/${categorySlug}/posts/`,
    )
    return response.data
  },
}

export default postsService
