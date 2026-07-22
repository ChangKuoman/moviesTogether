import { computed, ref, watch } from 'vue'

/**
 * itemsGetter is a function (not a ref) so this can paginate any computed source - the
 * page auto-resets to 1 whenever the underlying item count changes (e.g. a filter/sort change),
 * so you don't get stranded on an empty page. Watches items.length rather than the items array
 * itself - a computed source produces a brand new array reference on every recompute (e.g. just
 * re-sorting after an in-place rating edit), which would otherwise reset the page even though the
 * count didn't change.
 */
export function usePagination(itemsGetter, perPage = 10) {
  const page = ref(1)
  const items = computed(() => itemsGetter())
  const totalPages = computed(() => Math.max(1, Math.ceil(items.value.length / perPage)))

  watch(
    () => items.value.length,
    () => {
      page.value = 1
    },
  )

  const pagedItems = computed(() => {
    const start = (page.value - 1) * perPage
    return items.value.slice(start, start + perPage)
  })

  return { page, totalPages, pagedItems }
}
