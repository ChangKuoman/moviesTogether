<script setup>
import { onMounted, ref } from 'vue'
import { useModelStore } from '../stores/model'
import RecommendationCard from '../components/recommender/RecommendationCard.vue'
import Pagination from '../components/common/Pagination.vue'
import { usePagination } from '../composables/usePagination'

const modelStore = useModelStore()
const retraining = ref(false)

const { page, totalPages, pagedItems } = usePagination(() => modelStore.recommendations, 10)

onMounted(() => {
  modelStore.fetchStatus()
  modelStore.fetchRecommendations()
})

async function handleRecompute() {
  retraining.value = true
  try {
    await modelStore.retrain()
  } finally {
    retraining.value = false
  }
}
</script>

<template>
  <div>
    <div class="recommender-view__header">
      <h1>Recommender</h1>
      <button type="button" :disabled="retraining" @click="handleRecompute">
        {{ retraining ? 'Recomputing...' : 'Recompute' }}
      </button>
    </div>

    <p v-if="modelStore.status" class="recommender-view__status">
      Model last trained on {{ modelStore.status.current_rating_count }} rating(s)
      <span v-if="modelStore.status.stale"> — new ratings since last train, results may be outdated</span>
    </p>

    <p v-if="modelStore.loading">Loading recommendations...</p>
    <p v-else-if="modelStore.error" class="recommender-view__error">{{ modelStore.error }}</p>
    <p v-else-if="modelStore.recommendations.length === 0">
      Nothing to recommend yet — rate a few more items in the Library.
    </p>

    <RecommendationCard
      v-for="rec in pagedItems"
      :key="rec.item_id"
      :recommendation="rec"
    />
    <Pagination v-model="page" :total-pages="totalPages" />
  </div>
</template>

<style scoped>
.recommender-view__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.recommender-view__status {
  opacity: 0.7;
  font-size: 0.9rem;
}
.recommender-view__error {
  color: #e5484d;
}
</style>
