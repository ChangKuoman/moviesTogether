<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import PasswordField from '../components/common/PasswordField.vue'

const mode = ref('login') // 'login' | 'register'
const name = ref('')
const password = ref('')
const submitting = ref(false)

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function handleSubmit() {
  if (!name.value || !password.value) return
  submitting.value = true
  try {
    if (mode.value === 'login') {
      await auth.login(name.value, password.value)
    } else {
      await auth.register(name.value, password.value)
    }
    router.push(route.query.redirect || { name: 'library' })
  } catch {
    // error message is surfaced via auth.error
  } finally {
    submitting.value = false
  }
}

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  auth.error = null
}
</script>

<template>
  <div class="login-view">
    <h1>MoviesTogether</h1>
    <p class="login-view__subtitle">
      {{ mode === 'login' ? 'Log in to rate and get recommendations' : 'Create an account to join the group' }}
    </p>

    <form class="login-view__form" @submit.prevent="handleSubmit">
      <label>
        Name
        <input v-model="name" type="text" autocomplete="username" required />
      </label>
      <label>
        Password
        <PasswordField v-model="password" autocomplete="current-password" required minlength="4" />
      </label>

      <p v-if="auth.error" class="login-view__error">{{ auth.error }}</p>

      <button type="submit" :disabled="submitting">
        {{ mode === 'login' ? 'Log in' : 'Create account' }}
      </button>
    </form>

    <button type="button" class="login-view__toggle" @click="toggleMode">
      {{ mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in' }}
    </button>
  </div>
</template>

<style scoped>
.login-view {
  max-width: 360px;
  margin: 4rem auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.login-view__subtitle {
  opacity: 0.7;
  margin-top: -0.5rem;
}
.login-view__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.login-view__form label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.9rem;
}
.login-view__error {
  color: #e5484d;
  margin: 0;
}
.login-view__toggle {
  background: none;
  border: none;
  color: inherit;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
}
</style>
