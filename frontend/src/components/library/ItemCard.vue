<script setup>
import { computed, ref } from 'vue'
import { useRatingsStore } from '../../stores/ratings'
import RatingStars from './RatingStars.vue'
import ItemDetailModal from './ItemDetailModal.vue'

const props = defineProps({
  item: { type: Object, required: true },
  showFullTitle: { type: Boolean, default: false },
})

const ratingsStore = useRatingsStore()
const showModal = ref(false)

const label = computed(() => {
  const suffix =
    props.item.type === 'season' ? `Season ${props.item.season_number}` : props.item.year || 'Movie'
  return props.showFullTitle ? `${props.item.show_title} — ${suffix}` : suffix
})

const currentRating = computed(() => ratingsStore.byItemId[props.item.id] ?? null)

function handleRate(n) {
  ratingsStore.rate(props.item.id, n)
}

function handleClear() {
  ratingsStore.unrate(props.item.id)
}
</script>

<template>
  <div class="item-card">
    <button type="button" class="item-card__info" @click="showModal = true">
      <span class="item-card__label">{{ label }}</span>
    </button>
    <RatingStars :model-value="currentRating" @update:model-value="handleRate" @clear="handleClear" />

    <ItemDetailModal v-if="showModal" :item="item" @close="showModal = false" />
  </div>
</template>

<style scoped>
.item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
}
.item-card__info {
  flex: 1;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.3rem 0.4rem;
  margin: -0.3rem -0.4rem 0 0;
  text-align: left;
  border-radius: 6px;
}
.item-card__info:hover {
  background: #222;
}
.item-card__label {
  opacity: 0.75;
  font-size: 0.9rem;
}
</style>
