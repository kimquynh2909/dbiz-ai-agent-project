<template>
  <div :class="[cardBaseClass, cardPaddingClass, props.description ? 'group relative' : '']">
    <div class="flex items-center justify-between gap-2 p-2">
      <div class="flex flex-col items-start min-w-0">
        <p :class="['text-gray-600 leading-tight', titleClass]" :title="title">{{ title }}</p>
        <p :class="['font-bold text-gray-900 mt-1 leading-none', valueClass]" :title="formattedValue">
          {{ formattedValue }}
        </p>
        <div v-if="change" :class="['flex items-center', changeMarginClass]">
          <component :is="changeIcon" 
                     :class="[changeClass, changeIconSizeClass]" />
          <span :class="[changeClass, changeTextClass, 'font-medium']">
            {{ Math.abs(change) }}%
          </span>
          <span :class="[subtitleClass, 'ml-1']">{{ subtitle }}</span>
        </div>
      </div>
      <div :class="[iconBgClass, iconWrapperClass, 'rounded-md flex items-center justify-center flex-shrink-0']">
        <component :is="icon" :class="[iconClass, iconSizeClass]" />
      </div>
    </div>
    <transition name="fade">
      <div
        v-if="props.description"
        class="pointer-events-none absolute left-0 top-full z-10 mt-2 w-56 rounded-lg bg-gray-900 px-3 py-2 text-xs text-gray-100 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
      >
        {{ props.description }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TrendingUp as TrendingUpIcon, TrendingDown as TrendingDownIcon } from 'lucide-vue-next'

// Props cho card thống kê
const props = defineProps({
  title: String, // tiêu đề
  value: [Number, String], // giá trị hiển thị
  description: { type: String, default: '' }, // mô tả hiển thị khi hover
  subtitle: String, // mô tả nhỏ
  change: Number, // phần trăm thay đổi
  icon: [Object, Function], // icon
  iconColor: { type: String, default: 'blue' }, // màu icon
  format: { type: String, default: 'number' }, // kiểu hiển thị
  compact: { type: Boolean, default: false } // kiểu hiển thị nhỏ gọn
})

// Định dạng giá trị hiển thị
const formattedValue = computed(() => {
  if (props.format === 'percent') return `${props.value}%`
  if (props.format === 'number' && typeof props.value === 'number') return props.value.toLocaleString()
  return props.value
})

const cardBaseClass = computed(() =>
  props.compact
    ? 'bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow'
    : 'bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow'
)
const cardPaddingClass = computed(() => (props.compact ? 'px-3 py-2' : 'px-5 py-4'))
const valueClass = computed(() => (props.compact ? 'text-base sm:text-lg' : 'text-2xl'))
const titleClass = computed(() => (props.compact ? 'text-[10px] font-semibold tracking-wide uppercase' : 'text-sm'))
const changeMarginClass = computed(() => (props.compact ? 'mt-1' : 'mt-2'))
const iconWrapperClass = computed(() => (props.compact ? 'p-1.5' : 'p-3'))
const iconSizeClass = computed(() => (props.compact ? 'w-5 h-5' : 'w-7 h-7'))
const changeIconSizeClass = computed(() => (props.compact ? 'w-3 h-3 mr-1' : 'w-4 h-4 mr-1'))
const changeTextClass = computed(() => (props.compact ? 'text-[11px]' : 'text-sm'))
const subtitleClass = computed(() => (props.compact ? 'text-[11px] text-gray-500' : 'text-sm text-gray-500'))

// Chọn icon tăng/giảm
const changeIcon = computed(() => props.change >= 0 ? TrendingUpIcon : TrendingDownIcon)

// Màu cho phần trăm tăng/giảm
const changeClass = computed(() => props.change >= 0 ? 'text-green-600' : 'text-red-600')

// Màu nền cho icon
const iconBgClass = computed(() => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    yellow: 'bg-yellow-100',
    purple: 'bg-purple-100',
    red: 'bg-red-100'
  }
  return colors[props.iconColor] || colors.blue
})

// Màu icon
const iconClass = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    purple: 'text-purple-600',
    red: 'text-red-600'
  }
  return colors[props.iconColor] || colors.blue
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
