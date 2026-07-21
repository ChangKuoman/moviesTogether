import client from './client'

export function register(name, password) {
  return client.post('/auth/register', { name, password }).then((res) => res.data)
}

export function login(name, password) {
  return client.post('/auth/login', { name, password }).then((res) => res.data)
}

export function me() {
  return client.get('/auth/me').then((res) => res.data)
}
