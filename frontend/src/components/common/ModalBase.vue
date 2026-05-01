<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div
        v-if="visible"
        class="fixed inset-0 flex items-center justify-center"
        :class="zIndex"
      >
        <div class="absolute inset-0 bg-black/60" @click="handleBackdrop" />
        <div
          ref="panelRef"
          class="relative w-full max-h-[calc(100vh-3rem)] overflow-y-auto"
          :class="[maxWidth, panelClass]"
          role="dialog"
          aria-modal="true"
        >
          <slot />
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
// import các hàm lifecycle
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

// props cho modal
const props = defineProps({
  visible: { type: Boolean, default: false }, // hiển thị modal
  closeOnEsc: { type: Boolean, default: true }, // đóng bằng phím Esc
  closeOnBackdrop: { type: Boolean, default: true }, // đóng khi click nền
  maxWidth: { type: String, default: 'max-w-lg' }, // chiều rộng tối đa
  panelClass: { type: [String, Array, Object], default: () => 'bg-white rounded-xl shadow-xl' }, // class cho panel
  zIndex: { type: String, default: 'z-50' } // thứ tự lớp
})

// emit sự kiện đóng
const emit = defineEmits(['close'])

// ref tới panel
const panelRef = ref(null)

// xử lý click nền
const handleBackdrop = () => {
  if (!props.closeOnBackdrop) return
  emit('close')
}

// xử lý phím Esc
const handleEsc = (event) => {
  if (!props.visible || !props.closeOnEsc) return
  if (event.key === 'Escape') emit('close')
}

// khóa scroll body khi mở modal
const toggleBodyScroll = (shouldLock) => {
  const className = 'overflow-hidden'
  if (shouldLock) document.body.classList.add(className)
  else document.body.classList.remove(className)
}


// theo dõi trạng thái visible để khóa/mở scroll body
watch(() => props.visible, (visible) => {
  toggleBodyScroll(visible)
})

onMounted(() => {
  window.addEventListener('keydown', handleEsc)
  if (props.visible) toggleBodyScroll(true)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEsc)
  toggleBodyScroll(false)
})
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
