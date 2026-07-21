<script setup>
import ItemCard from './ItemCard.vue'

defineProps({
  group: { type: Object, required: true }, // { show_title, items: [...] }
})
</script>

<template>
  <div class="show-group">
    <h3 class="show-group__title">{{ group.show_title }}</h3>
    <ItemCard v-for="item in group.items" :key="item.id" :item="item" />
  </div>
</template>

<style scoped>
.show-group {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}
.show-group__title {
  margin: 0 0 0.25rem;
  font-size: 1.05rem;
}
</style>
