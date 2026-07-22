<script setup>
const props = defineProps({
  modelValue: { type: Number, default: null },
})
const emit = defineEmits(['update:modelValue', 'clear'])

function fillPercent(n) {
  if (!props.modelValue) return 0
  const fraction = props.modelValue - (n - 1)
  return Math.round(Math.max(0, Math.min(1, fraction)) * 100)
}

// Left half of the star = X.5, right half = X - lets every star carry two selectable values
// without extra UI chrome.
function handleClick(n, event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const clickedLeftHalf = event.clientX - rect.left < rect.width / 2
  const value = clickedLeftHalf ? n - 0.5 : n

  if (props.modelValue === value) {
    emit('clear')
  } else {
    emit('update:modelValue', value)
  }
}
</script>

<template>
  <div class="rating-stars">
    <button
      v-for="n in 5"
      :key="n"
      type="button"
      class="rating-stars__star"
      :aria-label="modelValue === n ? `Clear rating` : `Rate ${n} star${n > 1 ? 's' : ''}`"
      title="Click the left half of a star for a half star"
      @click="handleClick(n, $event)"
    >
      <span class="rating-stars__star-bg">★</span>
      <span class="rating-stars__star-fill" :style="{ width: fillPercent(n) + '%' }">★</span>
    </button>
  </div>
</template>

<style scoped>
.rating-stars {
  display: inline-flex;
  gap: 0.15rem;
}
.rating-stars__star {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.3rem;
  line-height: 1;
  padding: 0;
}
.rating-stars__star-bg {
  color: #555;
}
.rating-stars__star-fill {
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  white-space: nowrap;
  color: #f5b400;
}
</style>
