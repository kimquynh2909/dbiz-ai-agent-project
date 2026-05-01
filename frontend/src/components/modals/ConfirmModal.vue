<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-lg"
    :panel-class="['bg-white rounded-xl shadow-2xl w-full p-6']"
    :close-on-backdrop="false"
    z-index="z-60"
    @close="emit('cancel')"
  >
    <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h3>
    <p class="text-sm text-gray-700 mb-4" v-html="message"></p>
    <div class="flex justify-end space-x-3">
      <button @click="emit('cancel')" class="px-4 py-2 bg-gray-100 rounded-md text-gray-700">
        {{ cancelText }}
      </button>
      <button @click="emit('confirm')" class="px-4 py-2 bg-red-600 text-white rounded-md">
        {{ confirmText }}
      </button>
    </div>
  </ModalBase>
</template>

<script setup>
import ModalBase from '@/components/common/ModalBase.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Xác nhận'
  },
  message: {
    type: String,
    default: ''
  },
  confirmText: {
    type: String,
    default: 'Xác nhận'
  },
  cancelText: {
    type: String,
    default: 'Hủy'
  }
})

const emit = defineEmits(['confirm', 'cancel'])
</script>
