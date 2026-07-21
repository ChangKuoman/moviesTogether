<script setup>
defineProps({
  title: { type: String, required: true },
  neighbors: { type: Array, required: true }, // NeighborOut[]
})
</script>

<template>
  <div class="neighbor-list">
    <h3>Nearest to "{{ title }}"</h3>
    <ul>
      <li v-for="n in neighbors" :key="n.item_id">
        {{ n.show_title }} — similarity {{ n.similarity.toFixed(2) }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.neighbor-list {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-top: 1rem;
}
.neighbor-list ul {
  margin: 0;
  padding-left: 1.2rem;
}
</style>
