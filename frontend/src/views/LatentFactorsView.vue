<script setup>
import { onMounted, ref } from 'vue'
import { useModelStore } from '../stores/model'
import FactorTable from '../components/latent-factors/FactorTable.vue'
import ItemVectorViewer from '../components/latent-factors/ItemVectorViewer.vue'

const modelStore = useModelStore()
const factorTopItems = ref([]) // [{ factor_index, top, bottom }]

onMounted(async () => {
  await modelStore.fetchFactors()
  if (modelStore.factors) {
    const results = await Promise.all(
      Array.from({ length: modelStore.factors.k }, (_, i) => modelStore.fetchFactorTopItems(i)),
    )
    factorTopItems.value = results
  }
})
</script>

<template>
  <div>
    <h1>Latent Factors</h1>
    <p class="latent-factors-view__intro">
      The model never tells us what these dimensions mean — but we can guess by looking at which
      items score highest and lowest on each one.
    </p>

    <p v-if="modelStore.factorsError" class="latent-factors-view__error">{{ modelStore.factorsError }}</p>

    <template v-if="modelStore.factors">
      <FactorTable
        v-for="ft in factorTopItems"
        :key="ft.factor_index"
        :factor-index="ft.factor_index"
        :top-items="ft.top"
        :bottom-items="ft.bottom"
      />
      <ItemVectorViewer :items="modelStore.factors.items" />
    </template>
  </div>
</template>

<style scoped>
.latent-factors-view__intro {
  opacity: 0.75;
}
.latent-factors-view__error {
  color: #e5484d;
}
</style>
