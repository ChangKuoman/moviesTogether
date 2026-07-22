import { defineStore } from 'pinia'
import * as itemsApi from '../api/items'
import * as tmdbApi from '../api/tmdb'

export const useItemsStore = defineStore('items', {
  state: () => ({
    groups: [], // [{ show_title, items: [...] }]
    loading: false,
    error: null,
    tmdbConfigured: false,
    tmdbSearchResults: [],
    tmdbSearching: false,
  }),
  actions: {
    async fetchGrouped() {
      this.loading = true
      this.error = null
      try {
        this.groups = await itemsApi.getItemsGrouped()
      } catch (e) {
        this.error = e.response?.data?.detail || 'Could not load the library'
      } finally {
        this.loading = false
      }
    },
    async fetchTmdbStatus() {
      try {
        const status = await tmdbApi.getTmdbStatus()
        this.tmdbConfigured = status.configured
      } catch {
        this.tmdbConfigured = false
      }
    },
    async searchTmdb(query, type) {
      this.tmdbSearching = true
      try {
        this.tmdbSearchResults = await tmdbApi.searchTmdb(query, type)
      } catch {
        this.tmdbSearchResults = []
      } finally {
        this.tmdbSearching = false
      }
    },
    async addManualItem(payload) {
      const item = await itemsApi.createItem(payload)
      await this.fetchGrouped()
      return item
    },
    async addFromTmdb(payload) {
      const item = await tmdbApi.createItemFromTmdb(payload)
      await this.fetchGrouped()
      return item
    },
    // Adds several seasons of the same show in one go (e.g. "select all seasons") - fires the
    // requests together and refetches the library once at the end, rather than once per season.
    // A season already in the library is not treated as a failure - it's a no-op either way.
    async addSeasonsFromTmdb(tmdbId, seasonNumbers) {
      const results = await Promise.allSettled(
        seasonNumbers.map((seasonNumber) =>
          tmdbApi.createItemFromTmdb({ tmdb_id: tmdbId, media_type: 'tv', season_number: seasonNumber }),
        ),
      )
      await this.fetchGrouped()
      const failures = results.filter(
        (r) => r.status === 'rejected' && !r.reason?.response?.data?.detail?.includes('already in your library'),
      )
      return { failedCount: failures.length, total: results.length }
    },
    async removeItem(itemId) {
      await itemsApi.deleteItem(itemId)
      await this.fetchGrouped()
    },
  },
})
