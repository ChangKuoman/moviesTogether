<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, ScatterChart, GridComponent, TooltipComponent])

const props = defineProps({
  points: { type: Array, required: true },
  userPoints: { type: Array, required: true },
  currentUserId: { type: Number, default: null },
})
const emit = defineEmits(['select-item'])

function itemLabel(p) {
  return p.type === 'season' ? `${p.show_title} S${p.season_number}` : p.show_title
}

function userLabel(p) {
  if (p.name === 'Anonymous') return 'Anonymous'
  return p.user_id === props.currentUserId ? `${p.name} (you)` : `${p.name} (friend)`
}

const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: (params) => params.data.label,
  },
  grid: { left: 30, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'value', name: 'PC1', axisLabel: { show: false } },
  yAxis: { type: 'value', name: 'PC2', axisLabel: { show: false } },
  series: [
    {
      name: 'Items',
      type: 'scatter',
      symbolSize: 14,
      itemStyle: { color: '#5b8def' },
      data: props.points.map((p) => ({
        value: [p.x, p.y],
        label: itemLabel(p),
        itemId: p.item_id,
        kind: 'item',
      })),
    },
    {
      name: 'Users',
      type: 'scatter',
      symbol: 'diamond',
      symbolSize: 18,
      itemStyle: { color: '#f5b400' },
      data: props.userPoints.map((p) => ({
        value: [p.x, p.y],
        label: userLabel(p),
        userId: p.user_id,
        kind: 'user',
      })),
    },
  ],
}))

function handleClick(params) {
  if (params.data?.kind === 'item') {
    emit('select-item', params.data.itemId)
  }
}
</script>

<template>
  <VChart class="map-scatter-chart" :option="option" autoresize @click="handleClick" />
</template>

<style scoped>
.map-scatter-chart {
  height: 420px;
  width: 100%;
}
</style>
