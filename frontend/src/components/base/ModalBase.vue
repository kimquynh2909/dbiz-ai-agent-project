<template>
    <Teleport to="body">
      <transition name="modal-fade">
        <div
          v-if="visible"
          class="fixed inset-0 flex items-center justify-center px-4 py-6 sm:px-6"
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
  import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
  
  const props = defineProps({
    visible: {
      type: Boolean,
      default: false
    },
    closeOnEsc: {
      type: Boolean,
      default: true
    },
    closeOnBackdrop: {
      type: Boolean,
      default: true
    },
    maxWidth: {
      type: String,
      default: 'max-w-lg'
    },
    panelClass: {
      type: [String, Array, Object],
      default: () => 'bg-white rounded-xl shadow-xl'
    },
    zIndex: {
      type: String,
      default: 'z-50'
    }
  })
  
  const emit = defineEmits(['close'])
  
  const panelRef = ref(null)
  
  const handleBackdrop = () => {
    if (!props.closeOnBackdrop) return
    emit('close')
  }
  
  const handleEsc = (event) => {
    if (!props.visible || !props.closeOnEsc) return
    if (event.key === 'Escape') {
      emit('close')
    }
  }
  
  const toggleBodyScroll = (shouldLock) => {
    const className = 'overflow-hidden'
    if (shouldLock) {
      document.body.classList.add(className)
    } else {
      document.body.classList.remove(className)
    }
  }
  
  watch(
    () => props.visible,
    (visible) => {
      toggleBodyScroll(visible)
    }
  )
  
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
  