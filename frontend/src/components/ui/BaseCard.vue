<template>
  <div class="card">
    <div v-if="$slots.header || header" class="card-header">
      <slot name="header">
        <h3 class="text-lg font-semibold text-dark-100">{{ header }}</h3>
      </slot>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  header?: string
}

withDefaults(defineProps<Props>(), {
  header: ''
})
</script>
