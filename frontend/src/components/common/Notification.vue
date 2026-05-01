<template>
  <div class="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="flex items-center p-4 mb-2 text-sm text-gray-800 rounded-lg shadow-lg border pointer-events-auto min-w-[300px] max-w-md"
        :class="[
          notification.type === 'success' ? 'bg-white border-l-4 border-l-green-500' : '',
          notification.type === 'error' ? 'bg-white border-l-4 border-l-red-500' : '',
          notification.type === 'warning' ? 'bg-white border-l-4 border-l-yellow-500' : '',
          notification.type === 'info' ? 'bg-white border-l-4 border-l-blue-500' : '',
        ]"
        role="alert"
      >
        <component
          :is="getIcon(notification.type)"
          class="flex-shrink-0 inline w-5 h-5 mr-3"
          :class="[
            notification.type === 'success' ? 'text-green-500' : '',
            notification.type === 'error' ? 'text-red-500' : '',
            notification.type === 'warning' ? 'text-yellow-500' : '',
            notification.type === 'info' ? 'text-blue-500' : '',
          ]"
        />
        <div class="font-medium flex-1">{{ notification.message }}</div>
        <button
          type="button"
          class="ml-2 -mx-1.5 -my-1.5 rounded-lg focus:ring-2 p-1.5 inline-flex h-8 w-8 text-gray-400 hover:text-gray-900 hover:bg-gray-100"
          @click="store.remove(notification.id)"
          aria-label="Close"
        >
          <span class="sr-only">Close</span>
          <XIcon class="w-5 h-5" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useNotificationStore } from '@/stores/notifications'
import { storeToRefs } from 'pinia'
import { CheckCircle, AlertCircle, AlertTriangle, Info, X as XIcon } from 'lucide-vue-next'

const store = useNotificationStore()
const { notifications } = storeToRefs(store)

const getIcon = (type) => {
  switch (type) {
    case 'success':
      return CheckCircle
    case 'error':
      return AlertCircle
    case 'warning':
      return AlertTriangle
    case 'info':
      return Info
    default:
      return Info
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}
.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
