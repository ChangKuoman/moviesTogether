<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useFriendsStore } from '../stores/friends'
import { useModelStore } from '../stores/model'
import CompatibilityGauge from '../components/compatibility/CompatibilityGauge.vue'
import AgreementBreakdown from '../components/compatibility/AgreementBreakdown.vue'
import WatchTogetherTable from '../components/compatibility/WatchTogetherTable.vue'
import BothWatchedTable from '../components/compatibility/BothWatchedTable.vue'
import Pagination from '../components/common/Pagination.vue'
import { usePagination } from '../composables/usePagination'

const auth = useAuthStore()
const friendsStore = useFriendsStore()
const modelStore = useModelStore()

const friendId = ref(null)
const wCollab = ref(0.6)

const HYBRID_PER_PAGE = 10
const {
  page: hybridPage,
  totalPages: hybridTotalPages,
  pagedItems: hybridPagedItems,
} = usePagination(() => modelStore.hybrid?.items ?? [], HYBRID_PER_PAGE)
const hybridFillerRowCount = computed(() => HYBRID_PER_PAGE - hybridPagedItems.value.length)

const friendName = computed(
  () => friendsStore.friends.find((f) => f.id === friendId.value)?.name ?? 'friend',
)

const neitherWatched = computed(
  () => modelStore.watchTogether?.filter((i) => !i.rated_by_a && !i.rated_by_b) ?? [],
)
const youWatched = computed(
  () => modelStore.watchTogether?.filter((i) => i.rated_by_a && !i.rated_by_b) ?? [],
)
const friendWatched = computed(
  () => modelStore.watchTogether?.filter((i) => !i.rated_by_a && i.rated_by_b) ?? [],
)

onMounted(async () => {
  await friendsStore.fetchAll()
  friendId.value = friendsStore.friends[0]?.id ?? null
  refreshCompatibility()
  refreshWatchTogether()
  refreshHybrid()
})

function refreshCompatibility() {
  if (auth.currentUser?.id && friendId.value) {
    modelStore.fetchCompatibility(auth.currentUser.id, friendId.value)
  }
}

function refreshWatchTogether() {
  if (auth.currentUser?.id && friendId.value) {
    modelStore.fetchWatchTogether(auth.currentUser.id, friendId.value)
  }
}

function refreshHybrid() {
  modelStore.fetchHybrid(wCollab.value, 1 - wCollab.value)
}

watch(friendId, () => {
  refreshCompatibility()
  refreshWatchTogether()
})
watch(wCollab, refreshHybrid)
</script>

<template>
  <div>
    <h1>Analysis</h1>

    <section class="analysis-view__section">
      <h2>Compatibility</h2>

      <p v-if="friendsStore.friends.length === 0" class="analysis-view__empty">
        You need to be friends with someone to compare tastes — add a friend in the
        <RouterLink :to="{ name: 'friends' }">Friends</RouterLink> tab first.
      </p>
      <template v-else>
        <div class="analysis-view__pickers">
          <span>You vs</span>
          <select v-model="friendId">
            <option v-for="f in friendsStore.friends" :key="f.id" :value="f.id">{{ f.name }}</option>
          </select>
        </div>

        <p v-if="modelStore.compatibilityError" class="analysis-view__error">
          {{ modelStore.compatibilityError }}
        </p>
        <template v-if="modelStore.compatibility">
          <CompatibilityGauge
            :score-pct="modelStore.compatibility.score_pct"
            :overlap-count="modelStore.compatibility.overlap_count"
          />
          <AgreementBreakdown :compatibility="modelStore.compatibility" />

          <h3 class="analysis-view__subheading">Both watched</h3>
          <BothWatchedTable :items="modelStore.compatibility.both_watched" :friend-name="friendName" />
        </template>
      </template>
    </section>

    <section v-if="friendsStore.friends.length > 0" class="analysis-view__section">
      <h2>What to watch together</h2>
      <p class="analysis-view__intro">
        Ranked by the pick you'd both enjoy the most, not just whoever's favorite.
      </p>

      <p v-if="modelStore.watchTogetherError" class="analysis-view__error">
        {{ modelStore.watchTogetherError }}
      </p>
      <template v-else-if="modelStore.watchTogether">
        <h3 class="analysis-view__subheading">Neither of you has watched</h3>
        <WatchTogetherTable
          :items="neitherWatched"
          :friend-name="friendName"
          empty-message="Nothing unwatched by both of you right now."
        />

        <h3 class="analysis-view__subheading">You've watched, {{ friendName }} hasn't</h3>
        <WatchTogetherTable
          :items="youWatched"
          :friend-name="friendName"
          :empty-message="`Nothing you've rated that ${friendName} hasn't yet.`"
        />

        <h3 class="analysis-view__subheading">{{ friendName }} has watched, you haven't</h3>
        <WatchTogetherTable
          :items="friendWatched"
          :friend-name="friendName"
          :empty-message="`Nothing ${friendName} has rated that you haven't yet.`"
        />
      </template>
    </section>

    <section class="analysis-view__section">
      <h2>Hybrid recommendations</h2>
      <label class="analysis-view__slider">
        Collaborative <input v-model.number="wCollab" type="range" min="0" max="1" step="0.1" /> Content-based
      </label>
      <p class="analysis-view__weights">
        w_collab = {{ wCollab.toFixed(1) }}, w_content = {{ (1 - wCollab).toFixed(1) }}
      </p>

      <p v-if="modelStore.hybridError" class="analysis-view__error">{{ modelStore.hybridError }}</p>
      <table v-else-if="modelStore.hybrid" class="analysis-view__hybrid-table">
        <thead>
          <tr>
            <th>Item</th>
            <th>Collaborative</th>
            <th>Content</th>
            <th>Hybrid</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in hybridPagedItems" :key="item.item_id">
            <td>{{ item.show_title }}<span v-if="item.season_number"> S{{ item.season_number }}</span></td>
            <td>{{ item.collaborative_score.toFixed(2) }}</td>
            <td>{{ item.content_score.toFixed(2) }}</td>
            <td>{{ item.hybrid_score.toFixed(2) }}</td>
          </tr>
          <tr v-for="n in hybridFillerRowCount" :key="`filler-${n}`" class="analysis-view__filler-row">
            <td colspan="4">&nbsp;</td>
          </tr>
        </tbody>
      </table>
      <Pagination v-if="modelStore.hybrid" v-model="hybridPage" :total-pages="hybridTotalPages" always-show />
    </section>
  </div>
</template>

<style scoped>
.analysis-view__section {
  margin-bottom: 2rem;
}
.analysis-view__pickers {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.analysis-view__error {
  color: #e5484d;
}
.analysis-view__empty {
  opacity: 0.75;
}
.analysis-view__intro {
  opacity: 0.75;
  font-size: 0.9rem;
}
.analysis-view__slider {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.analysis-view__weights {
  opacity: 0.7;
  font-size: 0.85rem;
}
.analysis-view__hybrid-table {
  width: 100%;
  border-collapse: collapse;
}
.analysis-view__hybrid-table th,
.analysis-view__hybrid-table td {
  text-align: left;
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid #333;
}
.analysis-view__subheading {
  font-size: 1rem;
  opacity: 0.85;
  margin: 1.25rem 0 0.5rem;
}
.analysis-view__filler-row td {
  border-bottom-color: transparent;
}
</style>
