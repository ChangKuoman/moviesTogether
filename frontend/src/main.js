import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useSiteAccessStore } from './stores/siteAccess'

const app = createApp(App)
app.use(createPinia())
app.use(router)

useAuthStore().init()
useSiteAccessStore().init()

window.addEventListener('auth:unauthorized', () => {
  useAuthStore().logout()
  router.push({ name: 'login' })
})

window.addEventListener('site-access:required', () => {
  useSiteAccessStore().clear()
})

app.mount('#app')
