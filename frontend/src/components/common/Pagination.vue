<script setup>
const page = defineModel({ type: Number, required: true })
defineProps({
  totalPages: { type: Number, required: true },
})
</script>

<template>
  <div v-if="totalPages > 1" class="pagination">
    <button type="button" :disabled="page <= 1" @click="page -= 1">Prev</button>
    <span class="pagination__label">Page {{ page }} of {{ totalPages }}</span>
    <button type="button" :disabled="page >= totalPages" @click="page += 1">Next</button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.75rem 0;
  font-size: 0.85rem;
}
.pagination__label {
  opacity: 0.75;
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
