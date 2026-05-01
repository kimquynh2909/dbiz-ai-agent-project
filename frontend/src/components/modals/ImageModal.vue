<template>
  <ModalBase
    :visible="!!image"
    max-width="max-w-7xl"
    :panel-class="'bg-white rounded-2xl shadow-2xl w-[95vw] h-[75vh] flex flex-col overflow-hidden'"
    z-index="z-50"
    @close="emit('close')"
  >
    <div class="flex items-center justify-between px-6 py-4 border-b">
      <h3 class="text-lg font-semibold text-gray-900 text-center flex-1">{{ image?.title || image?.id }}</h3>
      <div class="flex items-center space-x-3">
        <span class="text-xs text-gray-500 hidden sm:block w-12 text-right">{{ zoomPercent }}%</span>
        <input
          type="range"
          :min="ZOOM_MIN"
          :max="ZOOM_MAX"
          step="0.1"
          :value="zoom"
          @input="handleZoomChange"
          class="w-28 sm:w-40 accent-blue-600"
        />
        <button @click.stop="zoomOut" :disabled="zoom <= ZOOM_MIN" class="p-2 rounded-full hover:bg-gray-100 text-gray-600 disabled:text-gray-300">
          <ZoomOutIcon class="w-4 h-4" />
        </button>
        <button @click.stop="resetZoom" class="p-2 rounded-full hover:bg-gray-100 text-gray-600">
          <RefreshIcon class="w-4 h-4" />
        </button>
        <button @click.stop="zoomIn" :disabled="zoom >= ZOOM_MAX" class="p-2 rounded-full hover:bg-gray-100 text-gray-600 disabled:text-gray-300">
          <ZoomInIcon class="w-4 h-4" />
        </button>
        <button @click="emit('close')" class="p-2 rounded-full hover:bg-gray-100 text-gray-500">
          <XIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <div class="relative flex-1 min-h-0">
      <div
        class="absolute inset-0 bg-gray-50 flex items-center justify-center p-4 overflow-hidden select-none"
        @wheel.prevent="handleWheel"
        @dblclick.stop="handleDoubleClick"
        @mousedown="startDrag"
        @mousemove="handleDrag"
        @mouseup="endDrag"
        @mouseleave="endDrag"
        @touchstart="startDrag"
        @touchmove.prevent="handleDrag"
        @touchend="endDrag"
        @touchcancel="endDrag"
      >
        <img
          v-if="image"
          :src="image.image_url || image.url || image.file_url"
          :alt="image.title || image.id"
          class="max-h-[90vh] w-full object-contain transition-transform"
          :style="transformStyles"
          draggable="false"
        />
      </div>

      <button
        @click.stop="showDetails = !showDetails"
        class="absolute top-4 right-4 px-3 py-1 text-xs font-medium rounded-full bg-black/60 text-white hover:bg-black/80 transition"
      >
        {{ showDetails ? 'Ẩn mô tả' : 'Xem mô tả' }}
      </button>

      <transition name="fade">
        <div
          v-if="showDetails"
          class="absolute top-6 right-6 w-[85vw] max-w-sm bg-white/95 backdrop-blur rounded-xl border border-gray-200 shadow-xl p-6 space-y-3 overflow-y-auto max-h-[calc(100%-3rem)]"
        >
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-sm font-semibold text-gray-800">Mô tả hình ảnh</h4>
            <button @click.stop="showDetails = false" class="text-gray-400 hover:text-gray-600">
              <XIcon class="w-4 h-4" />
            </button>
          </div>
          <p v-if="image?.description" class="text-sm text-gray-600 whitespace-pre-wrap">{{ image.description }}</p>
          <p v-else class="text-sm text-gray-400 italic">Không có mô tả cho hình ảnh này.</p>

          <div class="mt-4 space-y-2 text-xs text-gray-500">
            <p v-if="image?.page_number">Trang {{ image.page_number }}</p>
            <p v-if="image?.parent_document">Tài liệu: {{ image.parent_document }}</p>
            <p v-if="image?.alt_text">Alt text: {{ image.alt_text }}</p>
            <p v-if="image?.id">ID: {{ image.id }}</p>
          </div>
        </div>
      </transition>
    </div>
  </ModalBase>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { X as XIcon, ZoomIn as ZoomInIcon, ZoomOut as ZoomOutIcon, RefreshCw as RefreshIcon } from 'lucide-vue-next'
import ModalBase from '@/components/common/ModalBase.vue'

const props = defineProps({
  image: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const ZOOM_MIN = 0.5
const ZOOM_MAX = 4

const zoom = ref(1)
const offset = ref({ x: 0, y: 0 })
const showDetails = ref(false)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const dragStartOffset = ref({ x: 0, y: 0 })

const zoomPercent = computed(() => Math.round(zoom.value * 100))
const transformStyles = computed(() => ({
  transform: `scale(${zoom.value}) translate(${offset.value.x}px, ${offset.value.y}px)`,
  transformOrigin: 'center center',
  cursor: zoom.value > 1 ? (isDragging.value ? 'grabbing' : 'grab') : 'default',
  transition: isDragging.value ? 'none' : ''
}))

const clampZoom = (value) => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, value))

const setZoom = (value) => {
  const clamped = clampZoom(value)
  zoom.value = clamped
  if (clamped <= 1) {
    offset.value = { x: 0, y: 0 }
  }
}

const zoomIn = () => setZoom(zoom.value + 0.2)
const zoomOut = () => setZoom(zoom.value - 0.2)
const resetZoom = () => {
  offset.value = { x: 0, y: 0 }
  setZoom(1)
}

const handleZoomChange = (event) => {
  setZoom(parseFloat(event.target.value))
}

const handleWheel = (event) => {
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  setZoom(zoom.value + delta)
}

const handleDoubleClick = () => {
  if (zoom.value > 1.05) {
    resetZoom()
  } else {
    setZoom(2)
  }
}

const getPointerPosition = (event) => {
  if (event.touches && event.touches[0]) {
    return {
      x: event.touches[0].clientX,
      y: event.touches[0].clientY
    }
  }
  if (event.changedTouches && event.changedTouches[0]) {
    return {
      x: event.changedTouches[0].clientX,
      y: event.changedTouches[0].clientY
    }
  }
  return {
    x: event.clientX,
    y: event.clientY
  }
}

const startDrag = (event) => {
  if (zoom.value <= 1) return
  if (event.type === 'mousedown' && event.button !== 0) return
  const target = event.target
  if (!(target instanceof HTMLElement) || target.tagName !== 'IMG') return

  const position = getPointerPosition(event)
  dragStart.value = position
  dragStartOffset.value = { ...offset.value }
  isDragging.value = true
  event.preventDefault()
}

const handleDrag = (event) => {
  if (!isDragging.value) return

  const position = getPointerPosition(event)
  const deltaX = position.x - dragStart.value.x
  const deltaY = position.y - dragStart.value.y

  offset.value = {
    x: dragStartOffset.value.x + deltaX,
    y: dragStartOffset.value.y + deltaY
  }

  if (event.cancelable) {
    event.preventDefault()
  }
}

const endDrag = () => {
  if (!isDragging.value) return
  isDragging.value = false
}

onMounted(() => {
  window.addEventListener('mouseup', endDrag)
  window.addEventListener('touchend', endDrag)
  window.addEventListener('touchcancel', endDrag)
})

onBeforeUnmount(() => {
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('touchend', endDrag)
  window.removeEventListener('touchcancel', endDrag)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
