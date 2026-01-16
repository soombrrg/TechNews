import { defineStore } from 'pinia'
import { ref } from 'vue'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import postsService, { type PostsQueryParams, type CategoriesQueryParams, type PostList, type PostDetail, type PostCreateUpdate, type Category, type FeaturedPosts, type TogglePostPinStatus } from '@/services/posts'

interface Pagination {
  count: number
  next: string | null
  previous: string | null
}

export const usePostsStore = defineStore('posts', () => {
  const posts = ref<PostList[]>([])
  const currentPost = ref<PostDetail | null>(null)
  const featuredPosts = ref<FeaturedPosts | null>(null)
  const popularPosts = ref<PostList[]>([])
  const recentPosts = ref<PostList[]>([])
  const categories = ref<Category[]>([])

  const loading = ref<boolean>(false)
  const error = ref<string | Record<string, unknown> | null>(null)
  const pagination = ref<Pagination>({
    count: 0,
    next: null,
    previous: null,
  })

  // Fetch posts list
  async function fetchPosts(params: PostsQueryParams = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await postsService.getPosts(params)
      posts.value = data.results || []
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
      error.value = errData.response?.data || 'Failed to fetch posts'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch single post
  async function fetchPost(slug: string) {
    loading.value = true
    error.value = null
    try {
      const data = await postsService.getPost(slug)
      currentPost.value = data
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to fetch post'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create post
  async function createPost(postData: PostCreateUpdate) {
    loading.value = true
    error.value = null
    try {
      const data = await postsService.createPost(postData)
      // Created post is PostDetail type, but we store PostList in array  
      // Category field differs: PostDetail has number, PostList has string
      // We push anyway since they're compatible for display purposes
      posts.value.unshift(data as unknown as PostList)
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to create post'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update post
  async function updatePost(slug: string, postData: PostCreateUpdate) {
    loading.value = true
    error.value = null
    try {
      const data = await postsService.updatePost(slug, postData)
      const index = posts.value.findIndex((p) => p.slug === slug)
      if (index !== -1) {
        posts.value[index] = data as unknown as PostList
      }
      if (currentPost.value?.slug === slug) {
        currentPost.value = data
      }
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to update post'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete post
  async function deletePost(slug: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await postsService.deletePost(slug)
      posts.value = posts.value.filter((p) => p.slug !== slug)
      if (currentPost.value?.slug === slug) {
        currentPost.value = null
      }
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to delete post'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch featured posts
  async function fetchFeaturedPosts() {
    try {
      const data = await postsService.getFeaturedPosts()
      featuredPosts.value = data
      return data
    } catch (err) {
      console.error('Failed to fetch featured posts:', err)
      throw err
    }
  }

  // Fetch popular posts
  async function fetchPopularPosts() {
    try {
      const data = await postsService.getPopularPosts()
      popularPosts.value = data
      return data
    } catch (err) {
      console.error('Failed to fetch popular posts:', err)
      throw err
    }
  }

  // Fetch recent posts
  async function fetchRecentPosts() {
    try {
      const data = await postsService.getRecentPosts()
      recentPosts.value = data
      return data
    } catch (err) {
      console.error('Failed to fetch recent posts:', err)
      throw err
    }
  }

  // Fetch categories
  async function fetchCategories(params: CategoriesQueryParams = {}) {
    try {
      const data = await postsService.getCategories(params)
      // data can be array or paginated response depending on backend
      if (Array.isArray(data)) {
        categories.value = data
      } else if ('results' in data) {
        categories.value = data.results || []
      }
      return data
    } catch (err) {
      console.error('Failed to fetch categories:', err)
      throw err
    }
  }

  // Toggle pin status
  async function togglePinStatus(slug: string) {
    loading.value = true
    error.value = null
    try {
      const data = await postsService.togglePinStatus(slug)
      // Update post in list
      const index = posts.value.findIndex((p) => p.slug === slug)
      if (index !== -1) {
        posts.value[index] = { ...posts.value[index], ...data.post } as unknown as PostList
      }
      return data
    } catch (err: unknown) {
      const errData = err as { response?: { data?: string | Record<string, unknown> } }
      error.value = errData.response?.data || 'Failed to toggle pin status'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    posts,
    currentPost,
    featuredPosts,
    popularPosts,
    recentPosts,
    categories,
    loading,
    error,
    pagination,
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    fetchFeaturedPosts,
    fetchPopularPosts,
    fetchRecentPosts,
    fetchCategories,
    togglePinStatus,
  }
})
