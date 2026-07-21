<script setup>
defineProps({
  compatibility: { type: Object, required: true }, // CompatibilityOut
})
</script>

<template>
  <div class="agreement-breakdown">
    <div class="agreement-breakdown__section">
      <h3>Where you agree</h3>
      <ul>
        <li v-for="a in compatibility.top_agreements" :key="a.item_id">
          {{ a.show_title }} — {{ a.user_a_rating }}★ vs {{ a.user_b_rating }}★
        </li>
      </ul>
      <p v-if="!compatibility.top_agreements.length">No overlapping ratings yet.</p>
    </div>

    <div class="agreement-breakdown__section">
      <h3>Where you disagree</h3>
      <ul>
        <li v-for="d in compatibility.top_disagreements" :key="d.item_id">
          {{ d.show_title }} — {{ d.user_a_rating }}★ vs {{ d.user_b_rating }}★
        </li>
      </ul>
      <p v-if="!compatibility.top_disagreements.length">No overlapping ratings yet.</p>
    </div>

    <div v-if="compatibility.genre_breakdown.length" class="agreement-breakdown__section">
      <h3>By genre</h3>
      <ul>
        <li v-for="g in compatibility.genre_breakdown" :key="g.genre">
          {{ g.genre }} — {{ g.user_a_avg }}★ vs {{ g.user_b_avg }}★
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.agreement-breakdown__section {
  margin-bottom: 1rem;
}
.agreement-breakdown__section h3 {
  font-size: 0.95rem;
  opacity: 0.8;
  margin: 0 0 0.35rem;
}
.agreement-breakdown__section ul {
  margin: 0;
  padding-left: 1.2rem;
}
</style>
