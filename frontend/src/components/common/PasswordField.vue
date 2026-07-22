<script setup>
import { ref } from 'vue'

defineOptions({ inheritAttrs: false })
defineProps({
  modelValue: { type: String, default: '' },
})
defineEmits(['update:modelValue'])

const visible = ref(false)
</script>

<template>
  <div class="password-field">
    <input
      :type="visible ? 'text' : 'password'"
      :value="modelValue"
      v-bind="$attrs"
      class="password-field__input"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <button
      type="button"
      class="password-field__toggle"
      :aria-label="visible ? 'Hide password' : 'Show password'"
      :title="visible ? 'Hide password' : 'Show password'"
      @click="visible = !visible"
    >
      <svg v-if="visible" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
        <circle cx="12" cy="12" r="3" />
      </svg>
      <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
        <circle cx="12" cy="12" r="3" />
        <line x1="3" y1="21" x2="21" y2="3" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.password-field {
  position: relative;
  display: flex;
}
.password-field__input {
  width: 100%;
  padding-right: 2.2rem;
}
.password-field__toggle {
  position: absolute;
  right: 0.1rem;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: none;
  padding: 0.3rem;
  display: flex;
  align-items: center;
  opacity: 0.6;
}
.password-field__toggle:hover {
  opacity: 1;
}
</style>
