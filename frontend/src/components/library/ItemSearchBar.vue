<script setup>
import { ref, watch } from 'vue'
import { useItemsStore } from '../../stores/items'
import * as tmdbApi from '../../api/tmdb'
import ManualItemForm from './ManualItemForm.vue'

const itemsStore = useItemsStore()

const query = ref('')
const mediaType = ref('movie')
const seasons = ref(null) // populated once a TV show is picked
const pickedShow = ref(null)
const error = ref(null)
let debounceTimer = null

watch([query, mediaType], () => {
  seasons.value = null
  pickedShow.value = null
  clearTimeout(debounceTimer)
  if (!query.value.trim()) {
    itemsStore.tmdbSearchResults = []
    return
  }
  debounceTimer = setTimeout(() => {
    itemsStore.searchTmdb(query.value, mediaType.value)
  }, 300)
})

async function pickResult(result) {
  error.value = null
  if (mediaType.value === 'movie') {
    try {
      await itemsStore.addFromTmdb({ tmdb_id: result.tmdb_id, media_type: 'movie' })
      resetSearch()
    } catch (e) {
      error.value = e.response?.data?.detail || 'Could not add this movie'
    }
  } else {
    pickedShow.value = result
    seasons.value = await tmdbApi.getTvSeasons(result.tmdb_id)
  }
}

async function pickSeason(season) {
  error.value = null
  try {
    await itemsStore.addFromTmdb({
      tmdb_id: pickedShow.value.tmdb_id,
      media_type: 'tv',
      season_number: season.season_number,
    })
    resetSearch()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not add this season'
  }
}

function resetSearch() {
  query.value = ''
  seasons.value = null
  pickedShow.value = null
  itemsStore.tmdbSearchResults = []
}
</script>

<template>
  <div v-if="itemsStore.tmdbConfigured" class="item-search-bar">
    <div class="item-search-bar__controls">
      <input v-model="query" type="text" placeholder="Search movies or TV shows..." />
      <select v-model="mediaType">
        <option value="movie">Movie</option>
        <option value="tv">TV show</option>
      </select>
    </div>

    <p v-if="error" class="item-search-bar__error">{{ error }}</p>

    <ul v-if="!pickedShow && itemsStore.tmdbSearchResults.length" class="item-search-bar__results">
      <li v-for="result in itemsStore.tmdbSearchResults" :key="result.tmdb_id" @click="pickResult(result)">
        {{ result.title }} <span v-if="result.year">({{ result.year }})</span>
      </li>
    </ul>

    <div v-if="pickedShow && seasons" class="item-search-bar__seasons">
      <p>Pick a season of "{{ pickedShow.title }}":</p>
      <ul>
        <li v-for="season in seasons" :key="season.season_number" @click="pickSeason(season)">
          Season {{ season.season_number }} — {{ season.name }}
        </li>
      </ul>
    </div>
  </div>

  <ManualItemForm v-else />
</template>

<style scoped>
.item-search-bar__controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.item-search-bar__results,
.item-search-bar__seasons ul {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
}
.item-search-bar__results li,
.item-search-bar__seasons li {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}
.item-search-bar__results li:hover,
.item-search-bar__seasons li:hover {
  background: #222;
}
.item-search-bar__error {
  color: #e5484d;
}
</style>
