<template>
    <article class="card mb-8">
        <!-- Featured Image -->
        <div v-if="post.image"
            class="h-96 bg-gradient-to-br from-primary-600 to-primary-500 rounded-t-xl overflow-hidden">
            <img :src="post.image" :alt="post.title" class="w-full h-full object-cover" />
        </div>

        <div class="card-body">
            <!-- Category & Status -->
            <div class="flex items-center space-x-2 mb-4">
                <BaseBadge v-if="post.category_info" variant="primary">
                    {{ post.category_info.name }}
                </BaseBadge>
                <BaseBadge v-if="post.publication_status === 'd'" variant="warning">
                    Draft
                </BaseBadge>
                <BaseBadge v-if="post.is_pinned" variant="success">📌 Pinned</BaseBadge>
                <BaseBadge v-if="post.pinned_info?.pinned_at" variant="gray" class="text-xs">
                    Pinned {{ formatDate(post.pinned_info.pinned_at) }}
                </BaseBadge>
            </div>

            <!-- Title -->
            <h1 class="text-4xl font-bold text-dark-100 mb-4">{{ post.title }}</h1>

            <!-- Meta Info -->
            <div class="flex items-center justify-between mb-6 pb-6 border-b border-dark-700">
                <!-- Author Info -->
                <div v-if="post.author_info" class="flex items-center gap-3">
                    <div
                        class="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                        <!-- TODO: Add avatar image support -->
                        <span>
                            {{ post.author_info.username.charAt(0).toUpperCase() }}
                        </span>
                    </div>
                    <div>
                        <div class="font-medium text-dark-100 leading-tight">{{ post.author_info.username }}</div>
                        <div class="text-sm text-dark-400 mt-0.5">{{ formatDate(post.created) }}</div>
                    </div>
                </div>

                <!-- Stats -->
                <div class="flex items-center gap-6 text-dark-400">
                    <div class="flex items-center gap-2" title="Views">
                        <EyeIcon class="w-5 h-5" />
                        <span>{{ post.views_count || 0 }}</span>
                    </div>
                    <div class="flex items-center gap-2" title="Comments">
                        <ChatBubbleLeftIcon class="w-5 h-5" />
                        <span>{{ post.comments_count || 0 }}</span>
                    </div>
                    <button class="flex items-center gap-2 hover:text-primary-400 transition-colors" title="Share">
                        <ShareIcon class="w-5 h-5" />
                        <span>Share</span>
                    </button>
                </div>
            </div>

            <!-- Content -->
            <div class="prose prose-invert max-w-none">
                <p class="text-lg text-dark-200 whitespace-pre-wrap">{{ post.content }}</p>
            </div>


            <!-- Actions (if owner) -->
            <div v-if="isOwner" class="mt-8 pt-6 border-t border-dark-700">
                <div class="flex flex-wrap gap-4">
                    <router-link :to="`/posts/${post.slug}/edit`" class="btn btn-outline">
                        Edit Post
                    </router-link>
                    <button @click="$emit('delete')" class="btn btn-danger" :disabled="deleting">
                        {{ deleting ? 'Deleting...' : 'Delete Post' }}
                    </button>
                    <button v-if="post.can_pin" @click="$emit('togglePin')" class="btn btn-outline"
                        :disabled="togglingPin">
                        {{ togglingPin ? 'Processing...' : (post.is_pinned ? 'Unpin Post' : 'Pin Post') }}
                    </button>
                </div>
                <p v-if="post.can_pin && !post.is_pinned" class="text-sm text-dark-400 mt-2">
                    💡 Pin this post to keep it at the top of your profile
                </p>
            </div>
        </div>
    </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import { EyeIcon, ChatBubbleLeftIcon, ShareIcon } from '@heroicons/vue/24/outline'
import type { PostDetail as PostDetailType } from '@/services/posts'

interface Props {
    post: PostDetailType
    deleting?: boolean
    togglingPin?: boolean
}

interface Emits {
    (e: 'delete'): void
    (e: 'togglePin'): void
}

const props = withDefaults(defineProps<Props>(), {
    deleting: false,
    togglingPin: false
})

defineEmits<Emits>()

const authStore = useAuthStore()

const isOwner = computed(() => {
    return authStore.user && props.post.author === authStore.user.id
})

const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    })
}
</script>
