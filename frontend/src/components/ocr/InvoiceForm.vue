<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
    <div class="bg-white rounded-xl max-w-6xl w-full max-h-[95vh] overflow-hidden flex flex-col my-8">
      <div class="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <h3 class="text-xl font-bold">Kết quả OCR - Hóa đơn</h3>
        <button @click="$emit('close')" class="text-white hover:text-gray-200">
          <XIcon class="w-6 h-6" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="ocrResult && ocrResult.extracted_data" class="space-y-6">
          <!-- Header Summary -->
          <div
            class="bg-gradient-to-r from-sky-600 to-indigo-600 text-white rounded-lg shadow-sm p-6 border border-blue-200"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="text-lg font-semibold">Header &amp; Thông tin chung</div>
              <span class="text-xs uppercase tracking-wide text-white/70">OCR</span>
            </div>
            <div class="grid gap-4 md:grid-cols-4">
              <div>
                <p class="text-xs uppercase tracking-wide text-white/70 mb-1">Số hóa đơn</p>
                <input
                  v-model="formData.invoice_number"
                  type="text"
                  class="w-full rounded-lg bg-white/20 border border-white/40 px-3 py-2 text-white placeholder-white/50 focus:border-white focus:bg-white/30 focus:outline-none"
                  placeholder="Số hóa đơn"
                />
              </div>
              <div>
                <p class="text-xs uppercase tracking-wide text-white/70 mb-1">Ký hiệu</p>
                <input
                  v-model="formData.invoice_symbol"
                  type="text"
                  class="w-full rounded-lg bg-white/20 border border-white/40 px-3 py-2 text-white placeholder-white/50 focus:border-white focus:bg-white/30 focus:outline-none"
                  placeholder="Ký hiệu"
                />
              </div>
              <div>
                <p class="text-xs uppercase tracking-wide text-white/70 mb-1">Ngày hóa đơn</p>
                <input
                  v-model="formData.invoice_date"
                  type="date"
                  class="w-full rounded-lg bg-white/20 border border-white/40 px-3 py-2 text-white focus:border-white focus:bg-white/30 focus:outline-none"
                />
              </div>
              <div>
                <p class="text-xs uppercase tracking-wide text-white/70 mb-1">Mã tài liệu</p>
                <input
                  v-model="formData.document_code"
                  type="text"
                  class="w-full rounded-lg bg-white/20 border border-white/40 px-3 py-2 text-white placeholder-white/50 focus:border-white focus:bg-white/30 focus:outline-none"
                  placeholder="Mã tài liệu"
                />
              </div>
            </div>
          </div>

          <div v-if="scannedFile" class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 space-y-4">
            <div class="flex flex-col gap-1">
              <p class="text-xs uppercase tracking-wide text-gray-500">Tệp đã scan</p>
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-semibold text-gray-700 truncate">{{ scannedFile.name }}</p>
                  <p class="text-xs text-gray-500">
                    {{ formatFileSize(scannedFile.size) }} · {{ scannedFile.type || 'Không xác định' }}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button
                    type="button"
                    @click="openScannedFile"
                    class="px-3 py-1 text-xs font-semibold uppercase text-blue-600 border border-blue-200 rounded-full hover:bg-blue-50 transition-colors"
                  >
                    Xem
                  </button>
                  <button
                    type="button"
                    @click="downloadScannedFile"
                    class="px-3 py-1 text-xs font-semibold uppercase text-green-600 border border-green-200 rounded-full hover:bg-green-50 transition-colors"
                  >
                    Tải xuống
                  </button>
                </div>
              </div>
            </div>
            <div class="rounded-lg border border-dashed border-gray-200 px-4 py-6 text-sm text-gray-500">
              <p class="font-semibold text-gray-600">Preview chỉ hiển khi bấm “Xem”.</p>
              <p>Nhấn “Xem” để mở tệp trong tab mới hoặc “Tải xuống” để lưu.</p>
            </div>
          </div>

          <!-- Seller / Buyer Details -->
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-6">
            <div class="grid gap-6 lg:grid-cols-2">
              <div class="space-y-4">
                <div class="flex items-center gap-2 text-sm font-semibold text-green-700">
                  <span class="h-3 w-3 rounded-full bg-green-600"></span>
                  Người bán
                </div>
                <div class="grid gap-4 sm:grid-cols-2">
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Tên</p>
                    <input
                      v-model="formData.seller.name"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-green-50 focus:border-green-400 focus:bg-green-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Mã số thuế</p>
                    <input
                      v-model="formData.seller.tax_code"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-green-50 focus:border-green-400 focus:bg-green-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Địa chỉ</p>
                    <input
                      v-model="formData.seller.address"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-green-50 focus:border-green-400 focus:bg-green-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Điện thoại</p>
                    <input
                      v-model="formData.seller.phone"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-green-50 focus:border-green-400 focus:bg-green-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Email</p>
                    <input
                      v-model="formData.seller.email"
                      type="email"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-green-50 focus:border-green-400 focus:bg-green-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Tài khoản ngân hàng</p>
                    <input
                      v-model="formData.seller.bank_account"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-green-50 focus:border-green-400 focus:bg-green-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1 sm:col-span-2">
                    <p class="text-xs uppercase text-gray-500">Ngân hàng</p>
                    <input
                      v-model="formData.seller.bank_name"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-green-50 focus:border-green-400 focus:bg-green-50 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              <div class="space-y-4">
                <div class="flex items-center gap-2 text-sm font-semibold text-purple-700">
                  <span class="h-3 w-3 rounded-full bg-purple-600"></span>
                  Người mua
                </div>
                <div class="grid gap-4 sm:grid-cols-2">
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Tên</p>
                    <input
                      v-model="formData.buyer.name"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-purple-50 focus:border-purple-400 focus:bg-purple-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Tên công ty</p>
                    <input
                      v-model="formData.buyer.company_name"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-purple-50 focus:border-purple-400 focus:bg-purple-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Mã số thuế</p>
                    <input
                      v-model="formData.buyer.tax_code"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-purple-50 focus:border-purple-400 focus:bg-purple-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Địa chỉ</p>
                    <input
                      v-model="formData.buyer.address"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-purple-50 focus:border-purple-400 focus:bg-purple-50 focus:outline-none"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs uppercase text-gray-500">Điện thoại</p>
                    <input
                      v-model="formData.buyer.phone"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 bg-purple-50 focus:border-purple-400 focus:bg-purple-50 focus:outline-none"
                    />
                  </div>
                </div>
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
                    <th class="px-4 py-2 text-left font-semibold text-gray-700">Mô tả</th>
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
                      <div class="flex items-center gap-2">
                        <input
                          v-model="item.description"
                          type="text"
                          class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                        <button
                          type="button"
                          class="text-xs text-blue-600 underline"
                          @click="openDescriptionModal(item.description)"
                        >
                          Chi tiết
                        </button>
                      </div>
                    </td>
                    <td class="px-4 py-2">
                      <input
                        v-model="item.unit"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </td>
                    <td class="px-4 py-2 text-right">
                      <input
                        :value="formatCurrency(item.quantity)"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded text-right focus:outline-none focus:ring-1 focus:ring-blue-500"
                        @input="updateItemNumeric(item, 'quantity', $event.target.value)"
                      />
                    </td>
                    <td class="px-4 py-2 text-right">
                      <input
                        :value="formatCurrency(item.unit_price)"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded text-right focus:outline-none focus:ring-1 focus:ring-blue-500"
                        @input="updateItemNumeric(item, 'unit_price', $event.target.value)"
                      />
                    </td>
                    <td class="px-4 py-2 text-right font-medium">
                      {{ formatCurrency(item.amount) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Financial Info -->
          <div v-if="ocrResult.extracted_data.financial" class="bg-indigo-50 rounded-lg p-6 border border-indigo-200">
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
                  :value="formatCurrency(formData.financial.subtotal)"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateFinancial('subtotal', $event.target.value)"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Thuế VAT (%)</label>
                <input
                  :value="formatCurrency(formData.financial.vat_rate)"
                  type="text"
                  step="0.1"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateFinancial('vat_rate', $event.target.value)"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tiền thuế</label>
                <input
                  :value="formatCurrency(formData.financial.vat_amount)"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateFinancial('vat_amount', $event.target.value)"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tổng cộng</label>
                <input
                  :value="formatCurrency(formData.financial.total_amount)"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white font-bold text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateFinancial('total_amount', $event.target.value)"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Bằng chữ</label>
                <input
                  v-model="formData.financial.amount_in_words"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Đơn vị tiền tệ</label>
                <input
                  v-model="formData.financial.currency"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Payment Info -->
          <div v-if="ocrResult.extracted_data.payment_info" class="bg-gray-50 rounded-lg p-6 border border-gray-200">
            <h4 class="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <svg class="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"
                  clip-rule="evenodd"
                />
              </svg>
              <span>Thông tin thanh toán</span>
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Phương thức thanh toán</label>
                <input
                  v-model="formData.payment_info.payment_method"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div v-if="formData.payment_info.payment_status !== undefined">
                <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái thanh toán</label>
                <input
                  v-model="formData.payment_info.payment_status"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
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
          @click="handleCreateInvoice"
          :disabled="isSaving"
          class="px-6 py-2 bg-gradient-to-r from-green-600 to-green-500 text-white rounded-lg hover:from-green-700 hover:to-green-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isSaving">Đang tạo...</span>
          <span v-else>Tạo hóa đơn</span>
        </button>
      </div>
      <div
        v-if="descriptionModal.open"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6"
      >
        <div class="w-full max-w-lg bg-white rounded-xl shadow-xl overflow-hidden">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h3 class="text-lg font-semibold text-gray-900">Nội dung mô tả</h3>
            <button @click="closeDescriptionModal" class="text-gray-500 hover:text-gray-700">&times;</button>
          </div>
          <div class="px-6 py-4">
            <p class="text-sm text-gray-700 whitespace-pre-line">{{ descriptionModal.text || 'Không có nội dung' }}</p>
          </div>
          <div class="flex justify-end px-6 py-4 border-t">
            <button
              @click="closeDescriptionModal"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Đóng
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { X as XIcon } from 'lucide-vue-next'
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
  invoice_number: '',
  invoice_symbol: '',
  invoice_date: '',
  document_code: '',
  seller: {
    name: '',
    tax_code: '',
    phone: '',
    address: '',
    email: '',
    bank_account: '',
    bank_name: '',
  },
  buyer: {
    name: '',
    tax_code: '',
    phone: '',
    address: '',
    company_name: '',
  },
  items: [],
  financial: {
    subtotal: 0,
    vat_rate: 0,
    vat_amount: 0,
    total_amount: 0,
    amount_in_words: '',
    currency: 'VND',
  },
  payment_info: {
    payment_method: '',
    payment_status: '',
  },
})

const scannedFile = computed(() => props.ocrResult?.scannedFile)
const scannedFilePreview = computed(() => {
  const file = scannedFile.value
  if (!file?.base64) return null
  const mime = file.type || 'application/octet-stream'
  return `data:${mime};base64,${file.base64}`
})
const isImagePreview = computed(() => scannedFile.value?.type?.startsWith('image/'))
const isPdfPreview = computed(() => scannedFile.value?.type === 'application/pdf')
const pdfPreviewUrl = computed(() => {
  const file = scannedFile.value
  if (!file?.base64) return null
  const mime = file.type || 'application/pdf'
  return `data:${mime};base64,${file.base64}`
})

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  if (!bytes) return '-'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return ''
  const number = Number(value)
  if (Number.isNaN(number)) return ''
  return number.toLocaleString('vi-VN')
}

const parseCurrency = (value) => {
  if (value === undefined || value === null) return 0
  const normalized = String(value).replace(/[^0-9.-]/g, '')
  const parsed = Number(normalized)
  return Number.isNaN(parsed) ? 0 : parsed
}

const updateItemNumeric = (item, field, value) => {
  const raw = parseCurrency(value)
  item[field] = raw
  if (field === 'quantity' || field === 'unit_price') {
    if (item.quantity != null && item.unit_price != null) {
      item.amount = item.quantity * item.unit_price
    }
  }
}

const updateFinancial = (field, value) => {
  const raw = parseCurrency(value)
  formData.value.financial[field] = raw
}

const descriptionModal = ref({
  open: false,
  text: '',
})

const openDescriptionModal = (text) => {
  descriptionModal.value = {
    open: true,
    text: text || '',
  }
}

const closeDescriptionModal = () => {
  descriptionModal.value = {
    open: false,
    text: '',
  }
}

const createBlobFromBase64 = (base64, type) => {
  const binary = atob(base64)
  const len = binary.length
  const buffer = new Uint8Array(len)
  for (let i = 0; i < len; i += 1) {
    buffer[i] = binary.charCodeAt(i)
  }
  return new Blob([buffer], { type: type || 'application/octet-stream' })
}

const downloadScannedFile = () => {
  const file = scannedFile.value
  if (!file?.base64) return
  const blob = createBlobFromBase64(file.base64, file.type)
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = file.name || 'ocr-result'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const openScannedFile = () => {
  const url = isPdfPreview.value ? pdfPreviewUrl.value : scannedFilePreview.value
  if (!url) return
  window.open(url, '_blank')
}

// Initialize form data from OCR result
watch(
  () => props.ocrResult,
  (newResult) => {
    if (newResult && newResult.extracted_data) {
      const data = newResult.extracted_data

      formData.value.invoice_number = data.invoice_number || ''
      formData.value.invoice_symbol = data.invoice_symbol || ''
      formData.value.document_code = data.document_code || data.request_id || ''

      if (data.invoice_date) {
        const dateStr = data.invoice_date
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
          formData.value.invoice_date = dateStr
        } else {
          const parsedDate = new Date(dateStr)
          formData.value.invoice_date = isNaN(parsedDate.getTime()) ? '' : parsedDate.toISOString().split('T')[0]
        }
      } else {
        formData.value.invoice_date = ''
      }

      if (data.seller) {
        formData.value.seller = {
          name: data.seller.name || '',
          tax_code: data.seller.tax_code || '',
          phone: data.seller.phone || '',
          address: data.seller.address || '',
          email: data.seller.email || null,
          bank_account: data.seller.bank_account || '',
          bank_name: data.seller.bank_name || '',
        }
      }

      if (data.buyer) {
        formData.value.buyer = {
          name: data.buyer.name || '',
          tax_code: data.buyer.tax_code || '',
          phone: data.buyer.phone || null,
          address: data.buyer.address || '',
          company_name: data.buyer.company_name || '',
        }
      }

      formData.value.items = Array.isArray(data.items)
        ? data.items.map((item) => ({
            stt: item.stt || 0,
            description: item.description || '',
            unit: item.unit || null,
            quantity: item.quantity || null,
            unit_price: item.unit_price || null,
            amount: item.amount || 0,
          }))
        : []

      if (data.financial) {
        formData.value.financial = {
          subtotal: data.financial.subtotal || 0,
          vat_rate: data.financial.vat_rate || 0,
          vat_amount: data.financial.vat_amount || 0,
          total_amount: data.financial.total_amount || 0,
          amount_in_words: data.financial.amount_in_words || '',
          currency: data.financial.currency || 'VND',
        }
      }

      if (data.payment_info) {
        formData.value.payment_info = {
          payment_method: data.payment_info.payment_method || '',
          payment_status: data.payment_info.payment_status || null,
        }
      }

      console.log('Form data initialized from OCR result:', formData.value)
    }
  },
  { immediate: true }
)

// Calculate item amount when quantity or unit_price changes
watch(
  () => formData.value.items,
  (items) => {
    items.forEach((item) => {
      if (item.quantity != null && item.unit_price != null) {
        item.amount = item.quantity * item.unit_price
      }
    })
  },
  { deep: true }
)

const handleCreateInvoice = async () => {
  try {
    isSaving.value = true
    const response = await call('dbiz_ai_agent.api.ocr.create_ap_invoice_from_ocr', {
      invoice_data: formData.value,
      ocr_result: props.ocrResult,
      scanned_file: scannedFile.value,
    })

    const result = response?.message || response

    if (result.success) {
      emit('saved', result.name || result)
      emit('close')
    } else {
      notificationStore.notify('Lỗi khi tạo hóa đơn: ' + (result.error || result.message || 'Không xác định'), 'error')
    }
  } catch (error) {
    console.error('Error creating purchase invoice:', error)
    notificationStore.notify('Có lỗi xảy ra khi tạo hóa đơn: ' + (error.message || 'Vui lòng thử lại'), 'error')
  } finally {
    isSaving.value = false
  }
}
</script>
