import { defineStore } from 'pinia'
import * as notificationsApi from '../api/notifications'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    items: [],
    unreadCount: 0,
    loading: false,
  }),
  actions: {
    async fetchAll() {
      this.loading = true
      try {
        this.items = await notificationsApi.getNotifications()
        this.unreadCount = this.items.filter((n) => !n.read).length
      } catch {
        // silent - notifications are non-critical, next poll will retry
      } finally {
        this.loading = false
      }
    },
    async markAllRead() {
      if (this.unreadCount === 0) return
      this.items = this.items.map((n) => ({ ...n, read: true }))
      this.unreadCount = 0
      try {
        await notificationsApi.markAllRead()
      } catch {
        // next fetchAll() reconciles state if this failed
      }
    },
  },
})
