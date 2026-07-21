import { defineStore } from 'pinia'
import * as authApi from '../api/auth'
import { setAuthToken } from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    currentUser: JSON.parse(localStorage.getItem('currentUser') || 'null'),
    error: null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    init() {
      if (this.token) setAuthToken(this.token)
    },
    async register(name, password) {
      this.loading = true
      this.error = null
      try {
        const data = await authApi.register(name, password)
        this._applySession(data)
      } catch (e) {
        this.error = e.response?.data?.detail || 'Could not create account'
        throw e
      } finally {
        this.loading = false
      }
    },
    async login(name, password) {
      this.loading = true
      this.error = null
      try {
        const data = await authApi.login(name, password)
        this._applySession(data)
      } catch (e) {
        this.error = e.response?.data?.detail || 'Invalid name or password'
        throw e
      } finally {
        this.loading = false
      }
    },
    logout() {
      this.token = null
      this.currentUser = null
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
      setAuthToken(null)
    },
    _applySession(data) {
      this.token = data.access_token
      this.currentUser = data.user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('currentUser', JSON.stringify(data.user))
      setAuthToken(data.access_token)
    },
  },
})
