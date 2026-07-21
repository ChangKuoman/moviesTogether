<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const tabs = [
  { name: 'library', label: 'Library' },
  { name: 'recommender', label: 'Recommender' },
  { name: 'latent-factors', label: 'Latent Factors' },
  { name: 'movie-map', label: 'Movie Map' },
  { name: 'analysis', label: 'Analysis' },
  { name: 'friends', label: 'Friends' },
]

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <nav class="tab-nav">
    <div class="tab-nav__tabs">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.name"
        :to="{ name: tab.name }"
        class="tab-nav__link"
        active-class="tab-nav__link--active"
      >
        {{ tab.label }}
      </RouterLink>
    </div>
    <div class="tab-nav__user">
      <span>{{ auth.currentUser?.name }}</span>
      <button type="button" @click="handleLogout">Log out</button>
    </div>
  </nav>
</template>

<style scoped>
.tab-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #333;
}
.tab-nav__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
}
.tab-nav__link {
  text-decoration: none;
  color: inherit;
  opacity: 0.7;
  padding: 0.25rem 0.4rem;
  white-space: nowrap;
}
.tab-nav__link--active {
  opacity: 1;
  font-weight: 600;
  border-bottom: 2px solid currentColor;
}
.tab-nav__user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  white-space: nowrap;
}

@media (max-width: 480px) {
  .tab-nav__tabs {
    gap: 0.4rem 0.5rem;
    font-size: 0.85rem;
  }
}
</style>
