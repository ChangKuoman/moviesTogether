import client from './client'

export function getNotifications() {
  return client.get('/notifications').then((res) => res.data)
}

export function getUnreadCount() {
  return client.get('/notifications/unread-count').then((res) => res.data.count)
}

export function markAllRead() {
  return client.post('/notifications/read').then((res) => res.data)
}
