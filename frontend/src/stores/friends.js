import { defineStore } from 'pinia'
import * as friendsApi from '../api/friends'

export const useFriendsStore = defineStore('friends', {
  state: () => ({
    friends: [],
    incoming: [],
    outgoing: [],
    loading: false,
    error: null,
    sendError: null,
  }),
  actions: {
    async fetchAll() {
      this.loading = true
      this.error = null
      try {
        const [friends, incoming, outgoing] = await Promise.all([
          friendsApi.getFriends(),
          friendsApi.getIncomingRequests(),
          friendsApi.getOutgoingRequests(),
        ])
        this.friends = friends
        this.incoming = incoming
        this.outgoing = outgoing
      } catch (e) {
        this.error = e.response?.data?.detail || 'Could not load friends'
      } finally {
        this.loading = false
      }
    },
    async sendRequest(recipientName) {
      this.sendError = null
      try {
        await friendsApi.sendFriendRequest(recipientName)
        await this.fetchAll()
      } catch (e) {
        this.sendError = e.response?.data?.detail || 'Could not send that request'
        throw e
      }
    },
    async accept(requestId) {
      await friendsApi.acceptRequest(requestId)
      await this.fetchAll()
    },
    async decline(requestId) {
      await friendsApi.declineRequest(requestId)
      await this.fetchAll()
    },
  },
})
