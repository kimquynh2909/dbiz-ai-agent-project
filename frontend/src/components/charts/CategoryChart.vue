<template>
  <div class="relative h-64">
    <BaseChart type="doughnut" :data="data" :options="resolvedOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import BaseChart from '@/components/common/BaseChart.vue'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  }
})

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right'
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || ''
          const value = context.parsed
          const dataset = context.dataset?.data || []
          const total = dataset.reduce((a, b) => a + b, 0) || 1
          const percentage = ((value / total) * 100).toFixed(1)
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  }
}

const resolvedOptions = computed(() => ({
  ...defaultOptions,
  ...props.options
}))
</script>
