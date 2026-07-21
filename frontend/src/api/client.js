import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
})

export function setAuthToken(token) {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete client.defaults.headers.common.Authorization
  }
}

export function setSiteAccessToken(token) {
  if (token) {
    client.defaults.headers.common['X-Site-Access'] = token
  } else {
    delete client.defaults.headers.common['X-Site-Access']
  }
}

client.interceptors.response.use(
  (response) => response,
  (error) => {
    // a failed site-access attempt (wrong passphrase) is handled locally by the siteAccess
    // store's own try/catch - it's not a per-user auth failure and shouldn't log anyone out.
    if (error.config?.url === '/site-access') {
      return Promise.reject(error)
    }
    if (error.response?.status === 401) {
      if (error.response?.data?.detail === 'Site access required') {
        window.dispatchEvent(new CustomEvent('site-access:required'))
      } else {
        // let the auth store decide what to do (e.g. logout) via a custom event
        window.dispatchEvent(new CustomEvent('auth:unauthorized'))
      }
    }
    return Promise.reject(error)
  },
)

export default client
