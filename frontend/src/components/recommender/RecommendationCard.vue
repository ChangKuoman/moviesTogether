<script setup>
import ConfidenceBadge from './ConfidenceBadge.vue'

defineProps({
  recommendation: { type: Object, required: true },
})
</script>

<template>
  <div class="recommendation-card">
    <div class="recommendation-card__header">
      <h3>
        {{ recommendation.show_title }}
        <span v-if="recommendation.type === 'season'">S{{ recommendation.season_number }}</span>
      </h3>
      <span class="recommendation-card__predicted">{{ recommendation.predicted_rating.toFixed(1) }} ★</span>
    </div>
    <ConfidenceBadge
      :label="recommendation.confidence_label"
      :score="recommendation.confidence"
      :reason="recommendation.confidence_reason"
    />
    <p class="recommendation-card__explanation">{{ recommendation.explanation }}</p>
  </div>
</template>

<style scoped>
.recommendation-card {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}
.recommendation-card__header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.recommendation-card__header h3 {
  margin: 0;
  font-size: 1.05rem;
}
.recommendation-card__predicted {
  font-weight: 600;
  color: #f5b400;
}
.recommendation-card__explanation {
  margin: 0.4rem 0 0;
  opacity: 0.8;
  font-size: 0.9rem;
}
</style>
