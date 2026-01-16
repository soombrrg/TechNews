<template>
    <div class="mt-4 pl-8">
        <form @submit.prevent="$emit('submit')">
            <textarea :value="replyContent"
                @input="$emit('update:replyContent', ($event.target as HTMLTextAreaElement).value)"
                placeholder="Write a reply..." rows="2" class="form-input form-textarea mb-2" required>
            </textarea>
            <div class="flex space-x-2">
                <BaseButton type="submit" variant="primary" size="sm" :loading="loading">
                    Post Reply
                </BaseButton>
                <button type="button" @click="$emit('cancel')" class="btn btn-outline btn-sm">
                    Cancel
                </button>
            </div>
        </form>
    </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/ui/BaseButton.vue'
import type { CommentCreate } from '@/services/comments';

interface Props {
    loading?: boolean
    replyContent: CommentCreate['content']
}

interface Emits {
    (e: 'cancel'): void
    (e: 'submit'): void
    (e: 'update:replyContent', value: string): void
}


const props = withDefaults(defineProps<Props>(), {
    loading: false
})

const emit = defineEmits<Emits>()

</script>