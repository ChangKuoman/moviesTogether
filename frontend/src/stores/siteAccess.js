import { defineStore } from 'pinia'
import * as siteAccessApi from '../api/siteAccess'
import { setSiteAccessToken } from '../api/client'

export const useSiteAccessStore = defineStore('siteAccess', {
  state: () => ({
    siteToken: localStorage.getItem('siteToken') || null,
    error: null,
    loading: false,
  }),
  getters: {
    hasAccess: (state) => !!state.siteToken,
  },
  actions: {
    init() {
      if (this.siteToken) setSiteAccessToken(this.siteToken)
    },
    async verify(passphrase) {
      this.loading = true
      this.error = null
      try {
        const data = await siteAccessApi.verifySiteAccess(passphrase)
        this.siteToken = data.site_token
        localStorage.setItem('siteToken', data.site_token)
        setSiteAccessToken(data.site_token)
      } catch (e) {
        this.error = e.response?.data?.detail || 'Incorrect passphrase'
        throw e
      } finally {
        this.loading = false
      }
    },
    clear() {
      this.siteToken = null
      localStorage.removeItem('siteToken')
      setSiteAccessToken(null)
    },
  },
})
