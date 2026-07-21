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
    async removeItem(itemId) {
      await itemsApi.deleteItem(itemId)
      await this.fetchGrouped()
    },
  },
})
