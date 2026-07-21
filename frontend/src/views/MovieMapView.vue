<script setup>
import { onMounted, ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useModelStore } from '../stores/model'
import MapScatterChart from '../components/movie-map/MapScatterChart.vue'
import NeighborList from '../components/movie-map/NeighborList.vue'

const auth = useAuthStore()
const modelStore = useModelStore()
const selectedItem = ref(null)
const selectedNeighbors = ref([])
const scope = ref('friends') // 'friends' | 'everyone'

onMounted(() => {
  modelStore.fetchMovieMap(scope.value)
})

watch(scope, (value) => {
  modelStore.fetchMovieMap(value)
})

async function handleSelectItem(itemId) {
  const point = modelStore.movieMap.points.find((p) => p.item_id === itemId)
  selectedItem.value = point || null
  selectedNeighbors.value = await modelStore.fetchNeighbors(itemId)
}
</script>

<template>
  <div>
    <h1>Movie Map</h1>
    <p class="movie-map-view__intro">
      Each point is an item placed by its latent factors, flattened to 2D with PCA. Click a point
      to see its nearest neighbors.
    </p>

    <label class="movie-map-view__scope">
      Show taste points for
      <select v-model="scope">
        <option value="friends">You + friends</option>
        <option value="everyone">Everyone (anonymized)</option>
      </select>
    </label>

    <p v-if="modelStore.movieMapError" class="movie-map-view__error">{{ modelStore.movieMapError }}</p>

    <template v-if="modelStore.movieMap">
      <p v-if="modelStore.movieMap.warning" class="movie-map-view__warning">
        {{ modelStore.movieMap.warning }}
      </p>
      <p class="movie-map-view__variance">
        Explained variance: PC1 {{ (modelStore.movieMap.explained_variance[0] * 100).toFixed(0) }}%,
        PC2 {{ (modelStore.movieMap.explained_variance[1] * 100).toFixed(0) }}%
      </p>

      <MapScatterChart
        :points="modelStore.movieMap.points"
        :user-points="modelStore.movieMap.user_points"
        :current-user-id="auth.currentUser?.id"
        @select-item="handleSelectItem"
      />

      <NeighborList
        v-if="selectedItem"
        :title="selectedItem.show_title"
        :neighbors="selectedNeighbors"
      />
    </template>
  </div>
</template>

<style scoped>
.movie-map-view__intro {
  opacity: 0.75;
}
.movie-map-view__scope {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}
.movie-map-view__warning {
  color: #f5b400;
}
.movie-map-view__variance {
  opacity: 0.7;
  font-size: 0.85rem;
}
.movie-map-view__error {
  color: #e5484d;
}
</style>
