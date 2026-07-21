<script setup>
import { computed, ref } from 'vue'
import { usePagination } from '../../composables/usePagination'
import Pagination from '../common/Pagination.vue'

const props = defineProps({
  items: { type: Array, required: true },
  emptyMessage: { type: String, default: 'Nothing here right now.' },
})

const COLUMNS = [
  { key: 'title', label: 'Item' },
  { key: 'you', label: 'You' },
  { key: 'friend', label: 'Friend' },
  { key: 'average', label: 'Average' },
  { key: 'watch_together_score', label: 'Watch-together score' },
]

const SORT_VALUE = {
  title: (item) => item.show_title.toLowerCase(),
  you: (item) => item.predicted_a,
  friend: (item) => item.predicted_b,
  average: (item) => (item.predicted_a + item.predicted_b) / 2,
  watch_together_score: (item) => item.watch_together_score,
}

const sortKey = ref('watch_together_score')
const sortDir = ref('desc')

const sortedItems = computed(() => {
  const getValue = SORT_VALUE[sortKey.value]
  const dir = sortDir.value === 'asc' ? 1 : -1
  return [...props.items].sort((a, b) => {
    const va = getValue(a)
    const vb = getValue(b)
    if (va < vb) return -1 * dir
    if (va > vb) return 1 * dir
    return 0
  })
})

function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}

const { page, totalPages, pagedItems } = usePagination(() => sortedItems.value, 10)
</script>

<template>
  <p v-if="items.length === 0" class="watch-together-table__empty">{{ emptyMessage }}</p>
  <template v-else>
    <table class="watch-together-table">
      <thead>
        <tr>
          <th
            v-for="col in COLUMNS"
            :key="col.key"
            class="watch-together-table__sortable-th"
            @click="setSort(col.key)"
          >
            {{ col.label }}
            <span v-if="sortKey === col.key">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in pagedItems" :key="item.item_id">
          <td>{{ item.show_title }}<span v-if="item.season_number"> S{{ item.season_number }}</span></td>
          <td>{{ item.predicted_a.toFixed(2) }}</td>
          <td>{{ item.predicted_b.toFixed(2) }}</td>
          <td>{{ ((item.predicted_a + item.predicted_b) / 2).toFixed(2) }}</td>
          <td>{{ item.watch_together_score.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
    <Pagination v-model="page" :total-pages="totalPages" />
  </template>
</template>

<style scoped>
.watch-together-table {
  width: 100%;
  border-collapse: collapse;
}
.watch-together-table th,
.watch-together-table td {
  text-align: left;
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid #333;
}
.watch-together-table__sortable-th {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.watch-together-table__sortable-th:hover {
  color: #fff;
}
.watch-together-table__empty {
  opacity: 0.75;
  font-size: 0.9rem;
}
</style>
