<script setup>
defineProps({
  factorIndex: { type: Number, required: true },
  topItems: { type: Array, required: true },
  bottomItems: { type: Array, required: true },
})

function displayTitle(item) {
  return item.title
}
</script>

<template>
  <div class="factor-table">
    <h3>Factor {{ factorIndex }}</h3>
    <div class="factor-table__columns">
      <div>
        <h4>Highest loading</h4>
        <ol>
          <li v-for="item in topItems" :key="item.item_id">
            {{ displayTitle(item) }} ({{ item.loading.toFixed(2) }})
          </li>
        </ol>
      </div>
      <div>
        <h4>Lowest loading</h4>
        <ol>
          <li v-for="item in bottomItems" :key="item.item_id">
            {{ displayTitle(item) }} ({{ item.loading.toFixed(2) }})
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<style scoped>
.factor-table {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}
.factor-table__columns {
  display: flex;
  gap: 2rem;
}
.factor-table h4 {
  opacity: 0.7;
  font-size: 0.85rem;
  margin: 0.25rem 0;
}
.factor-table ol {
  margin: 0;
  padding-left: 1.2rem;
}
</style>
