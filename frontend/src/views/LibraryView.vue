<script setup>
import { computed, onMounted, ref } from 'vue'
import { useItemsStore } from '../stores/items'
import { useRatingsStore } from '../stores/ratings'
import ItemSearchBar from '../components/library/ItemSearchBar.vue'
import ShowGroup from '../components/library/ShowGroup.vue'
import ItemCard from '../components/library/ItemCard.vue'
import Pagination from '../components/common/Pagination.vue'
import { usePagination } from '../composables/usePagination'

const itemsStore = useItemsStore()
const ratingsStore = useRatingsStore()

const sortBy = ref('title') // 'title' | 'rating' | 'date_added'
const filterBy = ref('all') // 'all' | 'rated' | 'unrated'

onMounted(() => {
  itemsStore.fetchTmdbStatus()
  itemsStore.fetchGrouped()
  ratingsStore.fetchMine()
})

function matchesFilter(itemId) {
  const isRated = ratingsStore.byItemId[itemId] != null
  if (filterBy.value === 'rated') return isRated
  if (filterBy.value === 'unrated') return !isRated
  return true
}

// Sorting by title keeps the existing "grouped by show" layout (already alphabetical,
// seasons already ordered within a group). Sorting by rating is inherently per-item, so it
// flattens the groups into a single ranked list instead.
const filteredGroups = computed(() =>
  itemsStore.groups
    .map((group) => ({
      ...group,
      items: group.items.filter((item) => matchesFilter(item.id)),
    }))
    .filter((group) => group.items.length > 0),
)

const filteredFlatItemsByRating = computed(() => {
  const flat = itemsStore.groups.flatMap((group) => group.items).filter((item) => matchesFilter(item.id))
  return flat.sort((a, b) => {
    const ratingA = ratingsStore.byItemId[a.id] ?? -1
    const ratingB = ratingsStore.byItemId[b.id] ?? -1
    return ratingB - ratingA
  })
})

const filteredFlatItemsByDateAdded = computed(() => {
  const flat = itemsStore.groups.flatMap((group) => group.items).filter((item) => matchesFilter(item.id))
  return flat.sort((a, b) => new Date(b.added_at) - new Date(a.added_at))
})

const FLAT_LISTS_BY_SORT = {
  rating: filteredFlatItemsByRating,
  date_added: filteredFlatItemsByDateAdded,
}

const isEmpty = computed(() =>
  sortBy.value === 'title' ? filteredGroups.value.length === 0 : activeList.value.length === 0,
)

// One pagination instance covering whichever list is currently on screen - paginating groups
// (10 shows per page) when sorted by title, or individual items (10 per page) for the other
// sort modes, since switching modes naturally resets back to page 1.
const activeList = computed(() =>
  sortBy.value === 'title' ? filteredGroups.value : FLAT_LISTS_BY_SORT[sortBy.value].value,
)
const { page, totalPages, pagedItems } = usePagination(() => activeList.value, 10)
</script>

<template>
  <div>
    <h1>Library</h1>
    <ItemSearchBar />

    <div class="library-view__controls">
      <label>
        Sort by
        <select v-model="sortBy">
          <option value="title">Title</option>
          <option value="rating">Rating</option>
          <option value="date_added">Date added</option>
        </select>
      </label>
      <label>
        Show
        <select v-model="filterBy">
          <option value="all">All</option>
          <option value="rated">Rated</option>
          <option value="unrated">Not rated yet</option>
        </select>
      </label>
    </div>

    <p v-if="itemsStore.loading">Loading...</p>
    <p v-else-if="itemsStore.error" class="library-view__error">{{ itemsStore.error }}</p>
    <p v-else-if="itemsStore.groups.length === 0">
      Nothing here yet — add a movie or show above and rate it 0.5-5.
    </p>
    <p v-else-if="isEmpty">Nothing matches this filter.</p>

    <template v-else-if="sortBy === 'title'">
      <ShowGroup v-for="group in pagedItems" :key="group.show_title" :group="group" />
    </template>
    <div v-else class="library-view__flat-list">
      <ItemCard
        v-for="item in pagedItems"
        :key="item.id"
        :item="item"
        show-full-title
      />
    </div>

    <Pagination v-if="!isEmpty" v-model="page" :total-pages="totalPages" />
  </div>
</template>

<style scoped>
.library-view__error {
  color: #e5484d;
}
.library-view__controls {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.library-view__controls label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.library-view__flat-list {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.25rem 1rem;
}
.library-view__flat-list :deep(.item-card) {
  border-bottom: 1px solid #333;
}
.library-view__flat-list :deep(.item-card:last-child) {
  border-bottom: none;
}
</style>
