<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useNotificationsStore } from '../../stores/notifications'

const POLL_INTERVAL_MS = 30000

const MESSAGES = {
  friend_request_received: (name) => `${name} sent you a friend request`,
  friend_request_accepted: (name) => `${name} accepted your friend request`,
}

const store = useNotificationsStore()
const open = ref(false)
const rootEl = ref(null)
let pollHandle = null

function message(n) {
  return (MESSAGES[n.type] ?? (() => 'New notification'))(n.actor.name)
}

function toggle() {
  open.value = !open.value
  if (open.value) store.markAllRead()
}

function handleClickOutside(event) {
  if (open.value && rootEl.value && !rootEl.value.contains(event.target)) {
    open.value = false
  }
}

onMounted(() => {
  store.fetchAll()
  pollHandle = setInterval(() => store.fetchAll(), POLL_INTERVAL_MS)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  clearInterval(pollHandle)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="rootEl" class="notification-bell">
    <button type="button" class="notification-bell__trigger" aria-label="Notifications" @click="toggle">
      🔔
      <span v-if="store.unreadCount > 0" class="notification-bell__badge">{{ store.unreadCount }}</span>
    </button>

    <div v-if="open" class="notification-bell__panel">
      <p v-if="store.items.length === 0" class="notification-bell__empty">No notifications yet.</p>
      <ul v-else class="notification-bell__list">
        <li v-for="n in store.items" :key="n.id" class="notification-bell__item">
          <span>{{ message(n) }}</span>
          <time class="notification-bell__time">{{ new Date(n.created_at).toLocaleString() }}</time>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.notification-bell {
  position: relative;
}
.notification-bell__trigger {
  position: relative;
  border: none;
  background: none;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0.25rem;
}
.notification-bell__badge {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  background: #e5484d;
  color: #fff;
  border-radius: 999px;
  font-size: 0.65rem;
  line-height: 1;
  padding: 0.15rem 0.35rem;
  font-weight: 600;
}
.notification-bell__panel {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 0.4rem;
  width: 280px;
  max-height: 320px;
  overflow-y: auto;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.5rem;
  z-index: 10;
}
.notification-bell__empty {
  opacity: 0.7;
  font-size: 0.85rem;
  padding: 0.5rem;
}
.notification-bell__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.notification-bell__item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.85rem;
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
}
.notification-bell__time {
  font-size: 0.75rem;
  opacity: 0.6;
}
</style>
