<script setup>
defineProps({
  label: { type: String, required: true }, // 'low' | 'medium' | 'high'
  score: { type: Number, required: true },
  reason: { type: String, default: '' },
})
</script>

<template>
  <span class="confidence-badge" :class="`confidence-badge--${label}`" :title="reason">
    {{ label }} confidence ({{ Math.round(score * 100) }}%)
  </span>
</template>

<style scoped>
.confidence-badge {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  border: 1px solid currentColor;
  white-space: nowrap;
}
.confidence-badge--low {
  color: #e5484d;
}
.confidence-badge--medium {
  color: #f5b400;
}
.confidence-badge--high {
  color: #46a758;
}
</style>
