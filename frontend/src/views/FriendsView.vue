<script setup>
import { onMounted, ref } from 'vue'
import { useFriendsStore } from '../stores/friends'

const friendsStore = useFriendsStore()
const recipientName = ref('')
const sending = ref(false)

onMounted(() => {
  friendsStore.fetchAll()
})

async function handleSend() {
  if (!recipientName.value.trim()) return
  sending.value = true
  try {
    await friendsStore.sendRequest(recipientName.value.trim())
    recipientName.value = ''
  } catch {
    // error surfaced via friendsStore.sendError
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div>
    <h1>Friends</h1>

    <form class="friends-view__send-form" @submit.prevent="handleSend">
      <input v-model="recipientName" type="text" placeholder="Username" required />
      <button type="submit" :disabled="sending">Send friend request</button>
    </form>
    <p v-if="friendsStore.sendError" class="friends-view__error">{{ friendsStore.sendError }}</p>

    <p v-if="friendsStore.loading">Loading...</p>
    <p v-else-if="friendsStore.error" class="friends-view__error">{{ friendsStore.error }}</p>

    <section class="friends-view__section">
      <h2>Incoming requests</h2>
      <p v-if="friendsStore.incoming.length === 0" class="friends-view__empty">No pending requests.</p>
      <ul v-else class="friends-view__list">
        <li v-for="req in friendsStore.incoming" :key="req.id" class="friends-view__row">
          <span>{{ req.requester.name }}</span>
          <span class="friends-view__actions">
            <button type="button" @click="friendsStore.accept(req.id)">Accept</button>
            <button type="button" @click="friendsStore.decline(req.id)">Decline</button>
          </span>
        </li>
      </ul>
    </section>

    <section class="friends-view__section">
      <h2>Outgoing requests</h2>
      <p v-if="friendsStore.outgoing.length === 0" class="friends-view__empty">No pending requests.</p>
      <ul v-else class="friends-view__list">
        <li v-for="req in friendsStore.outgoing" :key="req.id" class="friends-view__row">
          <span>{{ req.recipient.name }}</span>
          <span class="friends-view__pending">Pending</span>
        </li>
      </ul>
    </section>

    <section class="friends-view__section">
      <h2>Your friends</h2>
      <p v-if="friendsStore.friends.length === 0" class="friends-view__empty">
        No friends yet — send a request above to start comparing tastes in Analysis.
      </p>
      <ul v-else class="friends-view__list">
        <li v-for="friend in friendsStore.friends" :key="friend.id" class="friends-view__row">
          <span>{{ friend.name }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.friends-view__send-form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.friends-view__error {
  color: #e5484d;
}
.friends-view__section {
  margin-top: 1.5rem;
}
.friends-view__empty {
  opacity: 0.7;
  font-size: 0.9rem;
}
.friends-view__list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.friends-view__row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid #333;
}
.friends-view__actions {
  display: flex;
  gap: 0.5rem;
}
.friends-view__pending {
  opacity: 0.6;
  font-size: 0.85rem;
}
</style>
