<script setup>
import { ref } from 'vue'
import { useSiteAccessStore } from '../stores/siteAccess'

const passphrase = ref('')
const submitting = ref(false)

const siteAccess = useSiteAccessStore()

async function handleSubmit() {
  if (!passphrase.value) return
  submitting.value = true
  try {
    await siteAccess.verify(passphrase.value)
  } catch {
    // error message is surfaced via siteAccess.error
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="site-gate-view">
    <h1>MoviesTogether</h1>
    <p class="site-gate-view__subtitle">This app is private. Enter the shared passphrase to continue.</p>

    <form class="site-gate-view__form" @submit.prevent="handleSubmit">
      <label>
        Passphrase
        <input v-model="passphrase" type="password" autocomplete="off" required autofocus />
      </label>

      <p v-if="siteAccess.error" class="site-gate-view__error">{{ siteAccess.error }}</p>

      <button type="submit" :disabled="submitting">
        {{ submitting ? 'Checking...' : 'Continue' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.site-gate-view {
  max-width: 360px;
  margin: 4rem auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.site-gate-view__subtitle {
  opacity: 0.7;
  margin-top: -0.5rem;
}
.site-gate-view__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.site-gate-view__form label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.9rem;
}
.site-gate-view__error {
  color: #e5484d;
  margin: 0;
}
</style>
