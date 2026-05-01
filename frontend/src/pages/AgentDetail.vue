<template>
  <div class="w-full bg-gradient-to-br from-gray-50 via-blue-50/30 to-blue-50/20 min-h-full">
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="max-w-6xl mx-auto">
        <!-- Back Button -->
        <button
          @click="goBack"
          class="mb-6 flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          <span class="font-medium">Quay lại</span>
        </button>

        <!-- Loading State -->
        <div v-if="isLoading" class="text-center py-20">
          <div
            class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"
          ></div>
          <p class="mt-6 text-gray-600 text-lg">Đang tải thông tin AI Agent...</p>
        </div>

        <!-- Agent Detail Content -->
        <div v-else-if="agent" class="space-y-6">
          <!-- Header Card -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <div class="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
              <!-- Agent Icon -->
              <div
                class="w-24 h-24 rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0"
                :class="agent.iconBg || 'bg-blue-600'"
              >
                <component :is="agent.icon || Brain" :size="48" class="text-white" />
              </div>

              <!-- Agent Info -->
              <div class="flex-1">
                <div class="flex items-start justify-between mb-3">
                  <div class="flex-1">
                    <div class="flex items-center space-x-3 mb-2">
                      <h1 class="text-3xl font-bold text-gray-900">
                        {{ agent.name }}
                      </h1>
                      <span
                        v-if="agent.isNew"
                        class="px-3 py-1 rounded-full text-xs font-bold bg-orange-500 text-white"
                      >
                        NEW
                      </span>
                    </div>
                    <p class="text-lg text-gray-600 font-medium">{{ agent.nameEn }}</p>
                  </div>
                  <div class="flex items-center space-x-3 ml-4 flex-wrap">
                    <span
                      v-if="agent.status === 'deployed'"
                      class="px-3 py-1.5 rounded-full text-sm font-semibold bg-green-100 text-green-700 flex items-center space-x-2"
                    >
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fill-rule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      <span>Đã triển khai</span>
                    </span>
                    <span
                      v-else-if="agent.status === 'registered'"
                      class="px-3 py-1.5 rounded-full text-sm font-semibold bg-blue-100 text-blue-700 flex items-center space-x-2"
                    >
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fill-rule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      <span>Đã đăng ký</span>
                    </span>

                    <!-- Download Document Button -->
                    <button
                      @click="showDownloadModal = true"
                      class="px-6 py-2.5 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2 whitespace-nowrap"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                        />
                      </svg>
                      <span>Download tài liệu</span>
                    </button>

                    <button
                      v-if="agent.status !== 'deployed'"
                      @click="showRegistrationModal = true"
                      class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2 whitespace-nowrap"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <span>Sử dụng dịch vụ</span>
                    </button>

                    <!-- Access URL Button -->
                    <button
                      v-if="agent && agent.url && agent.url.trim()"
                      @click="openAgentUrl"
                      class="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-purple-800 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2 whitespace-nowrap"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                        />
                      </svg>
                      <span>Truy cập</span>
                    </button>
                  </div>
                </div>

                <p class="text-gray-600 text-base leading-relaxed mb-4">
                  {{ agent.description }}
                </p>

                <!-- Agent Metadata -->
                <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                  <span class="flex items-center space-x-1.5">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"
                      />
                    </svg>
                    <span class="font-medium text-gray-700">Agent Code:</span>
                    <span>{{ agent.agent_code || 'N/A' }}</span>
                  </span>
                  <span class="flex items-center space-x-1.5">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fill-rule="evenodd"
                        d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <span class="font-medium text-gray-700">Nguồn:</span>
                    <span>{{ agent.source || 'N/A' }}</span>
                  </span>
                  <span class="flex items-center space-x-1.5">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fill-rule="evenodd"
                        d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <span class="font-medium text-gray-700">Module:</span>
                    <span>{{ agent.moduleName || 'N/A' }}</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Capabilities Section -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
              <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path
                  fill-rule="evenodd"
                  d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
                  clip-rule="evenodd"
                />
              </svg>
              <span>Khả năng</span>
            </h2>
            <div
              v-if="agent.capabilities && agent.capabilities.length > 0"
              class="grid grid-cols-1 md:grid-cols-2 gap-3"
            >
              <div
                v-for="(capability, index) in agent.capabilities"
                :key="index"
                class="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-100 hover:bg-blue-100 transition-colors"
              >
                <svg class="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clip-rule="evenodd"
                  />
                </svg>
                <span class="text-gray-700 font-medium">{{ capability }}</span>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <p>Chưa có thông tin về khả năng của AI Agent này.</p>
            </div>
          </div>

          <!-- Additional Details Section (if needed) -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Thông tin bổ sung</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Trạng thái</label>
                <p class="mt-1 text-lg font-medium text-gray-900">
                  <span
                    :class="{
                      'text-green-700': agent.status === 'deployed',
                      'text-blue-700': agent.status === 'registered' || agent.status === 'active',
                      'text-gray-700': agent.status === 'inactive',
                    }"
                  >
                    {{ getStatusLabel(agent.status) }}
                  </span>
                </p>
              </div>
              <div>
                <label class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Agent Code</label>
                <p class="mt-1 text-lg font-medium text-gray-900">{{ agent.agent_code || 'N/A' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else class="text-center py-20">
          <div
            class="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-red-100 to-red-200 flex items-center justify-center"
          >
            <svg class="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h3 class="text-2xl font-semibold text-gray-900 mb-2">Không tìm thấy AI Agent</h3>
          <p class="text-gray-600 text-lg mb-4">AI Agent bạn đang tìm không tồn tại hoặc đã bị xóa.</p>
          <button
            @click="goBack"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Quay lại
          </button>
        </div>
      </div>
    </div>

    <!-- Registration Modal -->
    <div
      v-if="showRegistrationModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showRegistrationModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div>
            <h3 class="text-xl font-bold text-gray-900">Đăng ký sử dụng dịch vụ</h3>
            <p class="text-sm text-gray-600 mt-1" v-if="agent">{{ agent.name }}</p>
          </div>
          <button @click="showRegistrationModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="submitRegistration" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Số điện thoại
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="registrationForm.phone"
                type="tel"
                placeholder="Nhập số điện thoại"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Email
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="registrationForm.email"
                type="email"
                placeholder="Nhập email"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Ngày đăng ký
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="registrationForm.registration_date"
                type="date"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Số lượng người dùng
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="registrationForm.user_count"
                type="number"
                min="1"
                placeholder="Nhập số lượng người dùng"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Diễn giải</label>
              <textarea
                v-model="registrationForm.description"
                rows="4"
                placeholder="Nhập diễn giải (nếu có)"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              ></textarea>
            </div>
          </form>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end space-x-3">
          <button
            @click="showRegistrationModal = false"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors font-medium"
          >
            Hủy
          </button>
          <button
            @click="submitRegistration"
            :disabled="isSubmitting"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <span v-if="!isSubmitting">Xác nhận đăng ký</span>
            <span v-else class="flex items-center space-x-2">
              <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Đang xử lý...</span>
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div
      v-if="showSuccessModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showSuccessModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        <div class="text-center">
          <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
            <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Đăng ký thành công!</h3>
          <p class="text-gray-600 mb-6">Chúng tôi sẽ liên hệ lại với bạn sớm nhất.</p>
          <button
            @click="closeSuccessModal"
            class="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>

    <!-- Download Document Modal -->
    <div
      v-if="showDownloadModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showDownloadModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between p-6 border-b bg-gradient-to-r from-green-50 to-emerald-50">
          <div>
            <h3 class="text-xl font-bold text-gray-900">Download tài liệu</h3>
            <p class="text-sm text-gray-600 mt-1" v-if="agent">{{ agent.name }}</p>
          </div>
          <button @click="showDownloadModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="submitDownload" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Họ tên
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="downloadForm.full_name"
                type="text"
                placeholder="Nhập họ và tên"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Số điện thoại
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="downloadForm.phone"
                type="tel"
                placeholder="Nhập số điện thoại"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Email
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="downloadForm.email"
                type="email"
                placeholder="Nhập email"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Mục đích download tài liệu
                <span class="text-red-500">*</span>
              </label>
              <select
                v-model="downloadForm.purpose"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">-- Chọn mục đích --</option>
                <option value="research">Nghiên cứu</option>
                <option value="evaluation">Đánh giá dịch vụ</option>
                <option value="implementation">Triển khai</option>
                <option value="training">Đào tạo</option>
                <option value="reference">Tham khảo</option>
                <option value="other">Khác</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Diễn giải</label>
              <textarea
                v-model="downloadForm.description"
                rows="4"
                placeholder="Nhập thông tin chi tiết về mục đích sử dụng tài liệu (nếu có)"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              ></textarea>
            </div>
          </form>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end space-x-3">
          <button
            @click="showDownloadModal = false"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors font-medium"
          >
            Hủy
          </button>
          <button
            @click="submitDownload"
            :disabled="isDownloading"
            class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <span v-if="!isDownloading">Xác nhận và Download</span>
            <span v-else class="flex items-center space-x-2">
              <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Đang xử lý...</span>
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Download Success Modal -->
    <div
      v-if="showDownloadSuccessModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showDownloadSuccessModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        <div class="text-center">
          <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
            <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Đã ghi nhận thông tin!</h3>
          <p class="text-gray-600 mb-6">Tài liệu đã được gửi tới email của bạn. Vui lòng kiểm tra hộp thư.</p>
          <button
            @click="closeDownloadSuccessModal"
            class="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { call } from 'frappe-ui'
import {
  DollarSign,
  Truck,
  Factory,
  Users,
  Brain,
  FileText,
  Receipt,
  TrendingUp,
  CheckCircle,
  Calendar,
  Package,
  ShoppingCart,
  Briefcase,
  UserCheck,
  Calculator,
  ClipboardCheck,
  Layers,
  MessageSquare,
  Database,
  Building,
} from 'lucide-vue-next'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const route = useRoute()
const router = useRouter()

const isLoading = ref(true)
const agent = ref(null)
const showRegistrationModal = ref(false)
const showSuccessModal = ref(false)
const isSubmitting = ref(false)
const registrationForm = ref({
  phone: '',
  email: '',
  registration_date: new Date().toISOString().split('T')[0],
  user_count: 1,
  description: '',
})

// Download related states
const showDownloadModal = ref(false)
const showDownloadSuccessModal = ref(false)
const isDownloading = ref(false)
const downloadForm = ref({
  full_name: '',
  phone: '',
  email: '',
  purpose: '',
  description: '',
})

// Icon mapping (same as AIAgents.vue)
const iconMap = {
  DollarSign: DollarSign,
  Truck: Truck,
  Factory: Factory,
  Users: Users,
  Brain: Brain,
  FileText: FileText,
  Receipt: Receipt,
  TrendingUp: TrendingUp,
  CheckCircle: CheckCircle,
  Calendar: Calendar,
  Package: Package,
  ShoppingCart: ShoppingCart,
  Briefcase: Briefcase,
  UserCheck: UserCheck,
  Calculator: Calculator,
  ClipboardCheck: ClipboardCheck,
  Layers: Layers,
  MessageSquare: MessageSquare,
  Database: Database,
  Building: Building,
}

// Load agent detail
const loadAgentDetail = async () => {
  try {
    isLoading.value = true
    const agentId = route.params.id

    const response = await call('dbiz_ai_agent.api.ai_catalog.get_agent_detail', {
      agent_id: agentId,
    })

    if (response.success && response.data) {
      // Map icon
      const iconName = response.data.icon
      const iconComponent = iconMap[iconName] || Brain

      // Debug: log agent data to check URL
      console.log('Agent data from API:', response.data)
      console.log('Agent URL:', response.data.url)

      agent.value = {
        ...response.data,
        icon: iconComponent,
      }

      // Debug: log final agent object
      console.log('Final agent object:', agent.value)
      console.log('Agent URL in object:', agent.value.url)
    } else {
      agent.value = null
    }
  } catch (error) {
    console.error('Failed to load agent detail:', error)
    agent.value = null
  } finally {
    isLoading.value = false
  }
}

// Get status label
const getStatusLabel = (status) => {
  const labels = {
    active: 'Đang hoạt động',
    registered: 'Đã đăng ký',
    deployed: 'Đã triển khai',
    inactive: 'Không hoạt động',
  }
  return labels[status] || status
}

// Go back
const goBack = () => {
  router.push('/ai-agents')
}

// Submit registration
const submitRegistration = async () => {
  if (!agent.value) return

  try {
    isSubmitting.value = true

    const agentId = route.params.id

    const response = await call('dbiz_ai_agent.api.ai_catalog.register_agent_service', {
      agent_id: agentId,
      phone: registrationForm.value.phone,
      email: registrationForm.value.email,
      registration_date: registrationForm.value.registration_date,
      user_count: registrationForm.value.user_count,
      description: registrationForm.value.description || '',
    })

    if (response.success) {
      showRegistrationModal.value = false
      showSuccessModal.value = true
      // Reset form
      registrationForm.value = {
        phone: '',
        email: '',
        registration_date: new Date().toISOString().split('T')[0],
        user_count: 1,
        description: '',
      }
      // Reload agent detail to update status
      await loadAgentDetail()
    } else {
      notificationStore.notify(response.message || 'Có lỗi xảy ra khi đăng ký. Vui lòng thử lại.', 'error')
    }
  } catch (error) {
    console.error('Failed to submit registration:', error)
    notificationStore.notify('Có lỗi xảy ra khi đăng ký. Vui lòng thử lại.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Close success modal
const closeSuccessModal = () => {
  showSuccessModal.value = false
}

// Submit download request
const submitDownload = async () => {
  if (!agent.value) return

  try {
    isDownloading.value = true

    const agentId = route.params.id

    const response = await call('dbiz_ai_agent.api.ai_catalog.log_document_download', {
      agent_id: agentId,
      full_name: downloadForm.value.full_name,
      phone: downloadForm.value.phone,
      email: downloadForm.value.email,
      purpose: downloadForm.value.purpose,
      description: downloadForm.value.description || '',
    })

    if (response.success) {
      showDownloadModal.value = false
      showDownloadSuccessModal.value = true

      // Reset form
      downloadForm.value = {
        full_name: '',
        phone: '',
        email: '',
        purpose: '',
        description: '',
      }

      // Trigger download if document URL is provided
      if (response.document_url) {
        window.open(response.document_url, '_blank')
      }
    } else {
      notificationStore.notify(response.message || 'Có lỗi xảy ra. Vui lòng thử lại.', 'error')
    }
  } catch (error) {
    console.error('Failed to submit download request:', error)
    notificationStore.notify('Có lỗi xảy ra. Vui lòng thử lại.', 'error')
  } finally {
    isDownloading.value = false
  }
}

// Close download success modal
const closeDownloadSuccessModal = () => {
  showDownloadSuccessModal.value = false
}

// Open agent URL
const openAgentUrl = () => {
  if (agent.value && agent.value.url) {
    // Ensure URL has protocol
    let url = agent.value.url
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }
    window.open(url, '_blank')
  }
}

// Load on mount
onMounted(() => {
  loadAgentDetail()
})
</script>

<style scoped>
/* Add any custom styles if needed */
</style>
