<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true }, // FactorItemOut[]
})

const selectedItemId = ref(props.items[0]?.item_id ?? null)

const selectedItem = computed(() =>
  props.items.find((i) => i.item_id === selectedItemId.value),
)
</script>

<template>
  <div class="item-vector-viewer">
    <h3>Inspect an item's raw vector</h3>
    <select v-model="selectedItemId">
      <option v-for="item in items" :key="item.item_id" :value="item.item_id">
        {{ item.show_title }}{{ item.season_number ? ` S${item.season_number}` : '' }}
      </option>
    </select>

    <div v-if="selectedItem" class="item-vector-viewer__bars">
      <div v-for="(value, idx) in selectedItem.vector" :key="idx" class="item-vector-viewer__row">
        <span class="item-vector-viewer__label">f{{ idx }}</span>
        <div class="item-vector-viewer__track">
          <div
            class="item-vector-viewer__fill"
            :class="{ 'item-vector-viewer__fill--negative': value < 0 }"
            :style="{ width: Math.min(Math.abs(value) * 40, 100) + '%' }"
          />
        </div>
        <span class="item-vector-viewer__value">{{ value.toFixed(3) }}</span>
      </div>
      <p class="item-vector-viewer__bias">Item bias: {{ selectedItem.bias.toFixed(3) }}</p>
    </div>
  </div>
</template>

<style scoped>
.item-vector-viewer {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}
.item-vector-viewer__bars {
  margin-top: 0.75rem;
}
.item-vector-viewer__row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}
.item-vector-viewer__label {
  width: 2rem;
  opacity: 0.7;
  font-size: 0.85rem;
}
.item-vector-viewer__track {
  flex: 1;
  height: 8px;
  background: #222;
  border-radius: 4px;
  overflow: hidden;
}
.item-vector-viewer__fill {
  height: 100%;
  background: #46a758;
}
.item-vector-viewer__fill--negative {
  background: #e5484d;
}
.item-vector-viewer__value {
  width: 4rem;
  text-align: right;
  font-size: 0.85rem;
  opacity: 0.8;
}
.item-vector-viewer__bias {
  opacity: 0.7;
  font-size: 0.85rem;
}
</style>
