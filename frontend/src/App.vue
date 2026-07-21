<script setup>
import { useAuthStore } from './stores/auth'
import { useSiteAccessStore } from './stores/siteAccess'
import TabNav from './components/common/TabNav.vue'
import SiteGateView from './views/SiteGateView.vue'

const auth = useAuthStore()
const siteAccess = useSiteAccessStore()
</script>

<template>
  <SiteGateView v-if="!siteAccess.hasAccess" />
  <div v-else class="app-shell">
    <TabNav v-if="auth.isAuthenticated" />
    <main class="app-shell__content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell__content {
  padding: 1.5rem;
  max-width: 1100px;
  margin: 0 auto;
  box-sizing: border-box;
}

@media (max-width: 480px) {
  .app-shell__content {
    padding: 1rem;
  }
}
</style>
