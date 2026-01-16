<template>
  <div class="form-group">
    <label v-if="label" :for="inputId" class="form-label">
      {{ label }}
      <span v-if="required" class="text-error-500">*</span>
    </label>
    <input :id="inputId" :type="type" :value="modelValue" :placeholder="placeholder" :disabled="disabled"
      :required="required" :class="inputClasses" @input="handleInput" @blur="handleBlur" />
    <p v-if="error" class="form-error">{{ error }}</p>
    <p v-else-if="helpText" class="form-help">{{ helpText }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue?: string | number
  label?: string
  type?: string
  placeholder?: string
  error?: string
  helpText?: string
  disabled?: boolean
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  type: 'text',
  placeholder: '',
  error: '',
  helpText: '',
  disabled: false,
  required: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
}>()

const inputId = computed(() => {
  return `input-${Math.random().toString(36).substr(2, 9)}`
})

const inputClasses = computed(() => {
  const classes = ['form-input']
  if (props.error) {
    classes.push('border-error-500 focus:border-error-500 focus:ring-error-500')
  }
  return classes.join(' ')
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}
</script>
