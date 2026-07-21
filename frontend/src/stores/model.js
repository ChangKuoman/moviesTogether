import { defineStore } from 'pinia'
import * as modelApi from '../api/model'

export const useModelStore = defineStore('model', {
  state: () => ({
    status: null,
    recommendations: [],
    loading: false,
    error: null,
    factors: null,
    factorsError: null,
    movieMap: null,
    movieMapError: null,
    neighborsByItemId: {},
    compatibility: null,
    compatibilityError: null,
    watchTogether: null,
    watchTogetherError: null,
    hybrid: null,
    hybridError: null,
  }),
  actions: {
    async fetchStatus() {
      try {
        this.status = await modelApi.getModelStatus()
      } catch {
        this.status = null
      }
    },
    async fetchRecommendations() {
      this.loading = true
      this.error = null
      try {
        this.recommendations = await modelApi.getRecommendations()
      } catch (e) {
        this.error =
          e.response?.data?.detail || 'Could not load recommendations'
        this.recommendations = []
      } finally {
        this.loading = false
      }
    },
    async retrain() {
      await modelApi.trainModel()
      await this.fetchStatus()
      await this.fetchRecommendations()
    },
    async fetchFactors() {
      this.factorsError = null
      try {
        this.factors = await modelApi.getFactors()
      } catch (e) {
        this.factors = null
        this.factorsError = e.response?.data?.detail || 'Could not load latent factors'
      }
    },
    async fetchFactorTopItems(factorIndex) {
      return modelApi.getFactorTopItems(factorIndex)
    },
    async fetchMovieMap(scope = 'friends') {
      this.movieMapError = null
      try {
        this.movieMap = await modelApi.getMovieMap(scope)
      } catch (e) {
        this.movieMap = null
        this.movieMapError = e.response?.data?.detail || 'Could not load the movie map'
      }
    },
    async fetchNeighbors(itemId) {
      const neighbors = await modelApi.getMovieMapNeighbors(itemId)
      this.neighborsByItemId = { ...this.neighborsByItemId, [itemId]: neighbors }
      return neighbors
    },
    async fetchCompatibility(userAId, userBId) {
      this.compatibilityError = null
      try {
        this.compatibility = await modelApi.getCompatibility(userAId, userBId)
      } catch (e) {
        this.compatibility = null
        this.compatibilityError = e.response?.data?.detail || 'Could not compute compatibility'
      }
    },
    async fetchWatchTogether(userAId, userBId) {
      this.watchTogetherError = null
      try {
        this.watchTogether = await modelApi.getWatchTogether(userAId, userBId)
      } catch (e) {
        this.watchTogether = null
        this.watchTogetherError = e.response?.data?.detail || 'Could not load watch-together picks'
      }
    },
    async fetchHybrid(wCollab, wContent) {
      this.hybridError = null
      try {
        this.hybrid = await modelApi.getHybrid(wCollab, wContent)
      } catch (e) {
        this.hybrid = null
        this.hybridError = e.response?.data?.detail || 'Could not load hybrid recommendations'
      }
    },
  },
})
