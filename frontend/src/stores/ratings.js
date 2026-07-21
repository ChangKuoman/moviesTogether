import { defineStore } from 'pinia'
import * as ratingsApi from '../api/ratings'

export const useRatingsStore = defineStore('ratings', {
  state: () => ({
    byItemId: {}, // { [item_id]: rating (1-5) }
    loading: false,
    error: null,
  }),
  actions: {
    async fetchMine() {
      this.loading = true
      this.error = null
      try {
        const ratings = await ratingsApi.getMyRatings()
        this.byItemId = Object.fromEntries(ratings.map((r) => [r.item_id, r.rating]))
      } catch (e) {
        this.error = e.response?.data?.detail || 'Could not load ratings'
      } finally {
        this.loading = false
      }
    },
    async rate(itemId, rating) {
      // optimistic update
      const previous = this.byItemId[itemId]
      this.byItemId = { ...this.byItemId, [itemId]: rating }
      try {
        await ratingsApi.upsertRating(itemId, rating)
      } catch (e) {
        this.byItemId = { ...this.byItemId, [itemId]: previous }
        throw e
      }
    },
    async unrate(itemId) {
      const previous = this.byItemId[itemId]
      const rest = { ...this.byItemId }
      delete rest[itemId]
      this.byItemId = rest
      try {
        await ratingsApi.deleteRating(itemId)
      } catch (e) {
        this.byItemId = { ...this.byItemId, [itemId]: previous }
        throw e
      }
    },
  },
})
