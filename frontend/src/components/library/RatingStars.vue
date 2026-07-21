<script setup>
const props = defineProps({
  modelValue: { type: Number, default: null },
})
const emit = defineEmits(['update:modelValue', 'clear'])

function handleClick(n) {
  if (props.modelValue === n) {
    emit('clear')
  } else {
    emit('update:modelValue', n)
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
      :class="{ 'rating-stars__star--filled': modelValue >= n }"
      :aria-label="modelValue === n ? `Clear rating` : `Rate ${n} star${n > 1 ? 's' : ''}`"
      :title="modelValue === n ? 'Click again to clear' : undefined"
      @click="handleClick(n)"
    >
      ★
    </button>
  </div>
</template>

<style scoped>
.rating-stars {
  display: inline-flex;
  gap: 0.15rem;
}
.rating-stars__star {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.3rem;
  line-height: 1;
  color: #555;
  padding: 0;
}
.rating-stars__star--filled {
  color: #f5b400;
}
</style>
