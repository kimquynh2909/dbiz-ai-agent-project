<template>
  <div class="flex-1 min-h-0 overflow-y-auto bg-gray-50">
    <div class="space-y-6 px-6 py-6">
      <!-- Main Content -->
      <div class="space-y-10">
        <section class="bg-white rounded-2xl shadow-sm p-5 border border-gray-200">
          <div class="flex justify-center text-gray-400 text-sm">
            <template v-for="step in stepDefinitions" :key="step.id">
              <div class="flex items-center gap-3">
                <div
                  class="flex h-9 w-9 items-center justify-center rounded-full border relative overflow-visible"
                  :class="
                    currentStep === step.id
                      ? 'bg-sky-600 text-white border-sky-600 rotate-step'
                      : 'bg-gray-100 border-gray-200 text-gray-500'
                  "
                >
                  {{ step.id }}
                </div>
                <div :class="currentStep === step.id ? 'text-gray-900 font-semibold' : 'text-gray-400'">
                  {{ step.label }}
                </div>
              </div>
              <div v-if="step.id < stepDefinitions.length" class="h-[2px] w-12 bg-gray-200 self-center"></div>
            </template>
          </div>
        </section>

        <section v-if="currentStep === 1" class="space-y-6 bg-white rounded-2xl shadow-sm p-6 border border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs uppercase tracking-wide text-gray-500">Step 1 · Upload & Chuẩn bị</p>
              <h3 class="text-lg font-semibold text-gray-900">Chọn loại chứng từ & Upload</h3>
            </div>
            <span class="text-sm text-sky-600">Step 1</span>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Loại tài liệu</label>
              <select
                v-model="documentType"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option v-for="dt in documentTypes" :key="dt.name" :value="dt.document_type_code">
                  {{ dt.document_type_name }}
                </option>
                <option v-if="documentTypes.length === 0" value="INVOICE">Hóa đơn</option>
                <option v-if="documentTypes.length === 0" value="CCCD">CCCD / CMND</option>
                <option v-if="documentTypes.length === 0" value="land_certificate">Sổ đỏ / Giấy chứng nhận đất</option>
              </select>
            </div>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-700">Xử lý hàng loạt</p>
                <p class="text-xs text-gray-500">Cho phép upload & xử lý nhiều tệp</p>
              </div>
              <button
                type="button"
                @click="batchMode = !batchMode"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none',
                  batchMode ? 'bg-sky-500' : 'bg-gray-300',
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    batchMode ? 'translate-x-5' : 'translate-x-1',
                  ]"
                ></span>
              </button>
            </div>
          </div>

          <div
            @drop="handleDrop"
            @dragover.prevent
            @dragenter.prevent
            :class="[
              'border-2 border-dashed rounded-xl p-6 md:p-8 min-h-[260px] transition-all duration-200',
              isDragging ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-green-400 hover:bg-green-50',
            ]"
          >
            <div v-if="pendingFiles.length === 0" class="flex flex-col items-center space-y-4 text-center">
              <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <UploadIcon class="w-8 h-8 text-green-600" />
              </div>
              <div>
                <p class="text-lg font-medium text-gray-900">Tải lên hoặc chụp ảnh chứng từ</p>
                <p class="text-sm text-gray-500 mt-1">Hỗ trợ PDF, JPG, PNG, TIFF</p>
              </div>
              <div class="flex gap-3">
                <button
                  @click="$refs.fileInput.click()"
                  class="px-5 py-2 rounded-xl bg-sky-600 text-white text-sm font-semibold hover:bg-sky-700 transition"
                >
                  Chọn file
                </button>
                <button
                  @click="openCamera"
                  class="px-5 py-2 rounded-xl border border-gray-300 text-sm font-semibold text-gray-700 hover:border-gray-400 transition"
                >
                  Chụp ảnh
                </button>
              </div>
              <input
                ref="fileInput"
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff,.webp"
                @change="handleFileSelect"
                class="hidden"
              />
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="md:col-span-2 space-y-2">
                <p class="text-sm text-gray-600">Tài liệu đã chọn ({{ pendingFiles.length }})</p>
                <div class="space-y-1 max-h-28 overflow-y-auto text-sm">
                  <div
                    v-for="file in pendingFiles"
                    :key="file.id"
                    class="flex items-center justify-between rounded-lg px-3 py-2 bg-white border border-gray-200"
                  >
                    <div class="text-gray-800 truncate">{{ file.name }}</div>
                    <div class="text-xs text-gray-500">{{ file.size }}</div>
                  </div>
                </div>
              </div>
              <div
                class="flex flex-col justify-between border-t border-gray-200 pt-4 md:border-t-0 md:border-l md:border-gray-200 md:pl-4"
              >
                <div>
                  <p class="text-sm font-medium text-gray-900">Xác nhận xử lý</p>
                  <p class="text-xs text-gray-500 mt-1">Gửi tài liệu lên OCR</p>
                </div>
                <button
                  type="button"
                  @click="confirmProcessing"
                  :disabled="pendingFiles.length === 0"
                  class="px-4 py-2 text-sm font-medium rounded-lg text-white bg-sky-600 hover:bg-sky-700 disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Xử lý {{ pendingFiles.length }} tài liệu
                </button>
              </div>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <!-- Lịch sử xử lý chứng từ -->
            <div
              class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-200 shadow-sm p-4 space-y-3"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p class="text-sm font-semibold uppercase tracking-wide text-blue-700">Lịch sử xử lý chứng từ</p>
              </div>
              <div
                v-if="recentTransactions.length === 0"
                class="text-sm text-blue-600 bg-white/60 rounded-lg p-3 text-center"
              >
                Chưa có lịch sử xử lý
              </div>
              <ul v-else class="space-y-2">
                <li
                  v-for="txn in recentTransactions"
                  :key="txn.name"
                  class="bg-white rounded-lg p-2.5 shadow-sm hover:shadow-md transition-shadow border border-blue-100"
                >
                  <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-2 flex-1 min-w-0">
                      <div class="flex-shrink-0">
                        <div
                          class="w-2 h-2 rounded-full"
                          :class="{
                            'bg-green-500': txn.status === 'Completed',
                            'bg-yellow-500': txn.status === 'Processing',
                            'bg-red-500': txn.status === 'Error',
                            'bg-gray-400': txn.status === 'Cancelled',
                          }"
                        ></div>
                      </div>
                      <span class="text-sm font-medium text-gray-700 truncate">{{ txn.file_name }}</span>
                    </div>
                    <div class="flex items-center space-x-2 ml-2 flex-shrink-0">
                      <span class="text-xs text-gray-500">{{ formatDate(txn.modified || txn.creation) }}</span>
                      <button
                        @click="viewTransactionDetailModal(txn.name)"
                        class="px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors"
                      >
                        Xem chi tiết
                      </button>
                    </div>
                  </div>
                </li>
              </ul>
            </div>

            <!-- Thống kê nhanh -->
            <div
              class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border-2 border-green-200 shadow-sm p-4 space-y-3"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                <p class="text-sm font-semibold uppercase tracking-wide text-green-700">Thống kê nhanh</p>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div
                  class="bg-white rounded-xl p-3 text-center shadow-sm border border-green-100 hover:shadow-md transition-shadow"
                >
                  <p class="text-xs font-medium text-green-600 mb-1">Hôm nay</p>
                  <p class="text-xl font-bold text-green-700">{{ stats.today }}</p>
                </div>
                <div
                  class="bg-white rounded-xl p-3 text-center shadow-sm border border-green-100 hover:shadow-md transition-shadow"
                >
                  <p class="text-xs font-medium text-green-600 mb-1">Tuần này</p>
                  <p class="text-xl font-bold text-green-700">{{ stats.week }}</p>
                </div>
                <div
                  class="bg-white rounded-xl p-3 text-center shadow-sm border border-green-100 hover:shadow-md transition-shadow"
                >
                  <p class="text-xs font-medium text-green-600 mb-1">Tháng này</p>
                  <p class="text-xl font-bold text-green-700">{{ stats.month }}</p>
                </div>
                <div
                  class="bg-white rounded-xl p-3 text-center shadow-sm border border-green-100 hover:shadow-md transition-shadow"
                >
                  <p class="text-xs font-medium text-green-600 mb-1">Tổng</p>
                  <p class="text-xl font-bold text-green-700">{{ stats.total }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-if="currentStep === 2" class="space-y-6 bg-white rounded-2xl shadow-sm p-6 border border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs uppercase tracking-wide text-gray-500">Step 2 · Xem trước & Xác nhận</p>
              <h3 class="text-lg font-semibold text-gray-900">File Input & Kết quả chi tiết</h3>
            </div>
            <span class="text-sm font-medium" :class="step2Disabled ? 'text-gray-400' : 'text-green-600'">
              {{ step2Disabled ? 'Đợi OCR' : 'Sẵn sàng xác nhận' }}
            </span>
          </div>
          <div class="space-y-6">
            <!-- File Input Section -->
            <div class="rounded-2xl border border-gray-200 p-4 space-y-4 bg-gray-50">
              <div class="flex items-center justify-between flex-wrap gap-3">
                <div>
                  <p class="text-sm font-semibold text-gray-900">File xử lý OCR</p>
                  <p class="text-xs text-gray-600 font-medium mt-1">
                    {{ scannedFileInfo?.name || 'Chưa có file OCR' }}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button
                    type="button"
                    @click="showValidationRulesModal = true"
                    class="px-4 py-2.5 text-sm font-semibold text-purple-600 bg-white border-2 border-purple-600 rounded-lg hover:bg-purple-50 transition-all shadow-sm"
                  >
                    Quy tắc kiểm tra
                  </button>
                  <button
                    type="button"
                    @click="handleValidateInvoice"
                    :disabled="step2Disabled || isValidating"
                    class="px-5 py-2.5 text-sm font-semibold text-orange-600 bg-white border-2 border-orange-600 rounded-lg hover:bg-orange-50 transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-sm"
                  >
                    <span v-if="isValidating">Đang kiểm tra...</span>
                    <span v-else>Kiểm tra thông tin hóa đơn</span>
                  </button>
                  <button
                    type="button"
                    @click="handleConfirmResult"
                    :disabled="step2Disabled || isSavingResult"
                    class="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-sky-600 to-sky-500 rounded-lg hover:from-sky-700 hover:to-sky-600 transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-sm"
                  >
                    <span v-if="isSavingResult">Đang xác nhận...</span>
                    <span v-else>Xác nhận</span>
                  </button>
                </div>
              </div>
              <div class="flex flex-wrap gap-3">
                <button
                  type="button"
                  @click="showFilePreviewModal = true"
                  :disabled="!scannedFilePreviewUrl"
                  class="px-4 py-2 rounded-lg border border-green-600 text-green-600 text-sm font-medium hover:bg-green-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Xem
                </button>
                <button
                  type="button"
                  @click="downloadScannedFile"
                  :disabled="!scannedFilePreviewUrl"
                  class="px-4 py-2 rounded-lg border border-blue-600 text-blue-600 text-sm font-medium hover:bg-blue-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Tải xuống
                </button>
                <button
                  type="button"
                  @click="$refs.resultFileInput.click()"
                  class="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  Chọn file mới
                </button>
              </div>
              <input
                ref="resultFileInput"
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff,.webp"
                @change="handleResultFileSelect"
                class="hidden"
              />
            </div>

            <!-- OCR Results Section - Full Width -->
            <div class="space-y-5">
              <!-- Header Information -->
              <div class="rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-sky-50 p-5 shadow-sm">
                <div class="flex items-center space-x-2 mb-4">
                  <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </div>
                  <h4 class="text-base font-bold text-gray-900">Thông tin OCR</h4>
                </div>
                <div class="grid gap-4 md:grid-cols-4">
                  <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-2">Số hóa đơn</label>
                    <input
                      v-model="resultForm.invoice_number"
                      type="text"
                      class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-sm font-medium"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-2">Ký hiệu</label>
                    <input
                      v-model="resultForm.invoice_symbol"
                      type="text"
                      class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-sm font-medium"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-2">Ngày</label>
                    <input
                      v-model="resultForm.invoice_date"
                      type="date"
                      class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-sm font-medium"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-2">Mã tài liệu</label>
                    <input
                      v-model="resultForm.document_code"
                      type="text"
                      class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-sm font-medium"
                    />
                  </div>
                </div>
              </div>

              <!-- Detail Information -->
              <div v-if="hasResult" class="space-y-5">
                <!-- Seller & Buyer -->
                <div class="grid gap-5 md:grid-cols-2">
                  <!-- Seller -->
                  <div
                    class="rounded-xl border border-gray-200 bg-white shadow-sm"
                    :class="{ 'border-yellow-400 bg-yellow-50/30': isSellerMissing }"
                  >
                    <div
                      class="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-orange-50 to-amber-50"
                    >
                      <div class="flex items-center space-x-2">
                        <div class="w-7 h-7 rounded-lg bg-orange-500 flex items-center justify-center">
                          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                            />
                          </svg>
                        </div>
                        <p class="text-sm font-bold text-gray-900 uppercase tracking-wide">Người bán</p>
                      </div>
                      <button
                        v-if="isSellerMissing"
                        type="button"
                        @click="showCreateSupplierModal = true"
                        class="text-xs text-blue-600 hover:text-blue-700 font-semibold underline"
                      >
                        + Tạo mới
                      </button>
                    </div>
                    <div class="p-4 space-y-3">
                      <div
                        v-if="isSellerMissing"
                        class="bg-yellow-100 border border-yellow-400 rounded-lg p-2.5 flex items-start space-x-2"
                      >
                        <svg
                          class="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <p class="text-xs text-yellow-800 font-medium">Thiếu thông tin nhà cung cấp</p>
                      </div>
                      <div>
                        <label class="block text-xs font-semibold text-gray-700 mb-2">Tên người bán</label>
                        <input
                          v-model="resultForm.seller.name"
                          placeholder="Nhập tên người bán"
                          :class="[
                            'w-full px-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm font-medium',
                            isSellerMissing && !resultForm.seller.name
                              ? 'border-yellow-400 bg-yellow-50'
                              : 'border-gray-300 bg-white',
                          ]"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-semibold text-gray-700 mb-2">Mã số thuế</label>
                        <input
                          v-model="resultForm.seller.tax_code"
                          placeholder="Nhập mã số thuế"
                          :class="[
                            'w-full px-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm font-medium',
                            isSellerMissing && !resultForm.seller.tax_code
                              ? 'border-yellow-400 bg-yellow-50'
                              : 'border-gray-300 bg-white',
                          ]"
                        />
                      </div>
                    </div>
                  </div>

                  <!-- Buyer -->
                  <div class="rounded-xl border border-gray-200 bg-white shadow-sm">
                    <div
                      class="flex items-center space-x-2 p-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50"
                    >
                      <div class="w-7 h-7 rounded-lg bg-green-500 flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                          />
                        </svg>
                      </div>
                      <p class="text-sm font-bold text-gray-900 uppercase tracking-wide">Người mua</p>
                    </div>
                    <div class="p-4 space-y-3">
                      <div>
                        <label class="block text-xs font-semibold text-gray-700 mb-2">Tên người mua</label>
                        <input
                          v-model="resultForm.buyer.name"
                          placeholder="Nhập tên người mua"
                          class="w-full px-3 py-2.5 border border-gray-300 bg-white rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm font-medium"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-semibold text-gray-700 mb-2">Mã số thuế</label>
                        <input
                          v-model="resultForm.buyer.tax_code"
                          placeholder="Nhập mã số thuế"
                          class="w-full px-3 py-2.5 border border-gray-300 bg-white rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm font-medium"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Items Details -->
                <div
                  class="rounded-xl border border-gray-200 bg-white shadow-sm"
                  :class="{ 'border-yellow-400 bg-yellow-50/30': isItemsMissing }"
                >
                  <div
                    class="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50"
                  >
                    <div class="flex items-center space-x-2">
                      <div class="w-7 h-7 rounded-lg bg-indigo-500 flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                          />
                        </svg>
                      </div>
                      <p class="text-sm font-bold text-gray-900 uppercase tracking-wide">Chi tiết hàng hóa</p>
                    </div>
                    <div class="flex items-center gap-2">
                      <button
                        v-if="isItemsMissing"
                        type="button"
                        @click="showCreateItemModal = true"
                        class="text-xs text-blue-600 hover:text-blue-700 font-semibold underline"
                      >
                        + Tạo mặt hàng
                      </button>
                      <button
                        type="button"
                        @click="addResultItem"
                        class="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition-colors"
                      >
                        + Thêm dòng
                      </button>
                    </div>
                  </div>
                  <div
                    v-if="isItemsMissing"
                    class="mx-4 mt-3 bg-yellow-100 border border-yellow-400 rounded-lg p-2.5 flex items-start space-x-2"
                  >
                    <svg class="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fill-rule="evenodd"
                        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <p class="text-xs text-yellow-800 font-medium">
                      Thiếu thông tin mặt hàng. Vui lòng thêm hoặc tạo mới.
                    </p>
                  </div>
                  <div class="p-4">
                    <div class="overflow-x-auto">
                      <div class="min-w-full">
                        <!-- Table Header -->
                        <div
                          class="grid grid-cols-12 gap-2 mb-2 pb-2 border-b-2 border-indigo-200 bg-indigo-50 rounded-lg px-3 py-2.5"
                        >
                          <div class="col-span-1 text-xs font-bold text-indigo-900">STT</div>
                          <div class="col-span-4 text-xs font-bold text-indigo-900">Mô tả</div>
                          <div class="col-span-1 text-xs font-bold text-indigo-900">Đơn vị</div>
                          <div class="col-span-2 text-xs font-bold text-indigo-900">Số lượng</div>
                          <div class="col-span-2 text-xs font-bold text-indigo-900">Đơn giá</div>
                          <div class="col-span-1 text-xs font-bold text-indigo-900">Thành tiền</div>
                          <div class="col-span-1 text-xs font-bold text-indigo-900"></div>
                        </div>
                        <!-- Table Body -->
                        <div class="space-y-2 max-h-96 overflow-y-auto">
                          <div
                            v-for="(item, index) in resultForm.items"
                            :key="index"
                            class="grid grid-cols-12 gap-2 px-3 py-2.5 rounded-lg bg-white border border-gray-200 hover:border-indigo-300 hover:shadow-sm transition-all"
                          >
                            <div class="col-span-1 flex items-center">
                              <input
                                v-model.number="item.stt"
                                type="number"
                                class="w-full px-2 py-2 border-0 bg-gray-50 rounded-lg text-sm text-center font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                              />
                            </div>
                            <div class="col-span-4">
                              <input
                                v-model="item.description"
                                placeholder="Nhập mô tả hàng hóa"
                                class="w-full px-3 py-2 border-0 bg-gray-50 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                              />
                            </div>
                            <div class="col-span-1">
                              <input
                                v-model="item.unit"
                                placeholder="ĐV"
                                class="w-full px-2 py-2 border-0 bg-gray-50 rounded-lg text-sm text-center font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                              />
                            </div>
                            <div class="col-span-2">
                              <input
                                v-model.number="item.quantity"
                                type="number"
                                step="0.01"
                                placeholder="0"
                                class="w-full px-3 py-2 border-0 bg-gray-50 rounded-lg text-sm text-right font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                              />
                            </div>
                            <div class="col-span-2">
                              <input
                                :value="formatCurrency(item.unit_price)"
                                @input="updateItemNumeric(item, 'unit_price', $event.target.value)"
                                placeholder="0"
                                class="w-full px-3 py-2 border-0 bg-gray-50 rounded-lg text-sm text-right font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                              />
                            </div>
                            <div class="col-span-1 flex items-center justify-end">
                              <span class="text-sm text-indigo-900 font-bold">{{ formatCurrency(item.amount) }}</span>
                            </div>
                            <div class="col-span-1 flex items-center justify-center">
                              <button
                                type="button"
                                @click="removeResultItem(index)"
                                class="w-7 h-7 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700 transition-colors font-bold flex items-center justify-center"
                                :disabled="resultForm.items.length === 1"
                              >
                                ×
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Financial Information -->
                <div class="rounded-xl border border-gray-200 bg-white shadow-sm">
                  <div
                    class="flex items-center space-x-2 p-4 border-b border-gray-200 bg-gradient-to-r from-teal-50 to-cyan-50"
                  >
                    <div class="w-7 h-7 rounded-lg bg-teal-500 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                    </div>
                    <p class="text-sm font-bold text-gray-900 uppercase tracking-wide">Thông tin tài chính</p>
                  </div>
                  <div class="p-4 space-y-4">
                    <div class="grid gap-4 md:grid-cols-3">
                      <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 p-3 rounded-lg border border-blue-200">
                        <label class="block text-xs font-semibold text-blue-700 mb-2">Tổng tiền</label>
                        <input
                          :value="formatCurrency(resultForm.financial.subtotal)"
                          @input="updateFinancial('subtotal', $event.target.value)"
                          placeholder="0"
                          class="w-full px-3 py-2.5 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-bold text-gray-900 bg-white"
                        />
                      </div>
                      <div
                        class="bg-gradient-to-br from-amber-50 to-amber-100/50 p-3 rounded-lg border border-amber-200"
                      >
                        <label class="block text-xs font-semibold text-amber-700 mb-2">VAT (%)</label>
                        <input
                          :value="formatCurrency(resultForm.financial.vat_rate)"
                          @input="updateFinancial('vat_rate', $event.target.value)"
                          placeholder="0"
                          class="w-full px-3 py-2.5 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm font-bold text-gray-900 bg-white"
                        />
                      </div>
                      <div
                        class="bg-gradient-to-br from-green-50 to-green-100/50 p-3 rounded-lg border-2 border-green-400"
                      >
                        <label class="block text-xs font-semibold text-green-700 mb-2">Tổng cộng</label>
                        <input
                          :value="formatCurrency(resultForm.financial.total_amount)"
                          @input="updateFinancial('total_amount', $event.target.value)"
                          placeholder="0"
                          class="w-full px-3 py-2.5 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm font-bold text-green-900 bg-white"
                        />
                      </div>
                    </div>
                    <div class="grid gap-4 md:grid-cols-2">
                      <div class="bg-gray-50 p-3 rounded-lg border border-gray-200">
                        <label class="block text-xs font-semibold text-gray-700 mb-2">Tiền thuế</label>
                        <input
                          :value="formatCurrency(resultForm.financial.vat_amount)"
                          @input="updateFinancial('vat_amount', $event.target.value)"
                          placeholder="0"
                          class="w-full px-3 py-2.5 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 text-sm font-medium text-gray-900 bg-white"
                        />
                      </div>
                      <div class="bg-gray-50 p-3 rounded-lg border border-gray-200">
                        <label class="block text-xs font-semibold text-gray-700 mb-2">Đơn vị tiền tệ</label>
                        <input
                          v-model="resultForm.financial.currency"
                          placeholder="VND"
                          class="w-full px-3 py-2.5 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 text-sm font-medium text-gray-900 bg-white"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="rounded-xl border-2 border-dashed border-gray-300 p-8 text-center bg-gray-50">
                <p class="text-sm text-gray-500">Chưa có kết quả OCR để hiển thị.</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Step 3: Kết quả & Dashboard -->
        <section v-if="currentStep === 3" class="space-y-6">
          <!-- Success Notification -->
          <div
            class="bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 rounded-2xl shadow-lg p-8 border-2 border-green-200"
          >
            <div class="text-center space-y-4">
              <div class="flex justify-center">
                <div class="relative">
                  <div
                    class="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-green-400 to-emerald-500 text-white text-3xl font-bold shadow-lg"
                  >
                    ✓
                  </div>
                  <div
                    class="absolute -top-1 -right-1 h-6 w-6 bg-green-500 rounded-full border-4 border-white animate-pulse"
                  ></div>
                </div>
              </div>
              <div>
                <p class="text-xs uppercase tracking-[3px] text-green-600 font-semibold mb-2">
                  Step 3 · Kết quả & Dashboard
                </p>
                <h3 class="text-3xl font-bold text-gray-900 mb-2">Xử lý thành công!</h3>
                <p class="text-sm text-gray-600 max-w-md mx-auto">
                  Chứng từ đã được OCR và lưu vào hệ thống thành công. Bạn có thể xem thống kê và tra cứu lịch sử xử lý
                  bên dưới.
                </p>
              </div>
              <div class="flex justify-center gap-3 pt-2">
                <button
                  @click="resetStepFlow"
                  class="px-6 py-3 rounded-xl bg-white border-2 border-green-500 text-green-600 text-sm font-semibold hover:bg-green-50 hover:shadow-md transition-all duration-200 flex items-center gap-2"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Xử lý chứng từ khác
                </button>
              </div>
            </div>

            <!-- File Info Card -->
            <div class="mt-6 grid gap-4 md:grid-cols-2">
              <div class="bg-white rounded-xl p-4 shadow-sm border border-green-100">
                <p class="text-xs uppercase tracking-wide text-gray-400 mb-2">File đã xử lý</p>
                <p class="text-lg font-semibold text-gray-900 truncate">{{ scannedFileInfo?.name || 'Không rõ' }}</p>
                <p class="text-sm text-green-600 font-medium mt-1">{{ finalResultStatus }}</p>
              </div>
              <div class="bg-white rounded-xl p-4 shadow-sm border border-green-100 space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Thời gian xử lý</span>
                  <span class="text-sm font-semibold text-gray-900">{{ finalResultTime }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Độ chính xác</span>
                  <span class="text-sm font-semibold text-gray-900">{{ finalResultAccuracy }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Dashboard Thống kê nhanh -->
          <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-200">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center space-x-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                <h3 class="text-lg font-bold text-gray-900">Thống kê nhanh</h3>
              </div>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div
                class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200 shadow-sm hover:shadow-md transition-shadow"
              >
                <p class="text-xs font-medium text-blue-600 mb-1">Hôm nay</p>
                <p class="text-2xl font-bold text-blue-700">{{ stats.today }}</p>
                <p class="text-xs text-blue-500 mt-1">chứng từ</p>
              </div>
              <div
                class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200 shadow-sm hover:shadow-md transition-shadow"
              >
                <p class="text-xs font-medium text-purple-600 mb-1">Tuần này</p>
                <p class="text-2xl font-bold text-purple-700">{{ stats.week }}</p>
                <p class="text-xs text-purple-500 mt-1">chứng từ</p>
              </div>
              <div
                class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border border-orange-200 shadow-sm hover:shadow-md transition-shadow"
              >
                <p class="text-xs font-medium text-orange-600 mb-1">Tháng này</p>
                <p class="text-2xl font-bold text-orange-700">{{ stats.month }}</p>
                <p class="text-xs text-orange-500 mt-1">chứng từ</p>
              </div>
              <div
                class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200 shadow-sm hover:shadow-md transition-shadow"
              >
                <p class="text-xs font-medium text-green-600 mb-1">Tổng cộng</p>
                <p class="text-2xl font-bold text-green-700">{{ stats.total }}</p>
                <p class="text-xs text-green-500 mt-1">chứng từ</p>
              </div>
            </div>
          </div>

          <!-- Tra cứu lịch sử xử lý -->
          <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-200">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center space-x-2">
                <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h3 class="text-lg font-bold text-gray-900">Tra cứu lịch sử xử lý</h3>
              </div>
            </div>

            <!-- Search and Filter -->
            <div class="mb-4 space-y-3">
              <div class="flex flex-col md:flex-row gap-3">
                <div class="flex-1 relative">
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Tìm kiếm theo tên file..."
                    class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    @input="handleSearchTransactions"
                  />
                  <svg
                    class="absolute left-3 top-2.5 w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
                <select
                  v-model="filterStatus"
                  @change="handleFilterTransactions"
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                >
                  <option value="">Tất cả trạng thái</option>
                  <option value="Processing">Đang xử lý</option>
                  <option value="Completed">Hoàn thành</option>
                  <option value="Error">Lỗi</option>
                  <option value="Cancelled">Đã hủy</option>
                </select>
              </div>
            </div>

            <!-- Transactions List -->
            <div class="space-y-2 max-h-96 overflow-y-auto">
              <div v-if="filteredHistoryTransactions.length === 0" class="text-center py-8 text-gray-500">
                <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p class="text-sm">Không tìm thấy lịch sử xử lý</p>
              </div>
              <div
                v-for="txn in filteredHistoryTransactions"
                :key="txn.name"
                class="bg-gray-50 rounded-lg p-3 border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
                @click="viewTransactionDetailModal(txn.name)"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3 flex-1 min-w-0">
                    <div class="flex-shrink-0">
                      <div
                        class="w-3 h-3 rounded-full"
                        :class="{
                          'bg-green-500': txn.status === 'Completed',
                          'bg-yellow-500': txn.status === 'Processing',
                          'bg-red-500': txn.status === 'Error',
                          'bg-gray-400': txn.status === 'Cancelled',
                        }"
                      ></div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ txn.file_name }}</p>
                      <p class="text-xs text-gray-500">
                        {{ getStatusLabel(txn.status) }} · {{ formatDate(txn.modified || txn.creation) }}
                      </p>
                    </div>
                  </div>
                  <button
                    @click.stop="viewTransactionDetailModal(txn.name)"
                    class="ml-3 px-3 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors flex-shrink-0"
                  >
                    Xem chi tiết
                  </button>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="filteredHistoryTransactions.length > 0" class="mt-4 flex items-center justify-between">
              <p class="text-sm text-gray-600">
                Hiển thị {{ Math.min((currentPage - 1) * pageSize + 1, filteredHistoryTransactions.length) }} -
                {{ Math.min(currentPage * pageSize, filteredHistoryTransactions.length) }}
                trong tổng số {{ filteredHistoryTransactions.length }} kết quả
              </p>
              <div class="flex gap-2">
                <button
                  @click="goToPrevPage"
                  :disabled="currentPage === 1"
                  class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Trước
                </button>
                <button
                  @click="goToNextPage"
                  :disabled="currentPage * pageSize >= filteredHistoryTransactions.length"
                  class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Sau
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
    <!-- Processing Overlay -->
    <div v-if="isProcessingOCR" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
        <div class="text-center space-y-6">
          <!-- Animated Processing Icon -->
          <div class="flex justify-center">
            <div class="relative">
              <div class="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <ScanTextIcon class="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>

          <!-- Processing Text -->
          <div class="space-y-2">
            <h3 class="text-xl font-bold text-gray-900">Đang xử lý OCR</h3>
            <p class="text-sm text-gray-600">Vui lòng đợi trong giây lát...</p>
          </div>

          <!-- Progress Bar -->
          <div class="space-y-2">
            <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div
                class="bg-gradient-to-r from-blue-500 to-blue-600 h-2.5 rounded-full transition-all duration-300"
                :style="{ width: `${processingProgress}%` }"
              ></div>
            </div>
            <p class="text-xs text-gray-500">{{ processingProgress }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- OCR Document Form Modal (for non-batch mode) -->
    <div
      v-if="showDocumentFormModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <div class="bg-white rounded-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between p-6 border-b">
          <h3 class="text-lg font-bold text-gray-900">Xác nhận tạo chứng từ</h3>
          <button @click="showDocumentFormModal = false" class="text-gray-400 hover:text-gray-600">
            <XIcon class="w-6 h-6" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="currentTransaction" class="space-y-6">
            <!-- Header Section -->
            <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h4 class="font-semibold text-gray-900 mb-4">Thông tin chứng từ</h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Ngày chứng từ</label>
                  <input
                    v-model="documentForm.posting_date"
                    type="date"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Loại chứng từ</label>
                  <input
                    :value="currentTransaction.document_type"
                    type="text"
                    disabled
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                  />
                </div>
              </div>
            </div>

            <!-- Details Section -->
            <div>
              <h4 class="font-semibold text-gray-900 mb-4">Chi tiết</h4>
              <div class="space-y-3">
                <div
                  v-for="(item, index) in documentForm.items"
                  :key="index"
                  class="bg-gray-50 rounded-lg p-4 border border-gray-200"
                >
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Tên trường</label>
                      <input
                        v-model="item.field_name"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Giá trị</label>
                      <input
                        v-model="item.field_value"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                  </div>
                  <button
                    @click="removeDocumentItem(index)"
                    class="mt-2 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                  >
                    Xóa
                  </button>
                </div>
                <button
                  @click="addDocumentItem"
                  class="w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors"
                >
                  + Thêm dòng
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end space-x-3">
          <button
            @click="showDocumentFormModal = false"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Hủy
          </button>
          <button
            @click="confirmCreateDocument"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Xác nhận tạo phiếu
          </button>
        </div>
      </div>
    </div>

    <!-- Transaction Detail Modal -->
    <div
      v-if="showTransactionDetailModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showTransactionDetailModal = false"
    >
      <div class="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div>
            <h3 class="text-xl font-bold text-gray-900">Chi tiết chứng từ xử lý</h3>
            <p class="text-sm text-gray-600 mt-1" v-if="transactionDetail">{{ transactionDetail.file_name }}</p>
          </div>
          <button
            @click="showTransactionDetailModal = false"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XIcon class="w-6 h-6" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="transactionDetail" class="space-y-6">
            <!-- Thông tin cơ bản -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 class="font-semibold text-gray-900 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Thông tin cơ bản
              </h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Tên file</label>
                  <p class="text-sm font-medium text-gray-900">{{ transactionDetail.file_name }}</p>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Trạng thái</label>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="{
                      'bg-green-100 text-green-800': transactionDetail.status === 'Completed',
                      'bg-yellow-100 text-yellow-800': transactionDetail.status === 'Processing',
                      'bg-red-100 text-red-800': transactionDetail.status === 'Error',
                      'bg-gray-100 text-gray-800': transactionDetail.status === 'Cancelled',
                    }"
                  >
                    {{ getStatusLabel(transactionDetail.status) }}
                  </span>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Loại chứng từ</label>
                  <p class="text-sm text-gray-900">{{ transactionDetail.document_type || 'N/A' }}</p>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Ngày tạo</label>
                  <p class="text-sm text-gray-900">{{ formatDate(transactionDetail.creation) }}</p>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Ngày cập nhật</label>
                  <p class="text-sm text-gray-900">{{ formatDate(transactionDetail.modified) }}</p>
                </div>
                <div v-if="transactionDetail.destination">
                  <label class="block text-xs font-medium text-gray-500 mb-1">Đích đến</label>
                  <p class="text-sm text-gray-900">{{ transactionDetail.destination }}</p>
                </div>
                <div v-if="transactionDetail.processing_time">
                  <label class="block text-xs font-medium text-gray-500 mb-1">Thời gian xử lý</label>
                  <p class="text-sm text-gray-900">{{ transactionDetail.processing_time }} giây</p>
                </div>
                <div v-if="transactionDetail.tokens_used">
                  <label class="block text-xs font-medium text-gray-500 mb-1">Tokens sử dụng</label>
                  <p class="text-sm text-gray-900">{{ transactionDetail.tokens_used }}</p>
                </div>
              </div>
            </div>

            <!-- Chi tiết OCR (details_info) -->
            <div v-if="transactionDetail.details_info" class="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h4 class="font-semibold text-gray-900 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Chi tiết OCR
              </h4>
              <div class="bg-white rounded-lg p-4 border border-blue-100 max-h-96 overflow-y-auto">
                <pre class="text-xs text-gray-700 whitespace-pre-wrap font-mono">{{
                  JSON.stringify(transactionDetail.details_info, null, 2)
                }}</pre>
              </div>
            </div>

            <!-- Mô tả -->
            <div v-if="transactionDetail.description" class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 class="font-semibold text-gray-900 mb-2">Mô tả</h4>
              <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ transactionDetail.description }}</p>
            </div>

            <!-- Thông tin bổ sung -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 class="font-semibold text-gray-900 mb-4">Thông tin bổ sung</h4>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div v-if="transactionDetail.company">
                  <label class="block text-xs font-medium text-gray-500 mb-1">Company</label>
                  <p class="text-gray-900">{{ transactionDetail.company }}</p>
                </div>
                <div v-if="transactionDetail.tenant">
                  <label class="block text-xs font-medium text-gray-500 mb-1">Tenant</label>
                  <p class="text-gray-900">{{ transactionDetail.tenant }}</p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <p class="text-gray-500">Đang tải chi tiết...</p>
          </div>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end">
          <button
            @click="showTransactionDetailModal = false"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>

    <!-- File Preview Modal -->
    <div
      v-if="showFilePreviewModal"
      class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
      @click.self="showFilePreviewModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[95vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b flex items-center justify-between bg-gray-50">
          <div>
            <h3 class="text-xl font-bold text-gray-900">Xem trước file</h3>
            <p class="text-sm text-gray-500 mt-1">{{ scannedFileInfo?.name || 'Không có tên file' }}</p>
          </div>
          <div class="flex items-center gap-3">
            <button
              @click="downloadScannedFile"
              :disabled="!scannedFilePreviewUrl"
              class="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed text-sm font-medium"
            >
              Tải xuống
            </button>
            <button @click="showFilePreviewModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <XIcon class="w-6 h-6" />
            </button>
          </div>
        </div>
        <div class="flex-1 overflow-auto p-6 bg-gray-100 flex items-center justify-center">
          <div v-if="scannedFilePreviewUrl" class="w-full h-full flex items-center justify-center">
            <img
              v-if="isImagePreview"
              :src="scannedFilePreviewUrl"
              alt="File Preview"
              class="max-w-full max-h-[75vh] object-contain rounded-lg shadow-lg bg-white p-2"
            />
            <iframe
              v-else-if="isPdfPreview"
              :src="scannedFilePreviewUrl"
              class="w-full h-[75vh] border-0 rounded-lg shadow-lg bg-white"
            />
            <div v-else class="p-8 text-center bg-white rounded-lg shadow-lg">
              <FileTextIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p class="text-sm text-gray-500">Xem trước chỉ khả dụng cho hình ảnh hoặc PDF.</p>
            </div>
          </div>
          <div v-else class="p-8 text-center bg-white rounded-lg shadow-lg">
            <FileTextIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p class="text-sm text-gray-500">Chưa có file để xem trước.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Supplier Modal -->
    <div
      v-if="showCreateSupplierModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showCreateSupplierModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b flex items-center justify-between bg-gray-50">
          <h3 class="text-xl font-bold text-gray-900">Tạo mới nhà cung cấp</h3>
          <button @click="showCreateSupplierModal = false" class="text-gray-400 hover:text-gray-600">
            <XIcon class="w-6 h-6" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Tên nhà cung cấp
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="newSupplierForm.supplier_name"
                type="text"
                placeholder="Nhập tên nhà cung cấp"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Mã số thuế
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="newSupplierForm.tax_id"
                type="text"
                placeholder="Nhập mã số thuế"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Loại nhà cung cấp</label>
              <select
                v-model="newSupplierForm.supplier_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Company">Công ty</option>
                <option value="Individual">Cá nhân</option>
              </select>
            </div>
          </div>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end space-x-3">
          <button
            @click="showCreateSupplierModal = false"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Hủy
          </button>
          <button
            @click="handleCreateSupplier"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Tạo mới
          </button>
        </div>
      </div>
    </div>

    <!-- Create Item Modal -->
    <div
      v-if="showCreateItemModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showCreateItemModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b flex items-center justify-between bg-gray-50">
          <h3 class="text-xl font-bold text-gray-900">Tạo mới mặt hàng</h3>
          <button @click="showCreateItemModal = false" class="text-gray-400 hover:text-gray-600">
            <XIcon class="w-6 h-6" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Mã mặt hàng</label>
              <input
                v-model="newItemForm.item_code"
                type="text"
                placeholder="Nhập mã mặt hàng (tự động nếu để trống)"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Tên mặt hàng
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="newItemForm.item_name"
                type="text"
                placeholder="Nhập tên mặt hàng"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Nhóm hàng</label>
              <input
                v-model="newItemForm.item_group"
                type="text"
                placeholder="Nhập nhóm hàng"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Đơn vị tính
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="newItemForm.stock_uom"
                type="text"
                placeholder="Cái, Kg, Lít..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end space-x-3">
          <button
            @click="showCreateItemModal = false"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Hủy
          </button>
          <button
            @click="handleCreateItem"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Tạo mới
          </button>
        </div>
      </div>
    </div>

    <!-- Camera Modal -->
    <div v-if="showCameraModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">Chụp ảnh tài liệu</h3>
          <button @click="closeCamera" class="text-gray-400 hover:text-gray-600">
            <XIcon class="w-6 h-6" />
          </button>
        </div>

        <div class="flex-1 p-6 flex flex-col items-center justify-center bg-gray-900 relative">
          <!-- Video Preview -->
          <video
            ref="videoElement"
            autoplay
            playsinline
            class="max-w-full max-h-[60vh] rounded-lg"
            :class="{ hidden: capturedImage }"
          ></video>

          <!-- Captured Image Preview -->
          <img v-if="capturedImage" :src="capturedImage" alt="Captured" class="max-w-full max-h-[60vh] rounded-lg" />

          <!-- Error Message -->
          <div v-if="cameraError" class="text-red-500 text-center mt-4">
            {{ cameraError }}
          </div>
        </div>

        <div class="p-6 border-t bg-gray-50 flex justify-center space-x-3">
          <button
            v-if="!capturedImage"
            @click="capturePhoto"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center space-x-2"
            :disabled="!streamActive"
          >
            <CameraIcon class="w-5 h-5" />
            <span>Chụp ảnh</span>
          </button>
          <button
            v-if="capturedImage"
            @click="retakePhoto"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Chụp lại
          </button>
          <button
            v-if="capturedImage"
            @click="useCapturedPhoto"
            class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            Sử dụng ảnh này
          </button>
          <button
            @click="closeCamera"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Hủy
          </button>
        </div>
      </div>
    </div>

    <!-- OCR Form Components -->
    <InvoiceForm
      v-if="showInvoiceFormModal && ocrResult && getDocumentType() === 'invoice_in'"
      :ocr-result="ocrResult"
      @close="showInvoiceFormModal = false"
      @saved="handleFormSaved"
    />
    <PurchaseReceiptForm
      v-if="showInvoiceFormModal && ocrResult && getDocumentType() === 'purchase_receipt'"
      :ocr-result="ocrResult"
      @close="showInvoiceFormModal = false"
      @saved="handleFormSaved"
    />
    <DeliveryNoteForm
      v-if="showInvoiceFormModal && ocrResult && getDocumentType() === 'delivery_note'"
      :ocr-result="ocrResult"
      @close="showInvoiceFormModal = false"
      @saved="handleFormSaved"
    />

    <!-- Validation Rules Modal -->
    <div
      v-if="showValidationRulesModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showValidationRulesModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between p-6 border-b bg-gradient-to-r from-purple-50 to-indigo-50">
          <div>
            <h3 class="text-2xl font-bold text-gray-900">📋 Quy tắc kiểm tra hóa đơn</h3>
            <p class="text-sm text-gray-600 mt-1">Hệ thống kiểm tra tự động 5 bước chuẩn</p>
          </div>
          <button @click="showValidationRulesModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          <!-- Rule 1: Check duplicate -->
          <div class="border-l-4 border-red-500 bg-red-50 p-4 rounded-r-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <span class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-red-100">
                  <span class="text-red-600 font-bold">1</span>
                </span>
              </div>
              <div class="ml-4 flex-1">
                <h4 class="text-lg font-semibold text-red-900 mb-2">✅ Check hóa đơn trùng lặp</h4>
                <div class="space-y-2 text-sm text-gray-700">
                  <p class="font-medium">Kiểm tra dựa trên bộ khóa (unique key):</p>
                  <div class="bg-white p-3 rounded border border-red-200">
                    <p class="font-semibold text-red-700 mb-1">Hóa đơn VAT (điện tử):</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>Mã số thuế người bán</li>
                      <li>Ký hiệu hóa đơn</li>
                      <li>Số hóa đơn</li>
                      <li>Ngày hóa đơn</li>
                      <li>Tổng tiền</li>
                    </ul>
                    <p class="mt-2 text-xs italic">
                      → Ghép thành: MST + KyHieu + SoHD + Ngay + TongTien → Tạo hash → So với DB
                    </p>
                  </div>
                  <div class="bg-white p-3 rounded border border-red-200">
                    <p class="font-semibold text-red-700 mb-1">Hóa đơn bán lẻ / siêu thị:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>Tên đơn vị bán, địa chỉ</li>
                      <li>Ngày giờ</li>
                      <li>Tổng tiền</li>
                      <li>Số POS / số giao dịch</li>
                    </ul>
                    <p class="mt-2 text-xs italic">→ Fuzzy match 95-98% để phát hiện trùng</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rule 2: Check MST -->
          <div class="border-l-4 border-blue-500 bg-blue-50 p-4 rounded-r-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <span class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-blue-100">
                  <span class="text-blue-600 font-bold">2</span>
                </span>
              </div>
              <div class="ml-4 flex-1">
                <h4 class="text-lg font-semibold text-blue-900 mb-2">✅ Check Mã số thuế hợp lệ</h4>
                <div class="space-y-2 text-sm text-gray-700">
                  <div class="bg-white p-3 rounded border border-blue-200">
                    <p class="font-semibold text-blue-700 mb-2">Quy tắc:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>
                        <strong>MST doanh nghiệp:</strong>
                        10 số
                      </li>
                      <li>
                        <strong>MST chi nhánh:</strong>
                        13 số (10 số + 3 số)
                      </li>
                      <li>Chỉ chứa ký tự số, không chữ</li>
                    </ul>
                  </div>
                  <div class="bg-white p-3 rounded border border-blue-200">
                    <p class="font-semibold text-blue-700 mb-2">Cách kiểm:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>
                        Regex:
                        <code class="bg-gray-100 px-2 py-1 rounded">^\d{{ 10 }}(\d{{ 3 }})?$</code>
                      </li>
                      <li>Thuật toán checksum MST (Bộ Tài Chính)</li>
                      <li>API Tổng cục Thuế: Kiểm tra trạng thái hoạt động</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rule 3: Check supplier -->
          <div class="border-l-4 border-green-500 bg-green-50 p-4 rounded-r-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <span class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-green-100">
                  <span class="text-green-600 font-bold">3</span>
                </span>
              </div>
              <div class="ml-4 flex-1">
                <h4 class="text-lg font-semibold text-green-900 mb-2">✅ Check thông tin nhà cung cấp</h4>
                <div class="space-y-2 text-sm text-gray-700">
                  <div class="bg-white p-3 rounded border border-green-200">
                    <p class="font-semibold text-green-700 mb-2">Các điểm cần kiểm tra:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>Tên pháp lý doanh nghiệp</li>
                      <li>Địa chỉ đăng ký</li>
                      <li>Tình trạng hoạt động</li>
                      <li>Ngành nghề kinh doanh</li>
                    </ul>
                  </div>
                  <div class="bg-white p-3 rounded border border-green-200">
                    <p class="font-semibold text-green-700 mb-2">Kỹ thuật matching:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>Fuzzy matching: Levenshtein / Cosine similarity</li>
                      <li>Chuẩn hóa text (remove dấu, lowercase, bỏ từ dư)</li>
                      <li>Tên + địa chỉ khớp ≥ 70-80%</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rule 4: Cross-check PO -->
          <div class="border-l-4 border-orange-500 bg-orange-50 p-4 rounded-r-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <span class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-orange-100">
                  <span class="text-orange-600 font-bold">4</span>
                </span>
              </div>
              <div class="ml-4 flex-1">
                <h4 class="text-lg font-semibold text-orange-900 mb-2">✅ Cross-check với PO (Purchase Order)</h4>
                <div class="space-y-2 text-sm text-gray-700">
                  <div class="bg-white p-3 rounded border border-orange-200">
                    <p class="font-semibold text-orange-700 mb-1">Tầng 1 — Thông tin chung:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>Nhà cung cấp trên PO = Nhà cung cấp trên HĐ</li>
                      <li>Ngày hóa đơn ≥ Ngày PO</li>
                      <li>MST khớp</li>
                    </ul>
                  </div>
                  <div class="bg-white p-3 rounded border border-orange-200">
                    <p class="font-semibold text-orange-700 mb-1">Tầng 2 — Dòng hàng:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>Tên hàng hóa (fuzzy match)</li>
                      <li>Số lượng HĐ ≤ Số lượng PO</li>
                      <li>Đơn giá ≈ Đơn giá PO (±1-2%)</li>
                    </ul>
                  </div>
                  <div class="bg-white p-3 rounded border border-orange-200">
                    <p class="font-semibold text-orange-700 mb-1">Tầng 3 — Giá trị:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>Tổng tiền hàng + VAT = Tổng thanh toán</li>
                      <li>So khớp với ngân sách PO/PR</li>
                    </ul>
                  </div>
                  <div class="bg-white p-3 rounded border border-orange-200">
                    <p class="font-semibold text-orange-700 mb-1">Tầng 4 — Cảnh báo nâng cao:</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>HĐ vượt giá PO</li>
                      <li>HĐ không thuộc PO nào</li>
                      <li>NCC không trong danh sách phê duyệt</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rule 5: Process flow -->
          <div class="border-l-4 border-purple-500 bg-purple-50 p-4 rounded-r-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <span class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-purple-100">
                  <span class="text-purple-600 font-bold">5</span>
                </span>
              </div>
              <div class="ml-4 flex-1">
                <h4 class="text-lg font-semibold text-purple-900 mb-2">✅ Quy trình xử lý chuẩn</h4>
                <div class="space-y-2 text-sm text-gray-700">
                  <div class="bg-white p-3 rounded border border-purple-200">
                    <ol class="list-decimal list-inside space-y-2 ml-2">
                      <li>
                        <strong>OCR</strong>
                        → Trích dữ liệu sạch
                      </li>
                      <li>
                        <strong>Chuẩn hóa</strong>
                        + Check MST
                      </li>
                      <li>
                        <strong>Lookup</strong>
                        nhà cung cấp
                      </li>
                      <li><strong>Check trùng</strong></li>
                      <li>
                        <strong>Match với PO</strong>
                        (từng field)
                      </li>
                    </ol>
                  </div>
                  <div class="bg-white p-3 rounded border border-purple-200">
                    <p class="font-semibold text-purple-700 mb-2">Kết quả:</p>
                    <div class="space-y-1">
                      <div class="flex items-center space-x-2">
                        <span class="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">PASS</span>
                        <span class="text-xs">Hóa đơn hợp lệ</span>
                      </div>
                      <div class="flex items-center space-x-2">
                        <span class="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-semibold">FAIL</span>
                        <span class="text-xs">Sai MST, không thuộc PO, vượt giá...</span>
                      </div>
                      <div class="flex items-center space-x-2">
                        <span class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs font-semibold">
                          NEED REVIEW
                        </span>
                        <span class="text-xs">Tên hàng lệch nhiều, số lượng vượt mức...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end">
          <button
            @click="showValidationRulesModal = false"
            class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>

    <!-- Validation Result Modal -->
    <div
      v-if="showValidationResultModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showValidationResultModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div
          class="flex items-center justify-between p-6 border-b"
          :class="[
            validationResults?.overall_status === 'PASS'
              ? 'bg-gradient-to-r from-green-50 to-emerald-50'
              : validationResults?.overall_status === 'FAIL'
              ? 'bg-gradient-to-r from-red-50 to-rose-50'
              : 'bg-gradient-to-r from-yellow-50 to-amber-50',
          ]"
        >
          <div class="flex items-center space-x-3">
            <div
              v-if="validationResults?.overall_status === 'PASS'"
              class="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center"
            >
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div
              v-else-if="validationResults?.overall_status === 'FAIL'"
              class="w-12 h-12 rounded-full bg-red-500 flex items-center justify-center"
            >
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div v-else class="w-12 h-12 rounded-full bg-yellow-500 flex items-center justify-center">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-900">Kết quả kiểm tra hóa đơn</h3>
              <p
                class="text-sm font-semibold mt-1"
                :class="[
                  validationResults?.overall_status === 'PASS'
                    ? 'text-green-700'
                    : validationResults?.overall_status === 'FAIL'
                    ? 'text-red-700'
                    : 'text-yellow-700',
                ]"
              >
                Trạng thái: {{ validationResults?.overall_status }}
              </p>
            </div>
          </div>
          <button
            @click="showValidationResultModal = false"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="validationResults?.checks" class="space-y-4">
            <div
              v-for="(check, index) in validationResults.checks"
              :key="index"
              class="border rounded-xl p-4 transition-all"
              :class="[
                check.status === 'PASS'
                  ? 'border-green-300 bg-green-50'
                  : check.status === 'FAIL'
                  ? 'border-red-300 bg-red-50'
                  : check.status === 'NEED REVIEW'
                  ? 'border-yellow-300 bg-yellow-50'
                  : 'border-gray-300 bg-gray-50',
              ]"
            >
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 mt-1">
                  <div
                    v-if="check.status === 'PASS'"
                    class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center"
                  >
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div
                    v-else-if="check.status === 'FAIL'"
                    class="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center"
                  >
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <div
                    v-else-if="check.status === 'NEED REVIEW'"
                    class="w-8 h-8 rounded-full bg-yellow-500 flex items-center justify-center"
                  >
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01" />
                    </svg>
                  </div>
                  <div v-else class="w-8 h-8 rounded-full bg-gray-400 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                </div>
                <div class="flex-1">
                  <h4 class="text-base font-bold text-gray-900 mb-1">
                    {{ check.name }}
                  </h4>
                  <p
                    class="text-sm font-medium mb-2"
                    :class="[
                      check.status === 'PASS'
                        ? 'text-green-700'
                        : check.status === 'FAIL'
                        ? 'text-red-700'
                        : check.status === 'NEED REVIEW'
                        ? 'text-yellow-700'
                        : 'text-gray-700',
                    ]"
                  >
                    {{ check.message }}
                  </p>

                  <!-- Details -->
                  <div v-if="check.details" class="mt-3 bg-white rounded-lg p-3 border border-gray-200">
                    <p class="text-xs font-semibold text-gray-600 mb-2">Chi tiết:</p>
                    <div class="space-y-1 text-xs text-gray-700">
                      <div v-for="(value, key) in check.details" :key="key" class="flex">
                        <span class="font-medium min-w-32">{{ formatDetailKey(key) }}:</span>
                        <span class="ml-2">{{ formatDetailValue(value) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">Không có kết quả kiểm tra</div>
        </div>

        <div class="p-6 border-t bg-gray-50 flex justify-end space-x-3">
          <button
            @click="showValidationResultModal = false"
            class="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors font-medium"
          >
            Đóng
          </button>
          <button
            v-if="validationResults?.overall_status === 'PASS' || validationResults?.overall_status === 'NEED REVIEW'"
            @click="
              showValidationResultModal = false;
              handleConfirmResult()
            "
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Tiếp tục xác nhận
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { call } from 'frappe-ui'
import InvoiceForm from '@/components/ocr/InvoiceForm.vue'
import PurchaseReceiptForm from '@/components/ocr/PurchaseReceiptForm.vue'
import DeliveryNoteForm from '@/components/ocr/DeliveryNoteForm.vue'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const { t } = useI18n()
import {
  ScanText as ScanTextIcon,
  Upload as UploadIcon,
  FileText as FileTextIcon,
  X as XIcon,
  Camera as CameraIcon,
} from 'lucide-vue-next'

const isDragging = ref(false)
const showDocumentFormModal = ref(false)
const showCameraModal = ref(false)
const showFilePreviewModal = ref(false)
const isProcessingOCR = ref(false)
const processingProgress = ref(0)
const showCreateSupplierModal = ref(false)
const showCreateItemModal = ref(false)
const newSupplierForm = ref({
  supplier_name: '',
  tax_id: '',
  supplier_type: 'Company',
})
const newItemForm = ref({
  item_code: '',
  item_name: '',
  item_group: '',
  stock_uom: 'Cái',
  is_stock_item: 1,
})
const currentTransaction = ref(null)
const showTransactionDetailModal = ref(false)
const transactionDetail = ref(null)
const transactions = ref([])
const recentTransactions = ref([])
const documentTypes = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const lastPageCount = ref(0)
const searchQuery = ref('')
const filterStatus = ref('')

// Camera state
const videoElement = ref(null)
const streamActive = ref(false)
const capturedImage = ref(null)
const cameraError = ref(null)
let mediaStream = null

const documentType = ref('INVOICE')
const batchMode = ref(false)
const showValidationRulesModal = ref(false)
const isValidating = ref(false)
const showValidationResultModal = ref(false)
const validationResults = ref(null)

const documentForm = ref({
  posting_date: new Date().toISOString().split('T')[0],
  items: [],
})

// OCR Result from n8n
const ocrResult = ref(null)
const showInvoiceFormModal = ref(false)

const resultForm = ref({
  invoice_number: '',
  invoice_symbol: '',
  invoice_date: '',
  document_code: '',
  seller: {
    name: '',
    tax_code: '',
    phone: '',
    address: '',
  },
  buyer: {
    name: '',
    company_name: '',
    tax_code: '',
    address: '',
  },
  items: [
    {
      stt: 1,
      description: '',
      unit: '',
      quantity: null,
      unit_price: null,
      amount: 0,
    },
  ],
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
const isSavingResult = ref(false)
const resultFileInput = ref(null)
const scannedFileInfo = computed(() => ocrResult.value?.scannedFile)
const scannedFilePreviewUrl = computed(() => {
  const file = scannedFileInfo.value
  if (!file?.base64) return null
  const mime = file.type || 'application/octet-stream'
  return `data:${mime};base64,${file.base64}`
})
const isImagePreview = computed(() => scannedFileInfo.value?.type?.startsWith('image/'))
const isPdfPreview = computed(() => scannedFileInfo.value?.type === 'application/pdf')
const hasResult = computed(() => !!ocrResult.value?.extracted_data)
const stepDefinitions = [
  { id: 1, label: 'Upload & Chọn loại', description: 'Chuẩn bị tài liệu đầu vào' },
  { id: 2, label: 'Xem trước & Xác nhận', description: 'Kiểm tra kết quả OCR' },
  { id: 3, label: 'Kết quả & Dashboard', description: 'Hoàn tất và xem kết quả' },
]
const currentStep = ref(1)
const step2Disabled = computed(() => !hasResult.value)
const finalResult = ref(null)
const finalResultStatus = computed(() => finalResult.value?.status || 'Đã xác nhận')
const finalResultTime = computed(() => finalResult.value?.processingTime || '-')
const finalResultAccuracy = computed(() =>
  finalResult.value?.accuracy ? `${finalResult.value.accuracy.toFixed(1)}%` : '-'
)

// Validation computed
const isSellerMissing = computed(() => {
  return !resultForm.value.seller?.name || !resultForm.value.seller?.tax_code
})

const isItemsMissing = computed(() => {
  return (
    !resultForm.value.items ||
    resultForm.value.items.length === 0 ||
    resultForm.value.items.every((item) => !item.description || !item.description.trim())
  )
})

const stats = ref({
  today: 0,
  week: 0,
  month: 0,
  total: 0,
})

const ocrSettings = ref({
  language: 'vie',
  quality: 'balanced',
  autoCorrect: true,
  preserveLayout: false,
})

const supportedFormats = ['PDF', 'JPG', 'JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP', 'GIF']

const pendingFiles = ref([])
const processingQueue = ref([])

watch(
  ocrResult,
  (newResult) => {
    const data = newResult?.extracted_data
    if (!data) {
      resultForm.value.items = [
        {
          stt: 1,
          description: '',
          unit: '',
          quantity: null,
          unit_price: null,
          amount: 0,
        },
      ]
      return
    }

    resultForm.value.invoice_number = data.invoice_number || ''
    resultForm.value.invoice_symbol = data.invoice_symbol || ''
    resultForm.value.document_code = data.document_code || data.request_id || ''

    if (data.invoice_date) {
      const dateStr = data.invoice_date
      if (/^\\d{4}-\\d{2}-\\d{2}$/.test(dateStr)) {
        resultForm.value.invoice_date = dateStr
      } else {
        const parsedDate = new Date(dateStr)
        resultForm.value.invoice_date = isNaN(parsedDate.getTime()) ? '' : parsedDate.toISOString().split('T')[0]
      }
    } else {
      resultForm.value.invoice_date = ''
    }

    if (data.seller) {
      resultForm.value.seller = {
        name: data.seller.name || '',
        tax_code: data.seller.tax_code || '',
        phone: data.seller.phone || '',
        address: data.seller.address || '',
      }
    }

    if (data.buyer) {
      resultForm.value.buyer = {
        name: data.buyer.name || '',
        company_name: data.buyer.company_name || '',
        tax_code: data.buyer.tax_code || '',
        address: data.buyer.address || '',
      }
    }

    resultForm.value.items =
      Array.isArray(data.items) && data.items.length > 0
        ? data.items.map((item, index) => ({
            stt: item.stt || index + 1,
            description: item.description || '',
            unit: item.unit || '',
            quantity: item.quantity || null,
            unit_price: item.unit_price || null,
            amount: item.amount || 0,
          }))
        : [
            {
              stt: 1,
              description: '',
              unit: '',
              quantity: null,
              unit_price: null,
              amount: 0,
            },
          ]

    if (data.financial) {
      resultForm.value.financial = {
        subtotal: data.financial.subtotal || 0,
        vat_rate: data.financial.vat_rate || 0,
        vat_amount: data.financial.vat_amount || 0,
        total_amount: data.financial.total_amount || 0,
        amount_in_words: data.financial.amount_in_words || '',
        currency: data.financial.currency || 'VND',
      }
    }

    if (data.payment_info) {
      resultForm.value.payment_info = {
        payment_method: data.payment_info.payment_method || '',
        payment_status: data.payment_info.payment_status || '',
      }
    }
  },
  { immediate: true }
)

watch(ocrResult, (value) => {
  currentStep.value = value?.extracted_data ? 2 : 1
})

watch(
  () => resultForm.value.items,
  (items) => {
    items.forEach((item) => {
      if (item.quantity != null && item.unit_price != null) {
        item.amount = item.quantity * item.unit_price
      }
    })
  },
  { deep: true }
)

watch(currentStep, (newStep) => {
  if (newStep === 3) {
    // Load all transactions for search/filter in step 3
    loadTransactions(1, true)
  }
})

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files)
  addPendingFiles(files)
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  addPendingFiles(files)
  if (e.target) {
    e.target.value = ''
  }
}

const addPendingFiles = (files) => {
  const list = batchMode.value ? files : files.slice(0, 1)

  list.forEach((file) => {
    pendingFiles.value.push({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: formatFileSize(file.size),
    })
  })
}

const confirmProcessing = () => {
  if (!pendingFiles.value.length) return

  // Set processing state
  isProcessingOCR.value = true
  processingProgress.value = 0

  pendingFiles.value.forEach((pf) => {
    const newItem = {
      id: Date.now() + Math.random(),
      name: pf.name,
      size: pf.size,
      status: 'processing',
      progress: 0,
    }

    processingQueue.value.push(newItem)
    handleFileOcr(pf.file, newItem)
  })

  pendingFiles.value = []
}

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return ''
  const number = Number(value)
  if (Number.isNaN(number)) return ''
  return number.toLocaleString('vi-VN')
}

const formatDetailKey = (key) => {
  const keyMap = {
    tax_id: 'Mã số thuế',
    type: 'Loại',
    checksum: 'Checksum',
    hash: 'Hash',
    duplicate_id: 'ID trùng',
    invoice_number: 'Số hóa đơn',
    invoice_date: 'Ngày hóa đơn',
    supplier_id: 'Mã NCC',
    supplier_name: 'Tên NCC',
    match_ratio: 'Độ khớp',
    matched_supplier: 'NCC khớp',
    matched_name: 'Tên khớp',
    invoice_name: 'Tên HĐ',
    system_name: 'Tên hệ thống',
    seller_name: 'Tên người bán',
    po_id: 'Mã PO',
    po_supplier: 'NCC trên PO',
    po_total: 'Tổng PO',
    po_reference: 'Tham chiếu PO',
    po_required: 'Yêu cầu PO',
    errors: 'Lỗi',
    warnings: 'Cảnh báo',
    length: 'Độ dài',
    status: 'Trạng thái',
  }
  return keyMap[key] || key
}

const formatDetailValue = (value) => {
  if (value === null || value === undefined) return 'N/A'
  if (typeof value === 'boolean') return value ? 'Có' : 'Không'
  if (typeof value === 'number' && value < 1 && value > 0) {
    return (value * 100).toFixed(0) + '%'
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
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
  if (item.quantity != null && item.unit_price != null) {
    item.amount = item.quantity * item.unit_price
  }
}

const updateFinancial = (field, value) => {
  const raw = parseCurrency(value)
  resultForm.value.financial[field] = raw
}

const addResultItem = () => {
  resultForm.value.items.push({
    stt: resultForm.value.items.length + 1,
    description: '',
    unit: '',
    quantity: null,
    unit_price: null,
    amount: 0,
  })
}

const removeResultItem = (index) => {
  if (resultForm.value.items.length === 1 && index === 0) {
    resultForm.value.items[0] = {
      stt: 1,
      description: '',
      unit: '',
      quantity: null,
      unit_price: null,
      amount: 0,
    }
    return
  }
  resultForm.value.items.splice(index, 1)
}

const handleResultFileSelect = (event) => {
  handleFileSelect(event)
  if (event.target) {
    event.target.value = ''
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

const openScannedFile = () => {
  const url = scannedFilePreviewUrl.value
  if (!url) return
  window.open(url, '_blank')
}

const downloadScannedFile = () => {
  const file = scannedFileInfo.value
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

// Handle invoice validation
const handleValidateInvoice = async () => {
  if (!hasResult.value) return

  try {
    isValidating.value = true

    // Prepare invoice data for validation
    const invoiceData = {
      invoice_number: resultForm.value.invoice_number,
      invoice_symbol: resultForm.value.invoice_symbol,
      invoice_date: resultForm.value.invoice_date,
      document_code: resultForm.value.document_code,
      po_reference: resultForm.value.document_code, // Assuming document_code might contain PO
      seller: {
        name: resultForm.value.seller.name,
        tax_code: resultForm.value.seller.tax_code,
      },
      buyer: {
        name: resultForm.value.buyer.name,
        tax_code: resultForm.value.buyer.tax_code,
      },
      items: resultForm.value.items.map((item) => ({
        stt: item.stt,
        description: item.description,
        unit: item.unit,
        quantity: item.quantity,
        unit_price: item.unit_price,
        amount: item.amount,
      })),
      financial: {
        subtotal: resultForm.value.financial.subtotal,
        vat_rate: resultForm.value.financial.vat_rate,
        vat_amount: resultForm.value.financial.vat_amount,
        total_amount: resultForm.value.financial.total_amount,
        currency: resultForm.value.financial.currency,
      },
    }

    // Call validation API
    const response = await call('dbiz_ai_agent.api.invoice_validation.validate_invoice_data', {
      invoice_data: JSON.stringify(invoiceData),
    })

    validationResults.value = response
    showValidationResultModal.value = true
  } catch (error) {
    console.error('Validation error:', error)
    notificationStore.notify('Có lỗi xảy ra khi kiểm tra hóa đơn: ' + (error.message || error), 'error')
  } finally {
    isValidating.value = false
  }
}

const handleConfirmResult = async () => {
  if (!hasResult.value) return

  // Validate before submit
  if (isSellerMissing.value) {
    if (!confirm('Thiếu thông tin nhà cung cấp. Bạn có muốn tạo mới nhà cung cấp không?')) {
      return
    }
    showCreateSupplierModal.value = true
    return
  }

  if (isItemsMissing.value) {
    if (!confirm('Thiếu thông tin mặt hàng. Bạn có muốn tạo mới mặt hàng không?')) {
      return
    }
    showCreateItemModal.value = true
    return
  }

  try {
    isSavingResult.value = true
    const response = await call('dbiz_ai_agent.api.ocr.create_ap_invoice_from_ocr', {
      invoice_data: resultForm.value,
      ocr_result: ocrResult.value,
      scanned_file: scannedFileInfo.value,
    })
    const result = response?.message || response
    if (result?.success) {
      notificationStore.notify('Xác nhận kết quả thành công.', 'success')
      finalResult.value = {
        filename: scannedFileInfo.value?.name || 'Unknown',
        processingTime: ocrResult.value?.processing_time || '-',
        accuracy: ocrResult.value?.confidence_scores?.overall || stats.value.accuracy,
        status: 'Đã xác nhận',
      }
      currentStep.value = 3
      await loadTransactions()
      await loadRecentTransactions()
      await loadStatistics()
    } else {
      notificationStore.notify(`Lỗi khi xác nhận: ${result?.error || result?.message || 'Không xác định'}`, 'error')
    }
  } catch (error) {
    console.error('Error confirming OCR result:', error)
    notificationStore.notify('Lỗi khi xác nhận kết quả: ' + (error.message || 'Vui lòng thử lại'), 'error')
  } finally {
    isSavingResult.value = false
  }
}

const handleCreateSupplier = async () => {
  if (!newSupplierForm.value.supplier_name || !newSupplierForm.value.tax_id) {
    notificationStore.notify('Vui lòng nhập đầy đủ thông tin nhà cung cấp', 'warning')
    return
  }

  try {
    const response = await call('dbiz_ai_agent.api.ocr.create_supplier', {
      supplier_name: newSupplierForm.value.supplier_name,
      tax_id: newSupplierForm.value.tax_id,
      supplier_type: newSupplierForm.value.supplier_type,
    })

    const result = response?.message || response
    if (result?.success) {
      // Cập nhật thông tin vào form
      resultForm.value.seller.name = newSupplierForm.value.supplier_name
      resultForm.value.seller.tax_code = newSupplierForm.value.tax_id

      // Reset form
      newSupplierForm.value = {
        supplier_name: '',
        tax_id: '',
        supplier_type: 'Company',
      }

      showCreateSupplierModal.value = false
      notificationStore.notify('Tạo nhà cung cấp thành công!', 'success')
    } else {
      notificationStore.notify(`Lỗi: ${result?.error || result?.message || 'Không thể tạo nhà cung cấp'}`, 'error')
    }
  } catch (error) {
    console.error('Error creating supplier:', error)
    notificationStore.notify('Lỗi khi tạo nhà cung cấp: ' + (error.message || 'Vui lòng thử lại'), 'error')
  }
}

const handleCreateItem = async () => {
  if (!newItemForm.value.item_name || !newItemForm.value.stock_uom) {
    notificationStore.notify('Vui lòng nhập đầy đủ thông tin mặt hàng', 'warning')
    return
  }

  try {
    const response = await call('dbiz_ai_agent.api.ocr.create_item', {
      item_code: newItemForm.value.item_code || undefined,
      item_name: newItemForm.value.item_name,
      item_group: newItemForm.value.item_group || undefined,
      stock_uom: newItemForm.value.stock_uom,
      is_stock_item: newItemForm.value.is_stock_item,
    })

    const result = response?.message || response
    if (result?.success) {
      // Thêm mặt hàng mới vào danh sách items
      const newItem = {
        stt: resultForm.value.items.length + 1,
        description: newItemForm.value.item_name,
        unit: newItemForm.value.stock_uom,
        quantity: null,
        unit_price: null,
        amount: 0,
      }
      resultForm.value.items.push(newItem)

      // Reset form
      newItemForm.value = {
        item_code: '',
        item_name: '',
        item_group: '',
        stock_uom: 'Cái',
        is_stock_item: 1,
      }

      showCreateItemModal.value = false
      notificationStore.notify('Tạo mặt hàng thành công!', 'success')
    } else {
      notificationStore.notify(`Lỗi: ${result?.error || result?.message || 'Không thể tạo mặt hàng'}`, 'error')
    }
  } catch (error) {
    console.error('Error creating item:', error)
    notificationStore.notify('Lỗi khi tạo mặt hàng: ' + (error.message || 'Vui lòng thử lại'), 'error')
  }
}

const resetStepFlow = () => {
  currentStep.value = 1
  ocrResult.value = null
  finalResult.value = null
  pendingFiles.value = []
  isProcessingOCR.value = false
  processingProgress.value = 0
}

const formatResultDataToText = (resultData) => {
  if (!resultData || typeof resultData !== 'object') {
    return ''
  }

  const source = resultData.data && typeof resultData.data === 'object' ? resultData.data : resultData

  const lines = []

  const isEmptyObject = (obj) => obj && typeof obj === 'object' && !Array.isArray(obj) && Object.keys(obj).length === 0

  const walk = (obj, prefix = '') => {
    if (!obj || typeof obj !== 'object') return

    Object.entries(obj).forEach(([key, value]) => {
      if (value === null || value === undefined) return

      if (typeof value === 'string') {
        const trimmed = value.trim()
        if (!trimmed) return
        lines.push(`${prefix}${key}: ${trimmed}`)
      } else if (typeof value === 'number' || typeof value === 'boolean') {
        lines.push(`${prefix}${key}: ${value}`)
      } else if (Array.isArray(value)) {
        if (value.length === 0) return
        const simpleVals = value.filter((v) => typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean')
        if (simpleVals.length === value.length) {
          lines.push(`${prefix}${key}: ${simpleVals.join(', ')}`)
        } else {
          lines.push(`${prefix}${key}:`)
          value.forEach((item) => {
            if (item && typeof item === 'object') {
              walk(item, `${prefix}  - `)
            } else if (item !== null && item !== undefined) {
              lines.push(`${prefix}  - ${item}`)
            }
          })
        }
      } else if (typeof value === 'object') {
        if (isEmptyObject(value)) return
        lines.push(`${prefix}${key}:`)
        walk(value, `${prefix}  `)
      }
    })
  }

  walk(source)

  return lines.join('\n')
}

// Convert file to base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64String = reader.result.split(',')[1] // Remove data:image/jpeg;base64, prefix
      console.log('File converted to base64, length:', base64String.length)
      resolve(base64String)
    }
    reader.onerror = (error) => {
      console.error('Error reading file:', error)
      reject(error)
    }
    reader.readAsDataURL(file)
  })
}

// Call n8n OCR API via backend to avoid CORS issues
const callN8nOCR = async (file, documentType) => {
  try {
    console.log('Starting OCR process for file:', file.name, 'type:', file.type, 'size:', file.size)

    // Convert file to base64
    const fileBase64 = await fileToBase64(file)

    if (!fileBase64 || fileBase64.length === 0) {
      throw new Error('Failed to convert file to base64')
    }

    // Generate request_id
    const requestId = `OCR-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // // Map document type
    // const docTypeMap = {
    //   'INVOICE': 'invoice_in',
    //   'invoice_in': 'invoice_in',
    //   'Hóa đơn đầu vào': 'invoice_in',
    //   'PURCHASE_RECEIPT': 'purchase_receipt',
    //   'purchase_receipt': 'purchase_receipt',
    //   'Phiếu nhập': 'purchase_receipt',
    //   'DELIVERY_NOTE': 'delivery_note',
    //   'delivery_note': 'delivery_note',
    //   'Phiếu xuất': 'delivery_note'
    // }
    const mappedDocType = documentType

    console.log('Calling n8n OCR API via backend:')
    console.log('- document_type:', mappedDocType)
    console.log('- request_id:', requestId)
    console.log('- file_base64 length:', fileBase64.length)

    // Check if file is too large (limit to 10MB base64 = ~7.5MB original)
    const maxBase64Size = 10 * 1024 * 1024 // 10MB
    if (fileBase64.length > maxBase64Size) {
      throw new Error(
        `File quá lớn (${(fileBase64.length / 1024 / 1024).toFixed(2)}MB). Vui lòng chọn file nhỏ hơn 7.5MB.`
      )
    }

    const content_type = file.type || 'application/octet-stream'

    const response = await call('dbiz_ai_agent.api.ocr.call_n8n_ocr_api', {
      file_base64: fileBase64,
      document_type: mappedDocType,
      request_id: requestId,
      file_name: file.name,
      file_mime_type: content_type,
    })

    console.log('Backend OCR API response:', response)

    // Handle frappe-ui response wrapping
    const result = response?.message || response

    if (!result || !result.success) {
      throw new Error(result?.error || result?.message || 'OCR processing failed')
    }

    // Get the actual OCR data
    const ocrData = result.data || result

    // Validate response structure
    if (!ocrData || typeof ocrData !== 'object') {
      throw new Error('Invalid response format from OCR API')
    }

    // Ensure success field exists
    if (ocrData.success === undefined) {
      // If no success field, assume success if extracted_data exists
      ocrData.success = !!ocrData.extracted_data
    }

    console.log('OCR API parsed response:', ocrData)

    ocrData.scanned_file = {
      name: file.name,
      type: file.type,
      size: file.size,
      base64: fileBase64,
    }
    return ocrData
  } catch (error) {
    console.error('Error calling n8n OCR API:', error)
    throw error
  }
}

// Format invoice result to text for display
const formatInvoiceResultToText = (ocrResponse) => {
  if (!ocrResponse || !ocrResponse.extracted_data) return 'Không có dữ liệu'

  const data = ocrResponse.extracted_data
  const lines = []

  lines.push('=== THÔNG TIN HÓA ĐƠN ===')
  lines.push(`Số hóa đơn: ${data.invoice_number || 'N/A'}`)
  lines.push(`Ký hiệu: ${data.invoice_symbol || 'N/A'}`)
  lines.push(`Ngày hóa đơn: ${data.invoice_date || 'N/A'}`)
  lines.push('')

  if (data.seller) {
    lines.push('=== NGƯỜI BÁN ===')
    lines.push(`Tên: ${data.seller.name || 'N/A'}`)
    lines.push(`Mã số thuế: ${data.seller.tax_code || 'N/A'}`)
    lines.push(`Địa chỉ: ${data.seller.address || 'N/A'}`)
    if (data.seller.phone) lines.push(`Điện thoại: ${data.seller.phone}`)
    if (data.seller.email) lines.push(`Email: ${data.seller.email}`)
    if (data.seller.bank_account) lines.push(`Tài khoản: ${data.seller.bank_account}`)
    if (data.seller.bank_name) lines.push(`Ngân hàng: ${data.seller.bank_name}`)
    lines.push('')
  }

  if (data.buyer) {
    lines.push('=== NGƯỜI MUA ===')
    lines.push(`Tên: ${data.buyer.name || 'N/A'}`)
    lines.push(`Mã số thuế: ${data.buyer.tax_code || 'N/A'}`)
    lines.push(`Địa chỉ: ${data.buyer.address || 'N/A'}`)
    if (data.buyer.phone) lines.push(`Điện thoại: ${data.buyer.phone}`)
    if (data.buyer.company_name) lines.push(`Tên công ty: ${data.buyer.company_name}`)
    lines.push('')
  }

  if (data.items && data.items.length > 0) {
    lines.push('=== CHI TIẾT HÀNG HÓA ===')
    data.items.forEach((item, index) => {
      lines.push(`${index + 1}. ${item.description || 'N/A'}`)
      if (item.unit) lines.push(`   Đơn vị: ${item.unit}`)
      if (item.quantity) lines.push(`   Số lượng: ${item.quantity}`)
      if (item.unit_price) lines.push(`   Đơn giá: ${item.unit_price.toLocaleString('vi-VN')}`)
      if (item.amount) lines.push(`   Thành tiền: ${item.amount.toLocaleString('vi-VN')}`)
    })
    lines.push('')
  }

  if (data.financial) {
    lines.push('=== THÔNG TIN TÀI CHÍNH ===')
    if (data.financial.subtotal) lines.push(`Tổng tiền: ${data.financial.subtotal.toLocaleString('vi-VN')}`)
    if (data.financial.vat_rate) lines.push(`Thuế VAT: ${data.financial.vat_rate}%`)
    if (data.financial.vat_amount) lines.push(`Tiền thuế: ${data.financial.vat_amount.toLocaleString('vi-VN')}`)
    if (data.financial.total_amount) lines.push(`Tổng cộng: ${data.financial.total_amount.toLocaleString('vi-VN')}`)
    if (data.financial.amount_in_words) lines.push(`Bằng chữ: ${data.financial.amount_in_words}`)
    if (data.financial.currency) lines.push(`Đơn vị tiền tệ: ${data.financial.currency}`)
    lines.push('')
  }

  if (data.payment_info) {
    lines.push('=== THÔNG TIN THANH TOÁN ===')
    if (data.payment_info.payment_method) lines.push(`Phương thức: ${data.payment_info.payment_method}`)
    if (data.payment_info.payment_status) lines.push(`Trạng thái: ${data.payment_info.payment_status}`)
  }

  return lines.join('\n')
}

const handleFileOcr = async (file, item) => {
  try {
    item.status = 'processing'
    item.progress = 10
    processingProgress.value = 10

    // Call n8n OCR API
    const ocrResponse = await callN8nOCR(file, documentType.value)

    item.progress = 50
    processingProgress.value = 50

    // Check if response is successful
    if (!ocrResponse || !ocrResponse.success) {
      const errorMsg = ocrResponse?.message || ocrResponse?.error || 'OCR processing failed'
      throw new Error(errorMsg)
    }

    // Validate extracted_data exists
    if (!ocrResponse.extracted_data) {
      throw new Error('OCR response missing extracted_data')
    }

    item.progress = 100
    processingProgress.value = 100
    item.status = 'completed'

    // Store OCR result (full response including metadata, confidence scores, etc.)
    const scannedFile = ocrResponse.scanned_file
    if (scannedFile) {
      delete ocrResponse.scanned_file
    }

    ocrResult.value = {
      ...ocrResponse,
      scannedFile: scannedFile
        ? {
            name: scannedFile.name,
            type: scannedFile.type,
            size: scannedFile.size,
            base64: scannedFile.base64,
          }
        : null,
    }
    currentStep.value = 2

    console.log('OCR result stored:', ocrResult.value)

    // Reload transactions
    await loadTransactions()
    await loadRecentTransactions()
    await loadStatistics()

    // Removed popup modal - information is already displayed below
    // If not batch mode, show appropriate form modal based on document type
    // if (!batchMode.value) {
    //   showInvoiceFormModal.value = true
    // }

    // Hide processing overlay after a short delay
    setTimeout(() => {
      isProcessingOCR.value = false
      processingProgress.value = 0
    }, 500)
  } catch (error) {
    console.error('OCR processing error:', error)
    item.status = 'error'
    item.error = error.message || 'Có lỗi xảy ra khi xử lý OCR'
    item.progress = 100

    // Hide processing overlay
    isProcessingOCR.value = false
    processingProgress.value = 0

    // Show error to user
    notificationStore.notify(`Lỗi xử lý OCR: ${error.message}`, 'error')
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Camera functions
const openCamera = async () => {
  try {
    showCameraModal.value = true
    cameraError.value = null
    capturedImage.value = null

    // Request camera access
    const constraints = {
      video: {
        facingMode: 'environment', // Use back camera if available
        width: { ideal: 1920 },
        height: { ideal: 1080 },
      },
    }

    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)

    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
      streamActive.value = true
    }
  } catch (error) {
    console.error('Error accessing camera:', error)
    cameraError.value = 'Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập camera của trình duyệt.'
    streamActive.value = false
  }
}

const capturePhoto = () => {
  if (!videoElement.value) return

  const canvas = document.createElement('canvas')
  canvas.width = videoElement.value.videoWidth
  canvas.height = videoElement.value.videoHeight

  const ctx = canvas.getContext('2d')
  ctx.drawImage(videoElement.value, 0, 0)

  capturedImage.value = canvas.toDataURL('image/jpeg', 0.9)

  // Stop video stream
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    streamActive.value = false
  }
}

const retakePhoto = async () => {
  capturedImage.value = null

  try {
    const constraints = {
      video: {
        facingMode: 'environment',
        width: { ideal: 1920 },
        height: { ideal: 1080 },
      },
    }

    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)

    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
      streamActive.value = true
    }
  } catch (error) {
    console.error('Error accessing camera:', error)
    cameraError.value = 'Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập camera của trình duyệt.'
  }
}

const useCapturedPhoto = () => {
  if (!capturedImage.value) return

  // Convert data URL to File
  fetch(capturedImage.value)
    .then((res) => res.blob())
    .then((blob) => {
      const file = new File([blob], `camera_${Date.now()}.jpg`, { type: 'image/jpeg' })
      addPendingFiles([file])
      closeCamera()
    })
    .catch((error) => {
      console.error('Error converting image:', error)
      cameraError.value = 'Lỗi khi xử lý ảnh. Vui lòng thử lại.'
    })
}

const closeCamera = () => {
  // Stop all tracks
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
  }

  if (videoElement.value) {
    videoElement.value.srcObject = null
  }

  showCameraModal.value = false
  streamActive.value = false
  capturedImage.value = null
  cameraError.value = null
}

// Get document type for component selection
const getDocumentType = () => {
  const docTypeMap = {
    INVOICE: 'invoice_in',
    invoice_in: 'invoice_in',
    'Hóa đơn đầu vào': 'invoice_in',
    PURCHASE_RECEIPT: 'purchase_receipt',
    purchase_receipt: 'purchase_receipt',
    'Phiếu nhập': 'purchase_receipt',
    DELIVERY_NOTE: 'delivery_note',
    delivery_note: 'delivery_note',
    'Phiếu xuất': 'delivery_note',
  }
  return docTypeMap[documentType.value] || 'invoice_in'
}

// Handle form saved event
const handleFormSaved = async (data) => {
  showInvoiceFormModal.value = false
  await loadTransactions()
  await loadRecentTransactions()
  await loadStatistics()
  // Show success message if needed
  if (data) {
    console.log('Form saved successfully:', data)
  }
}

const loadDocumentTypes = async () => {
  try {
    const response = await call('dbiz_ai_agent.api.ocr.get_document_types')
    // Handle frappe-ui response wrapping
    const result = response?.message || response

    if (result && result.success && result.data) {
      documentTypes.value = result.data
      console.log('Loaded document types:', documentTypes.value)
      // Update select options
      if (result.data.length > 0) {
        // Set default if current value is not in the list
        const currentExists = result.data.some((dt) => dt.document_type_code === documentType.value)
        if (!currentExists) {
          documentType.value = result.data[0].document_type_code
        }
      }
    } else {
      console.warn('No document types found or invalid response:', result)
      // Keep default options visible
    }
  } catch (error) {
    console.error('Failed to load document types:', error)
    // Keep default options visible on error
  }
}

const loadTransactions = async (page = currentPage.value, loadAll = false) => {
  try {
    const limit = loadAll ? 1000 : pageSize.value
    const response = await call('dbiz_ai_agent.api.ocr.get_transactions', {
      filters: {},
      limit: limit,
      start: loadAll ? 0 : (page - 1) * pageSize.value,
    })
    if (response.success && response.data) {
      transactions.value = response.data
      if (!loadAll) {
        currentPage.value = page
        lastPageCount.value = response.data.length
      }
    }
    // Also reload recent transactions and statistics
    await loadRecentTransactions()
    await loadStatistics()
  } catch (error) {
    console.error('Failed to load transactions:', error)
  }
}

const loadRecentTransactions = async () => {
  try {
    const response = await call('dbiz_ai_agent.api.ocr.get_recent_transactions', {
      limit: 3,
    })
    if (response.success && response.data) {
      recentTransactions.value = response.data
    }
  } catch (error) {
    console.error('Failed to load recent transactions:', error)
  }
}

const loadStatistics = async () => {
  try {
    const response = await call('dbiz_ai_agent.api.ocr.get_ocr_statistics')
    if (response.success && response.data) {
      stats.value = {
        today: response.data.today || 0,
        week: response.data.week || 0,
        month: response.data.month || 0,
        total: response.data.total || 0,
      }
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const filteredHistoryTransactions = computed(() => {
  let filtered = [...transactions.value]

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter((txn) => txn.file_name?.toLowerCase().includes(query))
  }

  // Filter by status
  if (filterStatus.value) {
    filtered = filtered.filter((txn) => txn.status === filterStatus.value)
  }

  return filtered
})

const handleSearchTransactions = () => {
  currentPage.value = 1
}

const handleFilterTransactions = () => {
  currentPage.value = 1
}

const goToPrevPage = () => {
  if (currentPage.value > 1) {
    loadTransactions(currentPage.value - 1)
  }
}

const goToNextPage = () => {
  if (lastPageCount.value === pageSize.value) {
    loadTransactions(currentPage.value + 1)
  }
}

const viewTransactionDetailModal = async (transactionId) => {
  try {
    const response = await call('dbiz_ai_agent.api.ocr.get_transaction_detail', {
      transaction_id: transactionId,
    })
    if (response.success && response.data) {
      transactionDetail.value = response.data
      showTransactionDetailModal.value = true
    } else {
      notificationStore.notify('Không thể tải chi tiết giao dịch', 'error')
    }
  } catch (error) {
    console.error('Failed to load transaction detail:', error)
    notificationStore.notify('Không thể tải chi tiết giao dịch', 'error')
  }
}

const viewTransactionDetail = async (transactionId, showForm = false) => {
  try {
    const response = await call('dbiz_ai_agent.api.ocr.get_transaction_detail', {
      transaction_id: transactionId,
    })
    if (response.success && response.data) {
      currentTransaction.value = response.data

      // Parse details_info to create form items
      if (response.data.details_info) {
        const details = response.data.details_info
        documentForm.value.items = []

        // Convert details_info object to form items
        const parseObject = (obj, prefix = '') => {
          Object.entries(obj).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
              if (typeof value === 'object' && !Array.isArray(value)) {
                parseObject(value, prefix ? `${prefix}.${key}` : key)
              } else {
                documentForm.value.items.push({
                  field_name: prefix ? `${prefix}.${key}` : key,
                  field_value: Array.isArray(value) ? JSON.stringify(value) : String(value),
                  field_type: Array.isArray(value) ? 'Text' : typeof value === 'number' ? 'Float' : 'Data',
                  sort_order: documentForm.value.items.length,
                })
              }
            }
          })
        }

        parseObject(details)
      }

      if (showForm) {
        showDocumentFormModal.value = true
      }
    }
  } catch (error) {
    console.error('Failed to load transaction detail:', error)
    notificationStore.notify('Không thể tải chi tiết giao dịch', 'error')
  }
}

const addDocumentItem = () => {
  documentForm.value.items.push({
    field_name: '',
    field_value: '',
    field_type: 'Data',
    sort_order: documentForm.value.items.length,
  })
}

const removeDocumentItem = (index) => {
  documentForm.value.items.splice(index, 1)
}

const confirmCreateDocument = async () => {
  if (!currentTransaction.value) return

  if (!documentForm.value.posting_date) {
    notificationStore.notify('Vui lòng nhập ngày chứng từ', 'warning')
    return
  }

  if (documentForm.value.items.length === 0) {
    notificationStore.notify('Vui lòng nhập ít nhất một dòng chi tiết', 'warning')
    return
  }

  try {
    const response = await call('dbiz_ai_agent.api.ocr.create_ocr_document', {
      transaction_id: currentTransaction.value.name,
      posting_date: documentForm.value.posting_date,
      items: documentForm.value.items,
    })

    if (response.success) {
      notificationStore.notify('Tạo chứng từ thành công!', 'success')
      showDocumentFormModal.value = false
      await loadTransactions()
      await loadRecentTransactions()
      await loadStatistics()
    } else {
      notificationStore.notify('Lỗi: ' + (response.error || 'Không thể tạo chứng từ'), 'error')
    }
  } catch (error) {
    console.error('Failed to create document:', error)
    notificationStore.notify('Lỗi khi tạo chứng từ: ' + error.message, 'error')
  }
}

const getStatusLabel = (status) => {
  const labels = {
    Processing: 'Đang xử lý',
    Completed: 'Hoàn thành',
    Error: 'Lỗi',
    Cancelled: 'Đã hủy',
  }
  return labels[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(async () => {
  await loadDocumentTypes()
  await loadTransactions()
  await loadRecentTransactions()
  await loadStatistics()
})
</script>

<style scoped>
.rotate-step {
  position: relative;
}

.rotate-step::after {
  content: '';
  position: absolute;
  inset: -6px;
  border-radius: 9999px;
  border: 2px solid rgba(14, 165, 233, 0.2);
  border-top-color: #0ea5e9;
  animation: spin-ring 1s ease-in-out infinite;
  pointer-events: none;
  z-index: -1;
}

@keyframes spin-ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
