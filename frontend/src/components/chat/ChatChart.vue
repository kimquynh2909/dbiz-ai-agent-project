<template>
  <div class="chat-chart-container">
    <div class="chart-wrapper">
      <canvas ref="canvasRef"></canvas>
    </div>
    <div v-if="summary" class="chart-summary">
      <div class="summary-item" v-if="summary.total_revenue_formatted">
        <span class="summary-icon">💰</span>
        <span class="summary-label">Tổng doanh thu:</span>
        <span class="summary-value">{{ summary.total_revenue_formatted }} VNĐ</span>
      </div>
      <div class="summary-item" v-if="summary.total_orders !== undefined">
        <span class="summary-icon">📦</span>
        <span class="summary-label">Tổng đơn hàng:</span>
        <span class="summary-value">{{ summary.total_orders }} đơn</span>
      </div>
      <div class="summary-item" v-if="summary.average_order_value_formatted">
        <span class="summary-icon">📈</span>
        <span class="summary-label">Trung bình/đơn:</span>
        <span class="summary-value">{{ summary.average_order_value_formatted }} VNĐ</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { Chart as ChartJS } from 'chart.js/auto'

const props = defineProps({
  chartType: { type: String, default: 'bar' },
  title: { type: String, default: '' },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) },
  summary: { type: Object, default: null }
})

const canvasRef = ref(null)
let chartInstance = null

// Merge default options with provided options
const mergedOptions = computed(() => {
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: !!props.title,
        text: props.title,
        font: {
          size: 14,
          weight: 'bold'
        },
        color: '#1f2937',
        padding: {
          top: 10,
          bottom: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(31, 41, 55, 0.95)',
        titleFont: { size: 13 },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            let value = context.parsed.y || context.parsed || 0
            return formatCurrency(value)
          }
        }
      }
    },
    scales: props.chartType === 'bar' || props.chartType === 'line' ? {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: function(value) {
            return formatCurrencyShort(value)
          },
          color: '#6b7280',
          font: { size: 11 }
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#6b7280',
          font: { size: 11 }
        }
      }
    } : undefined,
    animation: {
      duration: 800,
      easing: 'easeOutQuart'
    }
  }
  
  return { ...defaultOptions, ...props.options }
})

function formatCurrency(value) {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)} tỷ VNĐ`
  } else if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)} triệu VNĐ`
  } else if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)} nghìn VNĐ`
  }
  return `${value.toLocaleString('vi-VN')} VNĐ`
}

function formatCurrencyShort(value) {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(0)}B`
  } else if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(0)}M`
  } else if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K`
  }
  return value.toLocaleString('vi-VN')
}

const renderChart = () => {
  if (!canvasRef.value || !props.data) return
  if (chartInstance) chartInstance.destroy()
  
  const context = canvasRef.value.getContext('2d')
  chartInstance = new ChartJS(context, {
    type: props.chartType,
    data: props.data,
    options: mergedOptions.value
  })
}

onMounted(() => { 
  // Small delay to ensure container is properly sized
  setTimeout(renderChart, 50)
})

const deepWatchOptions = { deep: true }
watch(() => props.data, renderChart, deepWatchOptions)
watch(() => props.options, renderChart, deepWatchOptions)
watch(() => props.chartType, renderChart)
watch(() => props.title, renderChart)

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped>
.chat-chart-container {
  width: 100%;
  margin: 1rem 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 280px;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  flex: 1;
  min-width: 180px;
}

.summary-icon {
  font-size: 1.25rem;
}

.summary-label {
  font-size: 0.8rem;
  color: #6b7280;
  white-space: nowrap;
}

.summary-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
  margin-left: auto;
}

@media (max-width: 640px) {
  .chart-wrapper {
    height: 220px;
    padding: 0.75rem;
  }
  
  .chart-summary {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .summary-item {
    min-width: unset;
  }
}
</style>

