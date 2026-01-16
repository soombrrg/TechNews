<template>
  <div class="min-h-screen bg-dark-950 py-12">
    <div class="container-narrow">
      <h1 class="text-3xl font-bold text-dark-100 mb-8">Edit Post</h1>

      <!-- Loading State -->
      <div v-if="initialLoading" class="py-12">
        <LoadingSpinner size="lg" text="Loading post..." />
      </div>

      <!-- Edit Form -->
      <BaseCard v-else-if="post">
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <!-- Title -->
            <BaseInput v-model="form.title" label="Title" type="text" placeholder="Enter post title"
              :error="errors.title" required />

            <!-- Image Upload -->
            <div class="mt-4">
              <label class="form-label">Featured Image</label>
              <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dark-600 border-dashed rounded-lg"
                :class="{ 'border-primary-500': isDragging }" @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop">
                <div class="space-y-1 text-center">
                  <div v-if="imagePreview" class="mb-4 relative group">
                    <img :src="imagePreview" alt="Preview" class="mx-auto h-48 object-cover rounded-lg" />
                    <button type="button" @click="removeImage"
                      class="absolute top-2 right-2 bg-error-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd"
                          d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                          clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                  <div v-else>
                    <svg class="mx-auto h-12 w-12 text-dark-400" stroke="currentColor" fill="none" viewBox="0 0 48 48"
                      aria-hidden="true">
                      <path
                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <div class="flex text-sm text-dark-400 justify-center">
                      <label for="file-upload"
                        class="relative cursor-pointer bg-dark-800 rounded-md font-medium text-primary-500 hover:text-primary-400 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                        <span>Upload a file</span>
                        <input id="file-upload" name="file-upload" type="file" class="sr-only" accept="image/*"
                          @change="handleFileChange" />
                      </label>
                      <p class="pl-1">or drag and drop</p>
                    </div>
                    <p class="text-xs text-dark-500">PNG, JPG, GIF up to 10MB</p>
                  </div>
                </div>
              </div>
              <p v-if="errors.image" class="form-error">{{ errors.image }}</p>
            </div>

            <!-- Category -->
            <div class="mt-4">
              <label class="form-label"> Category <span class="text-error-500">*</span> </label>
              <select v-model="form.category" class="form-select" required>
                <option value="">Select a category</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
              <p v-if="errors.category" class="form-error">{{ errors.category }}</p>
            </div>

            <!-- Content -->
            <div class="mt-4">
              <label class="form-label"> Content <span class="text-error-500">*</span> </label>
              <textarea v-model="form.content" rows="12" placeholder="Write your post content..."
                class="form-input form-textarea" required></textarea>
              <p v-if="errors.content" class="form-error">{{ errors.content }}</p>
            </div>

            <!-- Publication Status -->
            <div class="mt-4">
              <label class="form-label">Publication Status</label>
              <select v-model="form.publication_status" class="form-select">
                <option value="p">Published</option>
                <option value="d">Draft</option>
              </select>
            </div>

            <!-- Error Message -->
            <div v-if="errors.general" class="mt-4 p-3 bg-error-500/10 border border-error-500/30 rounded-lg">
              <p class="text-error-400 text-sm">{{ errors.general }}</p>
            </div>

            <!-- Actions -->
            <div class="mt-6 flex space-x-4">
              <BaseButton type="submit" variant="primary" :loading="loading" size="lg">
                Update Post
              </BaseButton>
              <router-link :to="`/posts/${post.slug}`" class="btn btn-outline btn-lg">
                Cancel
              </router-link>
            </div>
          </form>
        </div>
      </BaseCard>

      <!-- Error State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">😕</div>
        <h3 class="text-xl font-semibold text-dark-100 mb-2">Post not found</h3>
        <p class="text-dark-400 mb-6">The post you're trying to edit doesn't exist</p>
        <router-link to="/posts" class="btn btn-primary"> Browse Posts </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { usePostsStore } from '@/stores/posts'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import type { Category, PostCreateUpdate } from '@/services/posts'


const route = useRoute()
const router = useRouter()
const toast = useToast()
const postsStore = usePostsStore()
const initialLoading = ref(true)
const loading = ref(false)
const categories = ref<Category[]>([])
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)
const isDragging = ref(false)

const post = computed(() => postsStore.currentPost)

const form = reactive({
  title: '',
  content: '',
  category: '' as string | number,
  publication_status: 'p' as 'p' | 'd',
})

const errors = reactive({
  title: '',
  content: '',
  category: '',
  image: '',
  general: '',
})

interface ApiErrorResponse {
  response?: {
    data?: {
      title?: string | string[]
      content?: string | string[]
      category?: string | string[]
      image?: string | string[]
      detail?: string
    }
  }
}

const handleSubmit = async () => {
  // Reset errors
  Object.keys(errors).forEach((key) => {
    errors[key as keyof typeof errors] = ''
  })

  // Validate
  if (!form.title.trim()) {
    errors.title = 'Title is required'
    return
  }
  if (!form.content.trim()) {
    errors.content = 'Content is required'
    return
  }
  if (!form.category) {
    errors.category = 'Category is required'
    return
  }

  loading.value = true

  try {
    if (!post.value?.slug) throw new Error('No post slug')

    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('content', form.content)
    formData.append('category', String(form.category))
    formData.append('publication_status', form.publication_status)

    if (imageFile.value) {
      formData.append('image', imageFile.value)
    }

    // Cast FormData to PostCreateUpdate - API supports FormData for file uploads
    const updatedPost = await postsStore.updatePost(post.value.slug, formData as unknown as PostCreateUpdate)
    toast.success('Post updated successfully!')
    router.push(`/posts/${updatedPost.slug}`)
  } catch (error: unknown) {
    console.error('Failed to update post:', error)
    const err = error as ApiErrorResponse

    if (err.response?.data) {
      const data = err.response.data
      if (data.title) {
        errors.title = Array.isArray(data.title) ? data.title[0] : data.title
      }
      if (data.content) {
        errors.content = Array.isArray(data.content) ? data.content[0] : data.content
      }
      if (data.category) {
        errors.category = Array.isArray(data.category) ? data.category[0] : data.category
      }
      if (data.image) {
        errors.image = Array.isArray(data.image) ? data.image[0] : data.image
      }
      if (!errors.title && !errors.content && !errors.category && !errors.image) {
        errors.general = (data.detail as string) || 'Failed to update post'
      }
    } else {
      errors.general = 'Failed to update post. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const slug = route.params.slug as string
  try {
    // Load categories
    const cats = await postsStore.fetchCategories()
    if (Array.isArray(cats)) {
      categories.value = cats
    } else if ('results' in cats) {
      categories.value = cats.results || []
    }

    // Load post
    await postsStore.fetchPost(slug)

    if (post.value) {
      // Populate form
      form.title = post.value.title
      form.content = post.value.content
      form.category = post.value.category || ''
      form.publication_status = post.value.publication_status || 'p'

      if (post.value.image) {
        imagePreview.value = post.value.image
      }
    }
  } catch (error) {
    console.error('Failed to load post:', error)
    toast.error('Failed to load post')
  } finally {
    initialLoading.value = false
  }
})

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    processFile(input.files[0])
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    processFile(event.dataTransfer.files[0])
  }
}

const processFile = (file: File) => {
  if (!file.type.startsWith('image/')) {
    errors.image = 'Please upload an image file'
    return
  }

  if (file.size > 10 * 1024 * 1024) { // 10MB
    errors.image = 'Image size should be less than 10MB'
    return
  }

  errors.image = ''
  imageFile.value = file

  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  imageFile.value = null
  imagePreview.value = null
}
</script>
