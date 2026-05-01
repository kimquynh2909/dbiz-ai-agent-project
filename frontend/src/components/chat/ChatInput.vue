<template>
  <div class="input-area bg-white border-t border-gray-200 px-6 py-2 shadow-lg z-10 sticky bottom-0">
    <div class="max-w-5xl mx-auto">
      <form @submit.prevent="handleSubmit" class="flex items-center space-x-3">
        <div class="flex-1 relative">
          <input
            v-model="localMessage"
            placeholder="Nhắn tin cho Ms.Sunny"
            :disabled="disabled"
            class="w-full px-6 py-4 pr-16 text-base border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 transition-all duration-200"
            :autofocus="shouldAutofocus"
          />
          <div class="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
            <button type="button" class="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
            <button
              type="button"
              class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              :class="{ 'text-blue-600': isRecording }"
              @click="toggleMicro"
            >
              <svg v-if="!isRecording" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
              <svg v-else class="w-5 h-5 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="#3b82f6" />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
            </button>
          </div>
        </div>
        <button
          type="submit"
          :disabled="!localMessage || !localMessage.trim() || disabled"
          class="w-12 h-12 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-full hover:from-blue-700 hover:to-blue-800 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const isRecording = ref(false)
let recognition = null

const startSpeechRecognition = () => {
  if (!('webkitSpeechRecognition' in window)) {
    notificationStore.notify('Trình duyệt không hỗ trợ nhận diện giọng nói!', 'warning')
    return
  }
  if (!recognition) {
    recognition = new window.webkitSpeechRecognition()
    recognition.lang = 'vi-VN'
    recognition.continuous = false
    recognition.interimResults = false
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      localMessage.value = transcript
    }
    recognition.onerror = (event) => {
      notificationStore.notify('Lỗi nhận diện giọng nói: ' + event.error, 'error')
    }
    recognition.onend = () => {
      isRecording.value = false
    }
  }
  recognition.start()
  isRecording.value = true
}

const stopSpeechRecognition = () => {
  if (recognition) {
    recognition.stop()
    isRecording.value = false
  }
}

const toggleMicro = () => {
  if (isRecording.value) {
    stopSpeechRecognition()
  } else {
    startSpeechRecognition()
  }
}

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const localMessage = ref(props.modelValue)

watch(
  () => props.modelValue,
  (newVal) => {
    localMessage.value = newVal
  }
)

watch(localMessage, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleSubmit = () => {
  if (!localMessage.value || !localMessage.value.trim() || props.disabled) return
  emit('submit', localMessage.value)
  localMessage.value = ''
}

// Avoid browser warning: "Blocked autofocusing on a <input> element in a cross-origin subframe."
// Only enable autofocus when widget is same-origin (e.g., opened directly),
// and disable when embedded cross-origin via parent_origin.
const shouldAutofocus = computed(() => {
  try {
    const u = new URL(window.location.href)
    const parentOrigin = u.searchParams.get('parent_origin')
    if (parentOrigin && parentOrigin !== window.location.origin) return false
  } catch (e) {
    /* ignore */
  }
  try {
    return window.top.location.origin === window.location.origin
  } catch (e) {
    // Cross-origin access throws; disable autofocus
    return false
  }
})
</script>

<style scoped>
.input-area {
  --input-height: 90px;
  min-height: var(--input-height);
}

@media (max-width: 1024px) {
  .input-area {
    left: 0 !important;
  }
}
</style>
