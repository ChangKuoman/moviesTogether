import client from './client'

export function trainModel() {
  return client.post('/model/train').then((res) => res.data)
}

export function getModelStatus() {
  return client.get('/model/status').then((res) => res.data)
}

export function getRecommendations() {
  return client.get('/recommendations/me').then((res) => res.data)
}

export function getFactors() {
  return client.get('/model/factors').then((res) => res.data)
}

export function getFactorTopItems(factorIndex, n = 5) {
  return client
    .get(`/model/factors/${factorIndex}/top-items`, { params: { n } })
    .then((res) => res.data)
}

export function getMovieMap(scope = 'friends') {
  return client.get('/movie-map', { params: { scope } }).then((res) => res.data)
}

export function getMovieMapNeighbors(itemId, n = 5) {
  return client.get(`/movie-map/neighbors/${itemId}`, { params: { n } }).then((res) => res.data)
}

export function getCompatibility(userA, userB) {
  return client
    .get('/compatibility', { params: { user_a: userA, user_b: userB } })
    .then((res) => res.data)
}

export function getWatchTogether(userA, userB) {
  return client
    .get('/compatibility/watch-together', { params: { user_a: userA, user_b: userB } })
    .then((res) => res.data)
}

export function getHybrid(wCollab, wContent) {
  return client
    .get('/analysis/hybrid', { params: { w_collab: wCollab, w_content: wContent } })
    .then((res) => res.data)
}
