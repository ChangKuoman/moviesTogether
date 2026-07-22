<script setup>
import { computed, ref } from 'vue'
import { usePagination } from '../../composables/usePagination'
import Pagination from '../common/Pagination.vue'

const props = defineProps({
  items: { type: Array, required: true },
  friendName: { type: String, default: 'friend' },
})

const COLUMNS = computed(() => [
  { key: 'title', label: 'Item' },
  { key: 'you', label: 'You' },
  { key: 'friend', label: props.friendName },
  { key: 'diff', label: 'Difference' },
])

const SORT_VALUE = {
  title: (item) => item.show_title.toLowerCase(),
  you: (item) => item.user_a_rating,
  friend: (item) => item.user_b_rating,
  diff: (item) => item.diff,
}

const sortKey = ref('title')
const sortDir = ref('asc')

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
    sortDir.value = 'asc'
  }
}

const PER_PAGE = 10
const { page, totalPages, pagedItems } = usePagination(() => sortedItems.value, PER_PAGE)

// Keeps the table's height constant across pages, whether it has 1 item or 10 - otherwise a
// 3-row page looks broken sitting above a full-height page.
const fillerRowCount = computed(() => PER_PAGE - pagedItems.value.length)
</script>

<template>
  <p v-if="items.length === 0" class="both-watched-table__empty">
    Nothing you've both rated yet.
  </p>
  <template v-else>
    <table class="both-watched-table">
      <thead>
        <tr>
          <th
            v-for="col in COLUMNS"
            :key="col.key"
            class="both-watched-table__sortable-th"
            @click="setSort(col.key)"
          >
            {{ col.label }}
            <span v-if="sortKey === col.key">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in pagedItems" :key="item.item_id">
          <td>{{ item.show_title }}</td>
          <td>{{ item.user_a_rating }}</td>
          <td>{{ item.user_b_rating }}</td>
          <td>{{ item.diff }}</td>
        </tr>
        <tr v-for="n in fillerRowCount" :key="`filler-${n}`" class="both-watched-table__filler-row">
          <td :colspan="COLUMNS.length">&nbsp;</td>
        </tr>
      </tbody>
    </table>
    <Pagination v-model="page" :total-pages="totalPages" always-show />
  </template>
</template>

<style scoped>
.both-watched-table {
  width: 100%;
  border-collapse: collapse;
}
.both-watched-table th,
.both-watched-table td {
  text-align: left;
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid #333;
}
.both-watched-table__sortable-th {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.both-watched-table__sortable-th:hover {
  color: #fff;
}
.both-watched-table__empty {
  opacity: 0.75;
  font-size: 0.9rem;
}
.both-watched-table__filler-row td {
  border-bottom-color: transparent;
}
</style>
