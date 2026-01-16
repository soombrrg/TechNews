<template>
  <button :type="type" :class="buttonClasses" :disabled="disabled || loading" @click="handleClick">
    <div v-if="loading" class="loading-spinner mr-2"></div>
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  type?: 'button' | 'reset' | 'submit'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false,
  fullWidth: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const classes = ['btn']

  // Variant
  classes.push(`btn-${props.variant}`)

  // Size
  if (props.size !== 'md') {
    classes.push(`btn-${props.size}`)
  }

  // Full width
  if (props.fullWidth) {
    classes.push('w-full')
  }

  return classes.join(' ')
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
