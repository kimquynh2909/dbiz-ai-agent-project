<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
    <div class="bg-white rounded-xl max-w-6xl w-full max-h-[95vh] overflow-hidden flex flex-col my-8">
      <div
        class="flex items-center justify-between p-6 border-b bg-gradient-to-r from-orange-600 to-orange-700 text-white"
      >
        <h3 class="text-xl font-bold">Kết quả OCR - Phiếu xuất</h3>
        <button @click="$emit('close')" class="text-white hover:text-gray-200">
          <XIcon class="w-6 h-6" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="ocrResult && ocrResult.extracted_data" class="space-y-6">
          <!-- Delivery Note Basic Info -->
          <div class="bg-orange-50 rounded-lg p-6 border border-orange-200">
            <h4 class="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <FileTextIcon class="w-5 h-5 text-orange-600" />
              <span>Thông tin phiếu xuất</span>
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Số phiếu xuất</label>
                <input
                  v-model="formData.delivery_note_number"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Ngày xuất</label>
                <input
                  v-model="formData.delivery_date"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Khách hàng</label>
                <input
                  v-model="formData.customer"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
            </div>
          </div>

          <!-- Items List -->
          <div
            v-if="formData.items && formData.items.length > 0"
            class="bg-yellow-50 rounded-lg p-6 border border-yellow-200"
          >
            <h4 class="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <svg class="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"
                />
              </svg>
              <span>Chi tiết hàng hóa</span>
            </h4>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="bg-yellow-100">
                  <tr>
                    <th class="px-4 py-2 text-left font-semibold text-gray-700">STT</th>
                    <th class="px-4 py-2 text-left font-semibold text-gray-700">Mã hàng</th>
                    <th class="px-4 py-2 text-left font-semibold text-gray-700">Tên hàng</th>
                    <th class="px-4 py-2 text-left font-semibold text-gray-700">Đơn vị</th>
                    <th class="px-4 py-2 text-right font-semibold text-gray-700">Số lượng</th>
                    <th class="px-4 py-2 text-right font-semibold text-gray-700">Đơn giá</th>
                    <th class="px-4 py-2 text-right font-semibold text-gray-700">Thành tiền</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(item, index) in formData.items" :key="index" class="hover:bg-gray-50">
                    <td class="px-4 py-2">{{ item.stt || index + 1 }}</td>
                    <td class="px-4 py-2">
                      <input
                        v-model="item.item_code"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-orange-500"
                      />
                    </td>
                    <td class="px-4 py-2">
                      <input
                        v-model="item.item_name"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-orange-500"
                      />
                    </td>
                    <td class="px-4 py-2">
                      <input
                        v-model="item.unit"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-orange-500"
                      />
                    </td>
                    <td class="px-4 py-2 text-right">
                      <input
                        v-model.number="item.quantity"
                        type="number"
                        class="w-full px-2 py-1 border border-gray-300 rounded text-right focus:outline-none focus:ring-1 focus:ring-orange-500"
                      />
                    </td>
                    <td class="px-4 py-2 text-right">
                      <input
                        v-model.number="item.unit_price"
                        type="number"
                        class="w-full px-2 py-1 border border-gray-300 rounded text-right focus:outline-none focus:ring-1 focus:ring-orange-500"
                      />
                    </td>
                    <td class="px-4 py-2 text-right font-medium">
                      {{ item.amount ? item.amount.toLocaleString('vi-VN') : '' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Total Info -->
          <div class="bg-indigo-50 rounded-lg p-6 border border-indigo-200">
            <h4 class="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <svg class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"
                />
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z"
                  clip-rule="evenodd"
                />
              </svg>
              <span>Thông tin tài chính</span>
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tổng tiền</label>
                <input
                  v-model.number="formData.total_amount"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white font-bold text-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                <textarea
                  v-model="formData.notes"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- OCR Metadata -->
          <div v-if="ocrResult.ocr_metadata" class="bg-gray-100 rounded-lg p-4 border border-gray-300">
            <div class="text-xs text-gray-600 space-y-1">
              <div>
                <strong>OCR Engine:</strong>
                {{ ocrResult.ocr_metadata.ocr_engine || 'N/A' }}
              </div>
              <div>
                <strong>Model:</strong>
                {{ ocrResult.ocr_metadata.model || 'N/A' }}
              </div>
              <div>
                <strong>Tokens used:</strong>
                {{ ocrResult.ocr_metadata.tokens_used || 'N/A' }}
              </div>
              <div>
                <strong>Language:</strong>
                {{ ocrResult.ocr_metadata.language_detected || 'N/A' }}
              </div>
              <div v-if="ocrResult.confidence_scores">
                <strong>Confidence:</strong>
                {{ (ocrResult.confidence_scores.overall * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="p-6 border-t bg-gray-50 flex justify-end space-x-3">
        <button
          @click="$emit('close')"
          class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
        >
          Đóng
        </button>
        <button
          @click="handleSave"
          :disabled="isSaving"
          class="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isSaving">Đang lưu...</span>
          <span v-else>Lưu dữ liệu</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { FileText as FileTextIcon, X as XIcon } from 'lucide-vue-next'
import { call } from 'frappe-ui'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const props = defineProps({
  ocrResult: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'saved'])

const isSaving = ref(false)
const formData = ref({
  delivery_note_number: '',
  delivery_date: '',
  customer: '',
  items: [],
  total_amount: 0,
  notes: '',
})

// Initialize form data from OCR result
watch(
  () => props.ocrResult,
  (newResult) => {
    if (newResult && newResult.extracted_data) {
      const data = newResult.extracted_data

      formData.value.delivery_note_number = data.delivery_note_number || ''
      formData.value.delivery_date = data.delivery_date || ''
      formData.value.customer = data.customer || ''
      formData.value.items = data.items || []
      formData.value.total_amount = data.total_amount || 0
      formData.value.notes = data.notes || ''
    }
  },
  { immediate: true }
)

// Calculate item amount
watch(
  () => formData.value.items,
  (items) => {
    items.forEach((item) => {
      if (item.quantity && item.unit_price) {
        item.amount = item.quantity * item.unit_price
      }
    })
  },
  { deep: true }
)

const handleSave = async () => {
  try {
    isSaving.value = true

    const response = await call('dbiz_ai_agent.api.ocr.save_delivery_note', {
      delivery_note_data: formData.value,
      ocr_result: props.ocrResult,
    })

    if (response.success) {
      emit('saved', response.data)
      emit('close')
    } else {
      notificationStore.notify('Lỗi khi lưu dữ liệu: ' + (response.message || 'Unknown error'), 'error')
    }
  } catch (error) {
    console.error('Error saving delivery note:', error)
    notificationStore.notify('Có lỗi xảy ra khi lưu dữ liệu: ' + error.message, 'error')
  } finally {
    isSaving.value = false
  }
}
</script>
