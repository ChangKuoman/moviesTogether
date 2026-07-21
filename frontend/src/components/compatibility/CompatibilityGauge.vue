<script setup>
defineProps({
  scorePct: { type: Number, required: true },
  overlapCount: { type: Number, required: true },
})
</script>

<template>
  <div class="compatibility-gauge">
    <div class="compatibility-gauge__score">{{ scorePct.toFixed(1) }}%</div>
    <p class="compatibility-gauge__overlap">
      Based on {{ overlapCount }} item(s) both of you have rated.
    </p>
  </div>
</template>

<style scoped>
.compatibility-gauge {
  text-align: center;
  padding: 1rem;
  border: 1px solid #333;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.compatibility-gauge__score {
  font-size: 2.5rem;
  font-weight: 700;
  color: #46a758;
}
.compatibility-gauge__overlap {
  opacity: 0.7;
  font-size: 0.85rem;
  margin: 0.25rem 0 0;
}
</style>
