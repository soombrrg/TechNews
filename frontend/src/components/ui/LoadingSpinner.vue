<template>
  <div class="flex justify-center items-center" :class="containerClass">
    <div :class="spinnerClasses"></div>
    <span v-if="text" class="ml-2 text-dark-300">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  text: '',
  color: 'primary'
})

const containerClass = computed(() => {
  const sizes: Record<string, string> = {
    sm: 'py-2',
    md: 'py-4',
    lg: 'py-8',
  }
  return sizes[props.size]
})

const spinnerClasses = computed(() => {
  const classes = ['loading-spinner']

  const sizes: Record<string, string> = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  }
  classes.push(sizes[props.size])

  if (props.color === 'primary') {
    classes.push('text-primary-500')
  } else if (props.color === 'white') {
    classes.push('text-white')
  }

  return classes.join(' ')
})
</script>
