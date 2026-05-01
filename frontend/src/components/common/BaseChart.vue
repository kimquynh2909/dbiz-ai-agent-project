<template>
  <div class="relative h-full w-full">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<script setup>
// import các hàm lifecycle và ChartJS
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Chart as ChartJS } from 'chart.js/auto'

// props cho chart
const props = defineProps({
  type: { type: String, required: true }, // loại chart
  data: { type: Object, required: true }, // dữ liệu
  options: { type: Object, default: () => ({}) }, // cấu hình chart
  plugins: { type: Array, default: () => [] } // plugin chart
})

// ref tới canvas
const canvasRef = ref(null)
let chartInstance = null

// hàm render chart
const renderChart = () => {
  if (!canvasRef.value || !props.data) return
  if (chartInstance) chartInstance.destroy()
  const context = canvasRef.value.getContext('2d')
  chartInstance = new ChartJS(context, {
    type: props.type,
    data: props.data,
    options: props.options,
    plugins: props.plugins
  })
}

// mount: vẽ chart lần đầu
onMounted(() => { renderChart() })

// watch: cập nhật chart khi props thay đổi
const deepWatchOptions = { deep: true }
watch(() => props.data, renderChart, deepWatchOptions)
watch(() => props.options, renderChart, deepWatchOptions)
watch(() => props.plugins, renderChart, deepWatchOptions)
watch(() => props.type, renderChart)

// unmount: hủy chart khi component bị destroy
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>
