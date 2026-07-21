<script setup>
import { ref } from 'vue'
import { useItemsStore } from '../../stores/items'

const itemsStore = useItemsStore()

const title = ref('')
const type = ref('movie')
const seasonNumber = ref(1)
const year = ref(null)
const submitting = ref(false)
const error = ref(null)

async function handleSubmit() {
  error.value = null
  submitting.value = true
  try {
    await itemsStore.addManualItem({
      title: title.value,
      type: type.value,
      season_number: type.value === 'season' ? Number(seasonNumber.value) : null,
      year: year.value ? Number(year.value) : null,
    })
    title.value = ''
    seasonNumber.value = 1
    year.value = null
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not add this item'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="manual-item-form" @submit.prevent="handleSubmit">
    <input v-model="title" type="text" placeholder="Title (e.g. Interstellar, The Office)" required />

    <select v-model="type">
      <option value="movie">Movie</option>
      <option value="season">TV season</option>
    </select>

    <input
      v-if="type === 'season'"
      v-model="seasonNumber"
      type="number"
      min="1"
      placeholder="Season #"
      required
    />

    <input v-model="year" type="number" min="1870" max="2100" placeholder="Year (optional)" />

    <button type="submit" :disabled="submitting">Add</button>

    <p v-if="error" class="manual-item-form__error">{{ error }}</p>
  </form>
</template>

<style scoped>
.manual-item-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 1.5rem;
}
.manual-item-form__error {
  color: #e5484d;
  width: 100%;
  margin: 0;
}
</style>
