import client from './client'

export function getMyRatings() {
  return client.get('/ratings/me').then((res) => res.data)
}

export function getAllRatings() {
  return client.get('/ratings/all').then((res) => res.data)
}

export function upsertRating(itemId, rating) {
  return client.post('/ratings', { item_id: itemId, rating }).then((res) => res.data)
}

export function deleteRating(itemId) {
  return client.delete(`/ratings/${itemId}`)
}
