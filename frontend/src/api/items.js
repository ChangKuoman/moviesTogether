import client from './client'

export function getItems() {
  return client.get('/items').then((res) => res.data)
}

export function getItemsGrouped() {
  return client.get('/items/grouped').then((res) => res.data)
}

export function createItem(payload) {
  return client.post('/items', payload).then((res) => res.data)
}

export function updateItem(itemId, payload) {
  return client.patch(`/items/${itemId}`, payload).then((res) => res.data)
}

export function deleteItem(itemId) {
  return client.delete(`/items/${itemId}`)
}
