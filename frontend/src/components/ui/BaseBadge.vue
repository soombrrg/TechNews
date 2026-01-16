<template>
  <span :class="badgeClasses">
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'gray'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'gray'
})

const badgeClasses = computed(() => {
  return `badge badge-${props.variant}`
})
</script>
