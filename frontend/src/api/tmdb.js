import client from './client'

export function getTmdbStatus() {
  return client.get('/tmdb/status').then((res) => res.data)
}

export function searchTmdb(query, type) {
  return client.get('/tmdb/search', { params: { q: query, type } }).then((res) => res.data)
}

export function getTvSeasons(tmdbId) {
  return client.get(`/tmdb/tv/${tmdbId}/seasons`).then((res) => res.data)
}

export function createItemFromTmdb(payload) {
  return client.post('/items/from-tmdb', payload).then((res) => res.data)
}
