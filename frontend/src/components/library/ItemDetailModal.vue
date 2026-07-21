<script setup>
import { ref } from 'vue'
import { useItemsStore } from '../../stores/items'
import Modal from '../common/Modal.vue'

const props = defineProps({
  item: { type: Object, required: true },
})
const emit = defineEmits(['close'])

const itemsStore = useItemsStore()
const removing = ref(false)

async function handleRemove() {
  removing.value = true
  try {
    await itemsStore.removeItem(props.item.id)
    emit('close')
  } finally {
    removing.value = false
  }
}
</script>

<template>
  <Modal @close="$emit('close')">
    <div class="item-detail">
      <img v-if="item.poster_url" :src="item.poster_url" :alt="item.title" class="item-detail__poster" />

      <h2 class="item-detail__title">
        {{ item.title }}
        <span v-if="item.season_number"> — Season {{ item.season_number }}</span>
      </h2>
      <p class="item-detail__meta">
        {{ item.type === 'season' ? 'TV season' : 'Movie' }}
        <span v-if="item.year"> · {{ item.year }}</span>
        <span v-if="item.runtime"> · {{ item.runtime }} min</span>
      </p>

      <p v-if="item.genres && item.genres.length" class="item-detail__genres">
        {{ item.genres.join(', ') }}
      </p>

      <p v-if="item.overview" class="item-detail__overview">{{ item.overview }}</p>

      <p v-if="item.director" class="item-detail__line"><strong>Director:</strong> {{ item.director }}</p>
      <p v-if="item.cast && item.cast.length" class="item-detail__line">
        <strong>Cast:</strong> {{ item.cast.join(', ') }}
      </p>

      <button
        type="button"
        class="item-detail__remove"
        :disabled="removing"
        @click="handleRemove"
      >
        {{ removing ? 'Removing...' : 'Remove from your library' }}
      </button>
    </div>
  </Modal>
</template>

<style scoped>
.item-detail__poster {
  width: 140px;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.item-detail__title {
  margin: 0 0 0.25rem;
}
.item-detail__meta {
  opacity: 0.7;
  font-size: 0.9rem;
  margin: 0 0 0.75rem;
}
.item-detail__genres {
  opacity: 0.85;
  font-size: 0.85rem;
  margin: 0 0 0.75rem;
}
.item-detail__overview {
  margin: 0 0 0.75rem;
  line-height: 1.4;
}
.item-detail__line {
  font-size: 0.9rem;
  margin: 0 0 0.4rem;
  opacity: 0.9;
}
.item-detail__remove {
  margin-top: 1rem;
  background: none;
  border: 1px solid #e5484d;
  color: #e5484d;
  border-radius: 6px;
  padding: 0.5rem 0.9rem;
  cursor: pointer;
}
.item-detail__remove:hover {
  background: #e5484d;
  color: #fff;
}
.item-detail__remove:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
